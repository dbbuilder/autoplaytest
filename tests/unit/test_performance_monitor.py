"""Unit tests for PerformanceMonitor."""

import pytest
import pytest_asyncio
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.monitoring.performance.performance_monitor import (
    PerformanceMonitor, PerformanceMetric, WebVitals
)


@pytest.fixture
def mock_page():
    """Create a mock Playwright page."""
    page = AsyncMock()
    page.url = "https://example.com"
    page.evaluate = AsyncMock()
    return page


@pytest_asyncio.fixture
async def performance_monitor():
    """Create a PerformanceMonitor instance."""
    monitor = PerformanceMonitor()
    await monitor.initialize()
    yield monitor
    await monitor.shutdown()


@pytest.mark.asyncio
class TestPerformanceMonitor:
    """Test PerformanceMonitor functionality."""
    
    async def test_initialization(self):
        """Test monitor initialization."""
        monitor = PerformanceMonitor()
        
        assert monitor.metrics == []
        assert monitor.start_time is None
        assert not monitor.monitoring_active
        
        await monitor.initialize()
        
        assert monitor.start_time is not None
        assert monitor.monitoring_active
        assert monitor.metrics == []
    
    async def test_set_page(self, performance_monitor, mock_page):
        """Test setting the page instance."""
        assert performance_monitor.page is None
        
        performance_monitor.set_page(mock_page)
        
        assert performance_monitor.page == mock_page
    
    async def test_inject_performance_script(self, performance_monitor, mock_page):
        """Test performance script injection."""
        performance_monitor.set_page(mock_page)
        
        await performance_monitor._inject_performance_script()
        
        # Verify script was injected
        mock_page.evaluate.assert_called_once()
        call_args = mock_page.evaluate.call_args[0][0]
        assert "window.__performanceMonitor" in call_args
        assert "PerformanceObserver" in call_args
        assert "largest-contentful-paint" in call_args
    
    async def test_collect_metrics(self, performance_monitor, mock_page):
        """Test metric collection."""
        # Mock client metrics
        mock_page.evaluate.side_effect = [
            # First call - client metrics
            {
                'lcp': 2500.0,
                'fcp': 800.0,
                'cls': 0.05,
                'ttfb': 200.0
            },
            # Second call - resources
            [
                {'name': 'style.css', 'type': 'css', 'duration': 50, 'size': 1024},
                {'name': 'script.js', 'type': 'script', 'duration': 100, 'size': 2048}
            ],
            # Third call - memory
            {
                'usedJSHeapSize': 10485760,
                'totalJSHeapSize': 20971520,
                'jsHeapSizeLimit': 2147483648
            }
        ]
        
        performance_monitor.set_page(mock_page)
        
        metrics = await performance_monitor.collect_metrics()
        
        assert metrics['web_vitals']['lcp'] == 2500.0
        assert metrics['web_vitals']['fcp'] == 800.0
        assert len(metrics['resources']) == 2
        assert metrics['memory']['usedJSHeapSize'] == 10485760
        
        # Check that metrics were stored
        assert len(performance_monitor.metrics) > 0
    
    async def test_get_web_vitals(self, performance_monitor):
        """Test getting Core Web Vitals."""
        # Add some metrics
        timestamp = time.time()
        performance_monitor.metrics = [
            PerformanceMetric(
                name="lcp", value=2300, unit="ms", 
                timestamp=timestamp, category="web_vitals"
            ),
            PerformanceMetric(
                name="fid", value=50, unit="ms",
                timestamp=timestamp, category="web_vitals"
            ),
            PerformanceMetric(
                name="cls", value=0.08, unit="score",
                timestamp=timestamp, category="web_vitals"
            )
        ]
        
        vitals = await performance_monitor.get_web_vitals()
        
        assert vitals.lcp == 2300
        assert vitals.fid == 50
        assert vitals.cls == 0.08
    
    async def test_analyze_performance_good(self, performance_monitor):
        """Test performance analysis with good metrics."""
        # Add good metrics
        timestamp = time.time()
        performance_monitor.metrics = [
            PerformanceMetric(
                name="lcp", value=2000, unit="ms",
                timestamp=timestamp, category="web_vitals"
            ),
            PerformanceMetric(
                name="fid", value=80, unit="ms",
                timestamp=timestamp, category="web_vitals"
            ),
            PerformanceMetric(
                name="cls", value=0.05, unit="score",
                timestamp=timestamp, category="web_vitals"
            )
        ]
        
        analysis = performance_monitor.analyze_performance()
        
        assert analysis['status'] == 'good'
        assert analysis['scores']['lcp'] == 'good'
        assert analysis['scores']['fid'] == 'good'
        assert analysis['scores']['cls'] == 'good'
        assert len(analysis['issues']) == 0
    
    async def test_analyze_performance_poor(self, performance_monitor):
        """Test performance analysis with poor metrics."""
        # Add poor metrics
        timestamp = time.time()
        performance_monitor.metrics = [
            PerformanceMetric(
                name="lcp", value=5000, unit="ms",
                timestamp=timestamp, category="web_vitals"
            ),
            PerformanceMetric(
                name="fid", value=400, unit="ms",
                timestamp=timestamp, category="web_vitals"
            ),
            PerformanceMetric(
                name="cls", value=0.3, unit="score",
                timestamp=timestamp, category="web_vitals"
            ),
            PerformanceMetric(
                name="total_resources", value=150, unit="count",
                timestamp=timestamp, category="resources"
            ),
            PerformanceMetric(
                name="total_resource_size", value=10*1024*1024, unit="bytes",
                timestamp=timestamp, category="resources"
            )
        ]
        
        analysis = performance_monitor.analyze_performance()
        
        assert analysis['status'] == 'poor'
        assert analysis['scores']['lcp'] == 'poor'
        assert analysis['scores']['fid'] == 'poor'
        assert analysis['scores']['cls'] == 'poor'
        assert len(analysis['issues']) > 3
        assert any('LCP' in issue for issue in analysis['issues'])
        assert any('resources' in issue for issue in analysis['issues'])
        assert len(analysis['recommendations']) > 0
    
    async def test_metric_callbacks(self, performance_monitor):
        """Test metric callback functionality."""
        callback_called = False
        metric_received = None
        
        def callback(metric):
            nonlocal callback_called, metric_received
            callback_called = True
            metric_received = metric
        
        performance_monitor.register_metric_callback('test_metric', callback)
        
        # Add a metric
        metric = PerformanceMetric(
            name="test_metric", value=100, unit="ms",
            timestamp=time.time(), category="test"
        )
        performance_monitor._add_metric(metric)
        
        assert callback_called
        assert metric_received == metric
    
    async def test_get_metrics_by_category(self, performance_monitor):
        """Test getting metrics by category."""
        timestamp = time.time()
        performance_monitor.metrics = [
            PerformanceMetric(
                name="lcp", value=2000, unit="ms",
                timestamp=timestamp, category="web_vitals"
            ),
            PerformanceMetric(
                name="fcp", value=800, unit="ms",
                timestamp=timestamp, category="web_vitals"
            ),
            PerformanceMetric(
                name="total_resources", value=50, unit="count",
                timestamp=timestamp, category="resources"
            )
        ]
        
        web_vitals = performance_monitor.get_metrics_by_category("web_vitals")
        resources = performance_monitor.get_metrics_by_category("resources")
        
        assert len(web_vitals) == 2
        assert len(resources) == 1
        assert all(m.category == "web_vitals" for m in web_vitals)
        assert all(m.category == "resources" for m in resources)
    
    async def test_export_metrics(self, performance_monitor):
        """Test metric export."""
        timestamp = time.time()
        performance_monitor.metrics = [
            PerformanceMetric(
                name="test_metric", value=123, unit="ms",
                timestamp=timestamp, category="test",
                metadata={"extra": "data"}
            )
        ]
        
        exported = performance_monitor.export_metrics()
        
        assert len(exported) == 1
        assert exported[0]['name'] == 'test_metric'
        assert exported[0]['value'] == 123
        assert exported[0]['unit'] == 'ms'
        assert exported[0]['metadata']['extra'] == 'data'
    
    async def test_periodic_collection(self, performance_monitor, mock_page):
        """Test periodic metric collection."""
        mock_page.evaluate.return_value = {'lcp': 2000}
        performance_monitor.set_page(mock_page)
        
        # Start monitoring
        await performance_monitor.start_monitoring()
        
        # Wait a bit for collection
        await asyncio.sleep(0.1)
        
        # Stop monitoring
        await performance_monitor.stop_monitoring()
        
        # Should have called evaluate at least once
        assert mock_page.evaluate.call_count >= 1
    
    async def test_cleanup(self, performance_monitor, mock_page):
        """Test cleanup functionality."""
        mock_page.evaluate.return_value = None
        performance_monitor.set_page(mock_page)
        
        await performance_monitor.cleanup()
        
        # Should attempt to cleanup client-side script
        mock_page.evaluate.assert_called_with(
            "if (window.__performanceMonitor) { window.__performanceMonitor.cleanup(); }"
        )
    
    async def test_shutdown(self, performance_monitor):
        """Test monitor shutdown."""
        assert performance_monitor.monitoring_active
        
        await performance_monitor.shutdown()
        
        assert not performance_monitor.monitoring_active
    
    async def test_get_metrics_summary(self, performance_monitor):
        """Test getting metrics summary."""
        timestamp = time.time()
        performance_monitor.metrics = [
            PerformanceMetric(
                name="lcp", value=2000, unit="ms",
                timestamp=timestamp, category="web_vitals"
            ),
            PerformanceMetric(
                name="total_resources", value=50, unit="count",
                timestamp=timestamp, category="resources"
            )
        ]
        
        summary = performance_monitor.get_metrics_summary()
        
        assert summary['total_metrics'] == 2
        assert 'web_vitals' in summary['categories']
        assert 'resources' in summary['categories']
        assert len(summary['categories']['web_vitals']) == 1
        assert len(summary['categories']['resources']) == 1
        assert summary['duration'] > 0
    
    async def test_get_unit_for_metric(self, performance_monitor):
        """Test unit determination for metrics."""
        assert performance_monitor._get_unit_for_metric('lcp') == 'ms'
        assert performance_monitor._get_unit_for_metric('cls') == 'score'
        assert performance_monitor._get_unit_for_metric('unknown') == 'value'
    
    async def test_no_page_set(self, performance_monitor):
        """Test behavior when no page is set."""
        # Should not raise error, just return empty
        metrics = await performance_monitor.collect_metrics()
        assert metrics == {}
        
        # Start monitoring without page should log warning but not change state
        await performance_monitor.start_monitoring()
        # monitoring_active is set to True in start_monitoring before the page check
        assert performance_monitor.monitoring_active