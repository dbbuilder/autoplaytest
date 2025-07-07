"""Error Detector - Detects and categorizes errors during test execution."""

import logging
import traceback
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime
from dataclasses import dataclass, asdict
import re
import json
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories."""
    JAVASCRIPT = "javascript"
    NETWORK = "network"
    ASSERTION = "assertion"
    TIMEOUT = "timeout"
    ELEMENT_NOT_FOUND = "element_not_found"
    NAVIGATION = "navigation"
    PERMISSION = "permission"
    CONSOLE = "console"
    SECURITY = "security"
    UNKNOWN = "unknown"


@dataclass
class Error:
    """Represents a detected error."""
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    timestamp: datetime
    source: str
    stack_trace: Optional[str] = None
    url: Optional[str] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class ErrorDetector:
    """Detects and categorizes errors during test execution."""
    
    def __init__(self):
        self.logger = logger
        self.errors: List[Error] = []
        self.page = None
        self.error_patterns: Dict[ErrorCategory, List[re.Pattern]] = self._init_error_patterns()
        self._error_callbacks: Dict[ErrorCategory, List[Callable]] = {}
        self._console_handlers = []
        self._network_handlers = []
        self._js_error_handler = None
        self.ignored_patterns: Set[re.Pattern] = set()
    
    def _init_error_patterns(self) -> Dict[ErrorCategory, List[re.Pattern]]:
        """Initialize error detection patterns."""
        return {
            ErrorCategory.JAVASCRIPT: [
                re.compile(r"ReferenceError:", re.I),
                re.compile(r"TypeError:", re.I),
                re.compile(r"SyntaxError:", re.I),
                re.compile(r"RangeError:", re.I),
                re.compile(r"Cannot read property", re.I),
                re.compile(r"is not defined", re.I),
                re.compile(r"is not a function", re.I),
            ],
            ErrorCategory.NETWORK: [
                re.compile(r"Failed to fetch", re.I),
                re.compile(r"NetworkError", re.I),
                re.compile(r"ERR_.*_FAILED", re.I),
                re.compile(r"CORS", re.I),
                re.compile(r"404.*Not Found", re.I),
                re.compile(r"500.*Internal Server Error", re.I),
                re.compile(r"503.*Service Unavailable", re.I),
            ],
            ErrorCategory.TIMEOUT: [
                re.compile(r"TimeoutError", re.I),
                re.compile(r"Timeout.*exceeded", re.I),
                re.compile(r"Navigation timeout", re.I),
                re.compile(r"Waiting for.*timeout", re.I),
            ],
            ErrorCategory.ELEMENT_NOT_FOUND: [
                re.compile(r"Element.*not found", re.I),
                re.compile(r"Could not find.*element", re.I),
                re.compile(r"No element matching", re.I),
                re.compile(r"Unable to locate element", re.I),
            ],
            ErrorCategory.SECURITY: [
                re.compile(r"SecurityError", re.I),
                re.compile(r"Refused to.*security", re.I),
                re.compile(r"Content Security Policy", re.I),
                re.compile(r"Mixed Content", re.I),
            ],
            ErrorCategory.PERMISSION: [
                re.compile(r"Permission denied", re.I),
                re.compile(r"NotAllowedError", re.I),
                re.compile(r"User denied", re.I),
            ]
        }
    
    async def initialize(self) -> None:
        """Initialize the error detector."""
        self.errors.clear()
        self.logger.info("Error detector initialized")
    
    def set_page(self, page) -> None:
        """Set the Playwright page instance for monitoring."""
        self.page = page
        self._setup_page_listeners()
    
    def _setup_page_listeners(self) -> None:
        """Set up event listeners on the page."""
        if not self.page:
            return
        
        # Console message handler
        async def handle_console_message(msg):
            if msg.type() in ['error', 'warning']:
                error = Error(
                    message=msg.text(),
                    category=ErrorCategory.CONSOLE,
                    severity=ErrorSeverity.HIGH if msg.type() == 'error' else ErrorSeverity.MEDIUM,
                    timestamp=datetime.now(),
                    source="console",
                    url=self.page.url if self.page else None,
                    metadata={"type": msg.type()}
                )
                self._add_error(error)
        
        self._console_handlers.append(handle_console_message)
        self.page.on("console", handle_console_message)
        
        # Page error handler (uncaught exceptions)
        async def handle_page_error(error):
            js_error = Error(
                message=str(error),
                category=ErrorCategory.JAVASCRIPT,
                severity=ErrorSeverity.CRITICAL,
                timestamp=datetime.now(),
                source="page_error",
                stack_trace=error.stack if hasattr(error, 'stack') else None,
                url=self.page.url if self.page else None
            )
            self._add_error(js_error)
        
        self._js_error_handler = handle_page_error
        self.page.on("pageerror", handle_page_error)
        
        # Response handler for network errors
        async def handle_response(response):
            if response.status >= 400:
                error = Error(
                    message=f"HTTP {response.status} for {response.url}",
                    category=ErrorCategory.NETWORK,
                    severity=self._get_http_error_severity(response.status),
                    timestamp=datetime.now(),
                    source="network",
                    url=response.url,
                    metadata={
                        "status": response.status,
                        "status_text": response.status_text,
                        "method": response.request.method
                    }
                )
                self._add_error(error)
        
        self._network_handlers.append(handle_response)
        self.page.on("response", handle_response)
        
        # Request failed handler
        async def handle_request_failed(request):
            error = Error(
                message=f"Request failed: {request.url}",
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.HIGH,
                timestamp=datetime.now(),
                source="network",
                url=request.url,
                metadata={
                    "method": request.method,
                    "failure": request.failure
                }
            )
            self._add_error(error)
        
        self._network_handlers.append(handle_request_failed)
        self.page.on("requestfailed", handle_request_failed)
    
    def _get_http_error_severity(self, status_code: int) -> ErrorSeverity:
        """Determine severity based on HTTP status code."""
        if status_code >= 500:
            return ErrorSeverity.CRITICAL
        elif status_code >= 400:
            return ErrorSeverity.HIGH
        else:
            return ErrorSeverity.MEDIUM
    
    def detect_error(self, message: str, source: str = "unknown", **kwargs) -> Optional[Error]:
        """Detect and categorize an error from a message."""
        # Check if should be ignored
        for pattern in self.ignored_patterns:
            if pattern.search(message):
                return None
        
        # Categorize the error
        category = self._categorize_error(message)
        severity = kwargs.get('severity', self._determine_severity(category, message))
        
        error = Error(
            message=message,
            category=category,
            severity=severity,
            timestamp=datetime.now(),
            source=source,
            stack_trace=kwargs.get('stack_trace'),
            url=kwargs.get('url'),
            line_number=kwargs.get('line_number'),
            column_number=kwargs.get('column_number'),
            metadata=kwargs.get('metadata')
        )
        
        self._add_error(error)
        return error
    
    def _categorize_error(self, message: str) -> ErrorCategory:
        """Categorize an error based on its message."""
        for category, patterns in self.error_patterns.items():
            for pattern in patterns:
                if pattern.search(message):
                    return category
        return ErrorCategory.UNKNOWN
    
    def _determine_severity(self, category: ErrorCategory, message: str) -> ErrorSeverity:
        """Determine error severity based on category and message."""
        # Critical errors
        if category in [ErrorCategory.JAVASCRIPT, ErrorCategory.SECURITY]:
            return ErrorSeverity.CRITICAL
        
        # High severity
        if category in [ErrorCategory.NETWORK, ErrorCategory.TIMEOUT, ErrorCategory.ELEMENT_NOT_FOUND]:
            return ErrorSeverity.HIGH
        
        # Check for specific keywords
        critical_keywords = ["fatal", "critical", "crash", "panic"]
        high_keywords = ["error", "fail", "exception", "refused"]
        medium_keywords = ["warning", "deprecated", "slow"]
        
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in critical_keywords):
            return ErrorSeverity.CRITICAL
        elif any(keyword in message_lower for keyword in high_keywords):
            return ErrorSeverity.HIGH
        elif any(keyword in message_lower for keyword in medium_keywords):
            return ErrorSeverity.MEDIUM
        
        return ErrorSeverity.LOW
    
    def _add_error(self, error: Error) -> None:
        """Add an error and notify callbacks."""
        self.errors.append(error)
        self.logger.error(f"Detected {error.severity.value} {error.category.value} error: {error.message}")
        
        # Notify callbacks
        if error.category in self._error_callbacks:
            for callback in self._error_callbacks[error.category]:
                try:
                    callback(error)
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
    
    def register_error_callback(self, category: ErrorCategory, callback: Callable) -> None:
        """Register a callback for specific error categories."""
        if category not in self._error_callbacks:
            self._error_callbacks[category] = []
        self._error_callbacks[category].append(callback)
    
    def add_ignored_pattern(self, pattern: str) -> None:
        """Add a pattern to ignore certain errors."""
        self.ignored_patterns.add(re.compile(pattern, re.I))
    
    def get_errors_by_category(self, category: ErrorCategory) -> List[Error]:
        """Get all errors of a specific category."""
        return [e for e in self.errors if e.category == category]
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[Error]:
        """Get all errors of a specific severity."""
        return [e for e in self.errors if e.severity == severity]
    
    def get_critical_errors(self) -> List[Error]:
        """Get all critical errors."""
        return self.get_errors_by_severity(ErrorSeverity.CRITICAL)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all detected errors."""
        summary = {
            "total_errors": len(self.errors),
            "by_category": {},
            "by_severity": {},
            "critical_errors": len(self.get_critical_errors()),
            "recent_errors": []
        }
        
        # Count by category
        for category in ErrorCategory:
            count = len(self.get_errors_by_category(category))
            if count > 0:
                summary["by_category"][category.value] = count
        
        # Count by severity
        for severity in ErrorSeverity:
            count = len(self.get_errors_by_severity(severity))
            if count > 0:
                summary["by_severity"][severity.value] = count
        
        # Recent errors (last 10)
        summary["recent_errors"] = [
            {
                "message": e.message,
                "category": e.category.value,
                "severity": e.severity.value,
                "timestamp": e.timestamp.isoformat(),
                "source": e.source
            }
            for e in self.errors[-10:]
        ]
        
        return summary
    
    def analyze_errors(self) -> Dict[str, Any]:
        """Analyze detected errors and provide insights."""
        analysis = {
            "status": "unknown",
            "issues": [],
            "patterns": [],
            "recommendations": []
        }
        
        if not self.errors:
            analysis["status"] = "good"
            return analysis
        
        # Check for critical errors
        critical_errors = self.get_critical_errors()
        if critical_errors:
            analysis["status"] = "critical"
            analysis["issues"].append(f"Found {len(critical_errors)} critical errors")
            for error in critical_errors[:3]:  # Show first 3
                analysis["issues"].append(f"- {error.category.value}: {error.message[:100]}")
        
        # Analyze patterns
        category_counts = {}
        for error in self.errors:
            category_counts[error.category] = category_counts.get(error.category, 0) + 1
        
        # Find most common error types
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        for category, count in sorted_categories[:3]:
            if count >= 3:
                analysis["patterns"].append(f"Frequent {category.value} errors ({count} occurrences)")
        
        # Provide recommendations
        if ErrorCategory.JAVASCRIPT in category_counts:
            analysis["recommendations"].append("Fix JavaScript errors to ensure proper functionality")
        
        if ErrorCategory.NETWORK in category_counts:
            network_errors = self.get_errors_by_category(ErrorCategory.NETWORK)
            status_codes = set()
            for error in network_errors:
                if error.metadata and 'status' in error.metadata:
                    status_codes.add(error.metadata['status'])
            
            if 404 in status_codes:
                analysis["recommendations"].append("Fix broken links and missing resources (404 errors)")
            if any(code >= 500 for code in status_codes):
                analysis["recommendations"].append("Server errors detected - check backend services")
        
        if ErrorCategory.TIMEOUT in category_counts:
            analysis["recommendations"].append("Optimize slow operations to prevent timeouts")
        
        if ErrorCategory.SECURITY in category_counts:
            analysis["recommendations"].append("Address security policy violations")
        
        # Overall status
        if critical_errors:
            analysis["status"] = "critical"
        elif len(self.errors) > 10:
            analysis["status"] = "poor"
        elif len(self.errors) > 5:
            analysis["status"] = "fair"
        else:
            analysis["status"] = "good"
        
        return analysis
    
    def export_errors(self) -> List[Dict[str, Any]]:
        """Export all errors as a list of dictionaries."""
        return [
            {
                "message": e.message,
                "category": e.category.value,
                "severity": e.severity.value,
                "timestamp": e.timestamp.isoformat(),
                "source": e.source,
                "stack_trace": e.stack_trace,
                "url": e.url,
                "line_number": e.line_number,
                "column_number": e.column_number,
                "metadata": e.metadata
            }
            for e in self.errors
        ]
    
    def clear_errors(self) -> None:
        """Clear all recorded errors."""
        self.errors.clear()
    
    async def cleanup(self) -> None:
        """Clean up event listeners."""
        if self.page:
            # Remove event listeners
            for handler in self._console_handlers:
                self.page.remove_listener("console", handler)
            
            if self._js_error_handler:
                self.page.remove_listener("pageerror", self._js_error_handler)
            
            for handler in self._network_handlers:
                self.page.remove_listener("response", handler)
                self.page.remove_listener("requestfailed", handler)
        
        self._console_handlers.clear()
        self._network_handlers.clear()
        self._js_error_handler = None
    
    async def shutdown(self) -> None:
        """Shutdown the error detector."""
        await self.cleanup()
        self.logger.info("Error detector shutdown complete")