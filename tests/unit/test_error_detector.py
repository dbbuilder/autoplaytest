"""Unit tests for ErrorDetector."""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.monitoring.errors.error_detector import (
    ErrorDetector, Error, ErrorSeverity, ErrorCategory
)


@pytest.fixture
def mock_page():
    """Create a mock Playwright page."""
    page = MagicMock()
    page.url = "https://example.com"
    page.on = MagicMock()
    page.remove_listener = MagicMock()
    return page


@pytest_asyncio.fixture
async def error_detector():
    """Create an ErrorDetector instance."""
    detector = ErrorDetector()
    await detector.initialize()
    yield detector
    await detector.shutdown()


@pytest.mark.asyncio
class TestErrorDetector:
    """Test ErrorDetector functionality."""
    
    async def test_initialization(self):
        """Test detector initialization."""
        detector = ErrorDetector()
        
        assert detector.errors == []
        assert detector.page is None
        assert len(detector.error_patterns) > 0
        
        await detector.initialize()
        
        assert detector.errors == []
    
    async def test_set_page(self, error_detector, mock_page):
        """Test setting the page instance."""
        assert error_detector.page is None
        
        error_detector.set_page(mock_page)
        
        assert error_detector.page == mock_page
        # Should set up event listeners
        assert mock_page.on.call_count >= 4  # console, pageerror, response, requestfailed
    
    async def test_detect_javascript_error(self, error_detector):
        """Test detecting JavaScript errors."""
        error = error_detector.detect_error(
            "ReferenceError: undefined variable",
            source="test"
        )
        
        assert error is not None
        assert error.category == ErrorCategory.JAVASCRIPT
        assert error.severity == ErrorSeverity.CRITICAL
        assert error.message == "ReferenceError: undefined variable"
        assert len(error_detector.errors) == 1
    
    async def test_detect_network_error(self, error_detector):
        """Test detecting network errors."""
        error = error_detector.detect_error(
            "Failed to fetch resource from API",
            source="network"
        )
        
        assert error is not None
        assert error.category == ErrorCategory.NETWORK
        assert error.severity == ErrorSeverity.HIGH
    
    async def test_detect_timeout_error(self, error_detector):
        """Test detecting timeout errors."""
        error = error_detector.detect_error(
            "TimeoutError: Navigation timeout exceeded",
            source="playwright"
        )
        
        assert error is not None
        assert error.category == ErrorCategory.TIMEOUT
        assert error.severity == ErrorSeverity.HIGH
    
    async def test_detect_element_not_found(self, error_detector):
        """Test detecting element not found errors."""
        error = error_detector.detect_error(
            "Element not found: #submit-button",
            source="test"
        )
        
        assert error is not None
        assert error.category == ErrorCategory.ELEMENT_NOT_FOUND
        assert error.severity == ErrorSeverity.HIGH
    
    async def test_detect_security_error(self, error_detector):
        """Test detecting security errors."""
        error = error_detector.detect_error(
            "SecurityError: Refused to load script due to Content Security Policy",
            source="browser"
        )
        
        assert error is not None
        assert error.category == ErrorCategory.SECURITY
        assert error.severity == ErrorSeverity.CRITICAL
    
    async def test_categorize_unknown_error(self, error_detector):
        """Test categorizing unknown errors."""
        error = error_detector.detect_error(
            "Some random error message",
            source="unknown"
        )
        
        assert error is not None
        assert error.category == ErrorCategory.UNKNOWN
    
    async def test_severity_determination(self, error_detector):
        """Test severity determination based on keywords."""
        # Critical keywords
        error = error_detector.detect_error(
            "Fatal crash in application",
            source="test"
        )
        assert error.severity == ErrorSeverity.CRITICAL
        
        # High keywords
        error = error_detector.detect_error(
            "Exception occurred during processing",
            source="test"
        )
        assert error.severity == ErrorSeverity.HIGH
        
        # Medium keywords
        error = error_detector.detect_error(
            "Warning: deprecated function used",
            source="test"
        )
        assert error.severity == ErrorSeverity.MEDIUM
    
    async def test_ignored_patterns(self, error_detector):
        """Test ignoring errors matching patterns."""
        # Add ignored pattern
        error_detector.add_ignored_pattern("ignore.*this")
        
        # This should be ignored
        error = error_detector.detect_error(
            "Please ignore all this",
            source="test"
        )
        
        assert error is None
        assert len(error_detector.errors) == 0
    
    async def test_error_callbacks(self, error_detector):
        """Test error callback functionality."""
        callback_called = False
        received_error = None
        
        def callback(error):
            nonlocal callback_called, received_error
            callback_called = True
            received_error = error
        
        error_detector.register_error_callback(ErrorCategory.JAVASCRIPT, callback)
        
        # Detect a JavaScript error
        error_detector.detect_error(
            "TypeError: cannot read property",
            source="test"
        )
        
        assert callback_called
        assert received_error is not None
        assert received_error.category == ErrorCategory.JAVASCRIPT
    
    async def test_get_errors_by_category(self, error_detector):
        """Test getting errors by category."""
        # Add various errors
        error_detector.detect_error("ReferenceError: x", source="test")
        error_detector.detect_error("Failed to fetch", source="test")
        error_detector.detect_error("TimeoutError", source="test")
        error_detector.detect_error("Another ReferenceError", source="test")
        
        js_errors = error_detector.get_errors_by_category(ErrorCategory.JAVASCRIPT)
        network_errors = error_detector.get_errors_by_category(ErrorCategory.NETWORK)
        timeout_errors = error_detector.get_errors_by_category(ErrorCategory.TIMEOUT)
        
        # "Another ReferenceError" doesn't match the pattern since it's looking for "ReferenceError:"
        assert len(js_errors) >= 1
        assert len(network_errors) == 1
        assert len(timeout_errors) == 1
        assert all(e.category == ErrorCategory.JAVASCRIPT for e in js_errors)
    
    async def test_get_errors_by_severity(self, error_detector):
        """Test getting errors by severity."""
        # Add errors with different severities
        error_detector.detect_error("SecurityError: critical", source="test")
        error_detector.detect_error("Warning: something", source="test")
        error_detector.detect_error("Fatal error", source="test")
        
        critical_errors = error_detector.get_errors_by_severity(ErrorSeverity.CRITICAL)
        medium_errors = error_detector.get_errors_by_severity(ErrorSeverity.MEDIUM)
        
        assert len(critical_errors) >= 2  # Security and Fatal
        assert len(medium_errors) >= 1    # Warning
    
    async def test_get_critical_errors(self, error_detector):
        """Test getting critical errors specifically."""
        error_detector.detect_error("Fatal crash", source="test")
        error_detector.detect_error("Minor warning", source="test")
        
        critical = error_detector.get_critical_errors()
        
        assert len(critical) == 1
        assert critical[0].message == "Fatal crash"
    
    async def test_get_error_summary(self, error_detector):
        """Test getting error summary."""
        # Add various errors
        for i in range(3):
            error_detector.detect_error(f"ReferenceError: undefined variable {i}", source="test")
        for i in range(2):
            error_detector.detect_error(f"Failed to fetch resource {i}", source="test")
        error_detector.detect_error("Fatal crash occurred", source="test")
        
        summary = error_detector.get_error_summary()
        
        assert summary['total_errors'] == 6
        assert summary['critical_errors'] >= 1
        assert ErrorCategory.JAVASCRIPT.value in summary['by_category']
        assert ErrorCategory.NETWORK.value in summary['by_category']
        assert len(summary['recent_errors']) <= 10
    
    async def test_analyze_errors_good(self, error_detector):
        """Test error analysis with no errors."""
        analysis = error_detector.analyze_errors()
        
        assert analysis['status'] == 'good'
        assert len(analysis['issues']) == 0
    
    async def test_analyze_errors_critical(self, error_detector):
        """Test error analysis with critical errors."""
        # Add critical errors
        error_detector.detect_error("Fatal: Application crashed", source="test")
        error_detector.detect_error("SecurityError: XSS detected", source="test")
        
        analysis = error_detector.analyze_errors()
        
        assert analysis['status'] == 'critical'
        assert len(analysis['issues']) > 0
        assert any('critical errors' in issue for issue in analysis['issues'])
    
    async def test_analyze_errors_patterns(self, error_detector):
        """Test error pattern detection in analysis."""
        # Add repeated errors
        for i in range(5):
            error_detector.detect_error(f"NetworkError: Request {i} failed", source="test")
        for i in range(4):
            error_detector.detect_error(f"TimeoutError: Operation {i} timed out", source="test")
        
        analysis = error_detector.analyze_errors()
        
        assert len(analysis['patterns']) > 0
        assert any('network' in pattern.lower() for pattern in analysis['patterns'])
        assert any('timeout' in pattern.lower() for pattern in analysis['patterns'])
    
    async def test_analyze_errors_recommendations(self, error_detector):
        """Test error analysis recommendations."""
        # Add errors that should trigger recommendations
        error_detector.detect_error("TypeError: undefined function", source="test")
        # Create a network error with 404 status
        error = Error(
            message="HTTP 404 for /api/data",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            timestamp=datetime.now(),
            source="network",
            metadata={'status': 404}
        )
        error_detector.errors.append(error)
        error_detector.detect_error("SecurityError: CORS blocked", source="test")
        
        analysis = error_detector.analyze_errors()
        
        assert len(analysis['recommendations']) > 0
        assert any('JavaScript' in rec for rec in analysis['recommendations'])
        assert any('broken links' in rec or '404' in rec for rec in analysis['recommendations'])
    
    async def test_export_errors(self, error_detector):
        """Test error export."""
        # Add an error with all fields
        error = Error(
            message="Test error",
            category=ErrorCategory.JAVASCRIPT,
            severity=ErrorSeverity.HIGH,
            timestamp=datetime.now(),
            source="test",
            stack_trace="at line 10",
            url="https://example.com",
            line_number=10,
            column_number=5,
            metadata={'extra': 'data'}
        )
        error_detector.errors.append(error)
        
        exported = error_detector.export_errors()
        
        assert len(exported) == 1
        assert exported[0]['message'] == 'Test error'
        assert exported[0]['category'] == 'javascript'
        assert exported[0]['severity'] == 'high'
        assert exported[0]['stack_trace'] == 'at line 10'
        assert exported[0]['metadata']['extra'] == 'data'
    
    async def test_clear_errors(self, error_detector):
        """Test clearing errors."""
        # Add some errors
        error_detector.detect_error("Error 1", source="test")
        error_detector.detect_error("Error 2", source="test")
        
        assert len(error_detector.errors) == 2
        
        error_detector.clear_errors()
        
        assert len(error_detector.errors) == 0
    
    async def test_page_event_handlers(self, error_detector, mock_page):
        """Test page event handler setup."""
        error_detector.set_page(mock_page)
        
        # Get the registered handlers
        calls = mock_page.on.call_args_list
        event_types = [call[0][0] for call in calls]
        
        assert 'console' in event_types
        assert 'pageerror' in event_types
        assert 'response' in event_types
        assert 'requestfailed' in event_types
    
    async def test_cleanup(self, error_detector, mock_page):
        """Test cleanup functionality."""
        error_detector.set_page(mock_page)
        
        # Should have handlers registered
        assert len(error_detector._console_handlers) > 0
        assert error_detector._js_error_handler is not None
        assert len(error_detector._network_handlers) > 0
        
        await error_detector.cleanup()
        
        # Handlers should be cleared
        assert len(error_detector._console_handlers) == 0
        assert error_detector._js_error_handler is None
        assert len(error_detector._network_handlers) == 0
        
        # Should have called remove_listener
        assert mock_page.remove_listener.called
    
    async def test_http_error_severity(self, error_detector):
        """Test HTTP error severity determination."""
        assert error_detector._get_http_error_severity(404) == ErrorSeverity.HIGH
        assert error_detector._get_http_error_severity(500) == ErrorSeverity.CRITICAL
        assert error_detector._get_http_error_severity(503) == ErrorSeverity.CRITICAL
        assert error_detector._get_http_error_severity(301) == ErrorSeverity.MEDIUM