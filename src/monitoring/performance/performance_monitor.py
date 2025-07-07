"""Performance Monitor - Tracks and analyzes performance metrics during test execution."""

import logging
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import asyncio
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Represents a performance metric."""
    name: str
    value: float
    unit: str
    timestamp: float
    category: str = "general"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class WebVitals:
    """Core Web Vitals metrics."""
    lcp: Optional[float] = None  # Largest Contentful Paint
    fid: Optional[float] = None  # First Input Delay
    cls: Optional[float] = None  # Cumulative Layout Shift
    fcp: Optional[float] = None  # First Contentful Paint
    ttfb: Optional[float] = None  # Time to First Byte
    tti: Optional[float] = None  # Time to Interactive


class PerformanceMonitor:
    """Monitors and tracks performance metrics during test execution."""
    
    def __init__(self):
        self.logger = logger
        self.metrics: List[PerformanceMetric] = []
        self.start_time: Optional[float] = None
        self.page = None
        self.monitoring_active = False
        self._metric_callbacks: Dict[str, List[Callable]] = {}
    
    async def initialize(self) -> None:
        """Initialize the performance monitor."""
        self.start_time = time.time()
        self.metrics.clear()
        self.monitoring_active = True
        self.logger.info("Performance monitor initialized")
    
    def set_page(self, page) -> None:
        """Set the Playwright page instance for monitoring."""
        self.page = page
    
    async def start_monitoring(self) -> None:
        """Start active performance monitoring."""
        if not self.page:
            self.logger.warning("No page set for monitoring")
            return
        
        self.monitoring_active = True
        
        # Inject performance monitoring script
        await self._inject_performance_script()
        
        # Start periodic metric collection
        asyncio.create_task(self._periodic_collection())
    
    async def stop_monitoring(self) -> None:
        """Stop active performance monitoring."""
        self.monitoring_active = False
    
    async def _inject_performance_script(self) -> None:
        """Inject client-side performance monitoring script."""
        try:
            await self.page.evaluate("""
                window.__performanceMonitor = {
                    metrics: {},
                    observers: [],
                    
                    init: function() {
                        // Observe Largest Contentful Paint
                        if ('PerformanceObserver' in window) {
                            const lcpObserver = new PerformanceObserver((list) => {
                                const entries = list.getEntries();
                                const lastEntry = entries[entries.length - 1];
                                this.metrics.lcp = lastEntry.renderTime || lastEntry.loadTime;
                            });
                            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
                            this.observers.push(lcpObserver);
                            
                            // Observe First Input Delay
                            const fidObserver = new PerformanceObserver((list) => {
                                const entries = list.getEntries();
                                if (entries.length > 0) {
                                    this.metrics.fid = entries[0].processingStart - entries[0].startTime;
                                }
                            });
                            fidObserver.observe({ entryTypes: ['first-input'] });
                            this.observers.push(fidObserver);
                            
                            // Observe Cumulative Layout Shift
                            let clsValue = 0;
                            const clsObserver = new PerformanceObserver((list) => {
                                for (const entry of list.getEntries()) {
                                    if (!entry.hadRecentInput) {
                                        clsValue += entry.value;
                                        this.metrics.cls = clsValue;
                                    }
                                }
                            });
                            clsObserver.observe({ entryTypes: ['layout-shift'] });
                            this.observers.push(clsObserver);
                        }
                        
                        // Get navigation timing metrics
                        if (window.performance && window.performance.timing) {
                            const timing = window.performance.timing;
                            this.metrics.ttfb = timing.responseStart - timing.fetchStart;
                            this.metrics.domContentLoaded = timing.domContentLoadedEventEnd - timing.navigationStart;
                            this.metrics.loadComplete = timing.loadEventEnd - timing.navigationStart;
                        }
                    },
                    
                    getMetrics: function() {
                        // Get paint timing
                        if (window.performance && window.performance.getEntriesByType) {
                            const paintEntries = window.performance.getEntriesByType('paint');
                            paintEntries.forEach(entry => {
                                if (entry.name === 'first-contentful-paint') {
                                    this.metrics.fcp = entry.startTime;
                                }
                            });
                        }
                        
                        // Calculate Time to Interactive (simplified)
                        if (this.metrics.domContentLoaded && this.metrics.fcp) {
                            this.metrics.tti = Math.max(this.metrics.domContentLoaded, this.metrics.fcp);
                        }
                        
                        return this.metrics;
                    },
                    
                    cleanup: function() {
                        this.observers.forEach(observer => observer.disconnect());
                        this.observers = [];
                    }
                };
                
                window.__performanceMonitor.init();
            """)
        except Exception as e:
            self.logger.error(f"Failed to inject performance script: {e}")
    
    async def _periodic_collection(self) -> None:
        """Periodically collect performance metrics."""
        while self.monitoring_active:
            try:
                await self.collect_metrics()
                await asyncio.sleep(1)  # Collect every second
            except Exception as e:
                self.logger.error(f"Error in periodic collection: {e}")
                if not self.monitoring_active:
                    break
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics from the page."""
        if not self.page:
            return {}
        
        try:
            # Get client-side metrics
            client_metrics = await self.page.evaluate("window.__performanceMonitor ? window.__performanceMonitor.getMetrics() : {}")
            
            # Get resource timing
            resources = await self.page.evaluate("""
                () => {
                    if (!window.performance || !window.performance.getEntriesByType) {
                        return [];
                    }
                    
                    const resources = window.performance.getEntriesByType('resource');
                    return resources.map(r => ({
                        name: r.name,
                        type: r.initiatorType,
                        duration: r.duration,
                        size: r.transferSize || 0
                    }));
                }
            """)
            
            # Get memory usage if available
            memory = await self.page.evaluate("""
                () => {
                    if (window.performance && window.performance.memory) {
                        return {
                            usedJSHeapSize: window.performance.memory.usedJSHeapSize,
                            totalJSHeapSize: window.performance.memory.totalJSHeapSize,
                            jsHeapSizeLimit: window.performance.memory.jsHeapSizeLimit
                        };
                    }
                    return null;
                }
            """)
            
            # Store metrics
            timestamp = time.time()
            
            if client_metrics:
                for metric_name, value in client_metrics.items():
                    if value is not None:
                        self._add_metric(
                            PerformanceMetric(
                                name=metric_name,
                                value=value,
                                unit=self._get_unit_for_metric(metric_name),
                                timestamp=timestamp,
                                category="web_vitals"
                            )
                        )
            
            # Analyze resources
            if resources:
                total_size = sum(r.get('size', 0) for r in resources)
                total_count = len(resources)
                
                self._add_metric(
                    PerformanceMetric(
                        name="total_resources",
                        value=total_count,
                        unit="count",
                        timestamp=timestamp,
                        category="resources"
                    )
                )
                
                self._add_metric(
                    PerformanceMetric(
                        name="total_resource_size",
                        value=total_size,
                        unit="bytes",
                        timestamp=timestamp,
                        category="resources"
                    )
                )
                
                # Resource breakdown by type
                resource_types = {}
                for resource in resources:
                    res_type = resource.get('type', 'unknown')
                    if res_type not in resource_types:
                        resource_types[res_type] = {'count': 0, 'size': 0, 'duration': 0}
                    resource_types[res_type]['count'] += 1
                    resource_types[res_type]['size'] += resource.get('size', 0)
                    resource_types[res_type]['duration'] += resource.get('duration', 0)
                
                for res_type, stats in resource_types.items():
                    self._add_metric(
                        PerformanceMetric(
                            name=f"{res_type}_count",
                            value=stats['count'],
                            unit="count",
                            timestamp=timestamp,
                            category="resources",
                            metadata={"type": res_type}
                        )
                    )
            
            # Memory metrics
            if memory:
                self._add_metric(
                    PerformanceMetric(
                        name="js_heap_used",
                        value=memory['usedJSHeapSize'],
                        unit="bytes",
                        timestamp=timestamp,
                        category="memory"
                    )
                )
                
                self._add_metric(
                    PerformanceMetric(
                        name="js_heap_total",
                        value=memory['totalJSHeapSize'],
                        unit="bytes",
                        timestamp=timestamp,
                        category="memory"
                    )
                )
            
            return {
                "web_vitals": client_metrics,
                "resources": resources,
                "memory": memory,
                "timestamp": timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
            return {}
    
    def _add_metric(self, metric: PerformanceMetric) -> None:
        """Add a metric and notify callbacks."""
        self.metrics.append(metric)
        
        # Notify callbacks
        if metric.name in self._metric_callbacks:
            for callback in self._metric_callbacks[metric.name]:
                try:
                    callback(metric)
                except Exception as e:
                    self.logger.error(f"Error in metric callback: {e}")
    
    def _get_unit_for_metric(self, metric_name: str) -> str:
        """Get the appropriate unit for a metric."""
        units = {
            'lcp': 'ms',
            'fcp': 'ms',
            'fid': 'ms',
            'cls': 'score',
            'ttfb': 'ms',
            'tti': 'ms',
            'domContentLoaded': 'ms',
            'loadComplete': 'ms'
        }
        return units.get(metric_name, 'value')
    
    def register_metric_callback(self, metric_name: str, callback: Callable) -> None:
        """Register a callback for when a specific metric is collected."""
        if metric_name not in self._metric_callbacks:
            self._metric_callbacks[metric_name] = []
        self._metric_callbacks[metric_name].append(callback)
    
    async def get_web_vitals(self) -> WebVitals:
        """Get the current Core Web Vitals."""
        vitals = WebVitals()
        
        # Get latest values for each vital
        for metric in reversed(self.metrics):
            if metric.category == "web_vitals":
                if metric.name == "lcp" and vitals.lcp is None:
                    vitals.lcp = metric.value
                elif metric.name == "fid" and vitals.fid is None:
                    vitals.fid = metric.value
                elif metric.name == "cls" and vitals.cls is None:
                    vitals.cls = metric.value
                elif metric.name == "fcp" and vitals.fcp is None:
                    vitals.fcp = metric.value
                elif metric.name == "ttfb" and vitals.ttfb is None:
                    vitals.ttfb = metric.value
                elif metric.name == "tti" and vitals.tti is None:
                    vitals.tti = metric.value
        
        return vitals
    
    def get_metrics_by_category(self, category: str) -> List[PerformanceMetric]:
        """Get all metrics for a specific category."""
        return [m for m in self.metrics if m.category == category]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected metrics."""
        # Get web vitals synchronously
        vitals = WebVitals()
        for metric in reversed(self.metrics):
            if metric.category == "web_vitals":
                if metric.name == "lcp" and vitals.lcp is None:
                    vitals.lcp = metric.value
                elif metric.name == "fid" and vitals.fid is None:
                    vitals.fid = metric.value
                elif metric.name == "cls" and vitals.cls is None:
                    vitals.cls = metric.value
                elif metric.name == "fcp" and vitals.fcp is None:
                    vitals.fcp = metric.value
                elif metric.name == "ttfb" and vitals.ttfb is None:
                    vitals.ttfb = metric.value
                elif metric.name == "tti" and vitals.tti is None:
                    vitals.tti = metric.value
        
        summary = {
            "total_metrics": len(self.metrics),
            "categories": {},
            "web_vitals": asdict(vitals),
            "duration": time.time() - self.start_time if self.start_time else 0
        }
        
        # Group by category
        for metric in self.metrics:
            if metric.category not in summary["categories"]:
                summary["categories"][metric.category] = []
            summary["categories"][metric.category].append({
                "name": metric.name,
                "value": metric.value,
                "unit": metric.unit,
                "timestamp": metric.timestamp
            })
        
        return summary
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze collected metrics and provide insights."""
        analysis = {
            "status": "unknown",
            "issues": [],
            "recommendations": [],
            "scores": {}
        }
        
        # Get web vitals synchronously
        vitals = WebVitals()
        for metric in reversed(self.metrics):
            if metric.category == "web_vitals":
                if metric.name == "lcp" and vitals.lcp is None:
                    vitals.lcp = metric.value
                elif metric.name == "fid" and vitals.fid is None:
                    vitals.fid = metric.value
                elif metric.name == "cls" and vitals.cls is None:
                    vitals.cls = metric.value
                elif metric.name == "fcp" and vitals.fcp is None:
                    vitals.fcp = metric.value
                elif metric.name == "ttfb" and vitals.ttfb is None:
                    vitals.ttfb = metric.value
                elif metric.name == "tti" and vitals.tti is None:
                    vitals.tti = metric.value
        
        # LCP Analysis (should be < 2.5s for good)
        if vitals.lcp is not None:
            if vitals.lcp <= 2500:
                analysis["scores"]["lcp"] = "good"
            elif vitals.lcp <= 4000:
                analysis["scores"]["lcp"] = "needs improvement"
                analysis["issues"].append(f"LCP is {vitals.lcp}ms (should be < 2500ms)")
            else:
                analysis["scores"]["lcp"] = "poor"
                analysis["issues"].append(f"LCP is {vitals.lcp}ms (critical: should be < 2500ms)")
        
        # FID Analysis (should be < 100ms for good)
        if vitals.fid is not None:
            if vitals.fid <= 100:
                analysis["scores"]["fid"] = "good"
            elif vitals.fid <= 300:
                analysis["scores"]["fid"] = "needs improvement"
                analysis["issues"].append(f"FID is {vitals.fid}ms (should be < 100ms)")
            else:
                analysis["scores"]["fid"] = "poor"
                analysis["issues"].append(f"FID is {vitals.fid}ms (critical: should be < 100ms)")
        
        # CLS Analysis (should be < 0.1 for good)
        if vitals.cls is not None:
            if vitals.cls <= 0.1:
                analysis["scores"]["cls"] = "good"
            elif vitals.cls <= 0.25:
                analysis["scores"]["cls"] = "needs improvement"
                analysis["issues"].append(f"CLS is {vitals.cls} (should be < 0.1)")
            else:
                analysis["scores"]["cls"] = "poor"
                analysis["issues"].append(f"CLS is {vitals.cls} (critical: should be < 0.1)")
        
        # Resource analysis
        resource_metrics = self.get_metrics_by_category("resources")
        if resource_metrics:
            latest_count = None
            latest_size = None
            
            for metric in reversed(resource_metrics):
                if metric.name == "total_resources" and latest_count is None:
                    latest_count = metric.value
                elif metric.name == "total_resource_size" and latest_size is None:
                    latest_size = metric.value
            
            if latest_count and latest_count > 100:
                analysis["issues"].append(f"High number of resources: {int(latest_count)}")
                analysis["recommendations"].append("Consider bundling resources to reduce HTTP requests")
            
            if latest_size and latest_size > 5 * 1024 * 1024:  # 5MB
                size_mb = latest_size / (1024 * 1024)
                analysis["issues"].append(f"Large total resource size: {size_mb:.1f}MB")
                analysis["recommendations"].append("Optimize images and use compression")
        
        # Overall status
        if not analysis["issues"]:
            analysis["status"] = "good"
        elif len(analysis["issues"]) <= 2:
            analysis["status"] = "fair"
        else:
            analysis["status"] = "poor"
        
        return analysis
    
    def export_metrics(self) -> List[Dict[str, Any]]:
        """Export all metrics as a list of dictionaries."""
        return [
            {
                "name": m.name,
                "value": m.value,
                "unit": m.unit,
                "timestamp": m.timestamp,
                "category": m.category,
                "metadata": m.metadata
            }
            for m in self.metrics
        ]
    
    async def cleanup(self) -> None:
        """Clean up monitoring resources."""
        if self.page:
            try:
                await self.page.evaluate("if (window.__performanceMonitor) { window.__performanceMonitor.cleanup(); }")
            except Exception:
                pass  # Page might be closed
    
    async def shutdown(self) -> None:
        """Shutdown the performance monitor."""
        self.monitoring_active = False
        await self.cleanup()
        self.logger.info("Performance monitor shutdown complete")