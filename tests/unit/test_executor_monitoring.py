"""
Unit tests for TestExecutor monitoring functionality
Following TDD approach - write tests first, then implementation
"""

import pytest
import pytest_asyncio
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import tempfile
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.executor.test_executor import TestExecutor
from core.engine.main_engine import TestConfiguration


class TestExecutorMonitoring:
    """Test the _execute_with_monitoring method and actual script execution"""
    
    @pytest_asyncio.fixture
    async def test_executor(self):
        """Create a TestExecutor instance for testing."""
        executor = TestExecutor()
        await executor.initialize()
        yield executor
        await executor.shutdown()
    
    @pytest.fixture
    def test_config(self):
        """Create a test configuration."""
        return TestConfiguration(
            url="https://example.com",
            username="testuser",
            password="testpass",
            headless=True,
            browser="chromium"
        )
    
    @pytest.fixture
    def sample_test_script(self):
        """Sample Playwright test script."""
        return '''
import asyncio
from playwright.async_api import async_playwright

async def test_example():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://example.com")
        title = await page.title()
        assert "Example" in title
        
        await browser.close()
        print("Test passed!")

if __name__ == "__main__":
    asyncio.run(test_example())
'''
    
    @pytest.mark.asyncio
    async def test_execute_with_monitoring_exists(self, test_executor):
        """Test that _execute_with_monitoring method exists."""
        assert hasattr(test_executor, '_execute_with_monitoring')
        assert callable(getattr(test_executor, '_execute_with_monitoring', None))
    
    @pytest.mark.asyncio
    async def test_execute_with_monitoring_basic(self, test_executor, test_config):
        """Test basic execution with monitoring."""
        # Prepare execution environment
        execution_env = {
            'enhanced_script_path': '/tmp/test_script.py',
            'temp_dir': '/tmp/test_dir',
            'screenshots_dir': '/tmp/test_dir/screenshots',
            'logs_dir': '/tmp/test_dir/logs'
        }
        
        execution_result = {
            'script_name': 'test_script.py',
            'errors': [],
            'performance_metrics': {},
            'screenshots': [],
            'console_logs': []
        }
        
        # This should not raise an exception
        await test_executor._execute_with_monitoring(
            execution_env, execution_result, test_config
        )
        
        # Check that execution was attempted
        assert 'status' not in execution_result or execution_result['status'] != 'failed'
    
    @pytest.mark.asyncio
    async def test_execute_with_monitoring_captures_metrics(self, test_executor, test_config):
        """Test that execution captures performance metrics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            script_path = temp_path / "test_script.py"
            
            # Write test script
            script_path.write_text('''
import time
print("Starting test")
time.sleep(0.1)
print("Test completed")
''')
            
            execution_env = {
                'enhanced_script_path': str(script_path),
                'temp_dir': str(temp_path),
                'screenshots_dir': str(temp_path / 'screenshots'),
                'logs_dir': str(temp_path / 'logs')
            }
            
            execution_result = {
                'script_name': 'test_script.py',
                'errors': [],
                'performance_metrics': {},
                'screenshots': [],
                'console_logs': []
            }
            
            await test_executor._execute_with_monitoring(
                execution_env, execution_result, test_config
            )
            
            # Should have performance metrics
            assert 'performance_metrics' in execution_result
            assert len(execution_result['performance_metrics']) > 0
    
    @pytest.mark.asyncio
    async def test_execute_script_file_runs_actual_test(self, test_executor, test_config, sample_test_script):
        """Test that execute_script_file actually runs the Playwright test."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            script_path = temp_path / "test_playwright.py"
            script_path.write_text(sample_test_script)
            
            # Execute the script
            result = await test_executor.execute_script_file(
                str(script_path),
                test_config,
                "test_session_123"
            )
            
            # Check execution results
            assert result['status'] in ['passed', 'failed']
            assert result['execution_duration'] > 0
            assert 'performance_metrics' in result
            
            # If using subprocess, there should be execution evidence
            if result['status'] == 'passed':
                assert len(result['errors']) == 0
    
    @pytest.mark.asyncio
    async def test_execute_with_subprocess(self, test_executor, test_config):
        """Test that scripts are executed using subprocess/pytest."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            script_path = temp_path / "test_subprocess.py"
            
            # Write a simple test that we know will pass
            script_path.write_text('''
def test_simple():
    assert 1 + 1 == 2
    print("Simple test passed")
''')
            
            execution_env = {
                'enhanced_script_path': str(script_path),
                'temp_dir': str(temp_path),
                'screenshots_dir': str(temp_path / 'screenshots'),
                'logs_dir': str(temp_path / 'logs')
            }
            
            execution_result = {
                'script_name': 'test_subprocess.py',
                'errors': [],
                'performance_metrics': {},
                'test_results': {},
                'console_logs': []
            }
            
            # Should use pytest to run the test
            await test_executor._execute_with_monitoring(
                execution_env, execution_result, test_config
            )
            
            # Check that pytest was used
            assert 'test_results' in execution_result
            assert execution_result.get('pytest_used', False) == True
    
    @pytest.mark.asyncio
    async def test_error_handling_in_execution(self, test_executor, test_config):
        """Test error handling when script fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            script_path = temp_path / "test_error.py"
            
            # Write a test that will fail
            script_path.write_text('''
def test_failing():
    assert False, "This test should fail"
''')
            
            execution_env = {
                'enhanced_script_path': str(script_path),
                'temp_dir': str(temp_path),
                'screenshots_dir': str(temp_path / 'screenshots'),
                'logs_dir': str(temp_path / 'logs')
            }
            
            execution_result = {
                'script_name': 'test_error.py',
                'errors': [],
                'performance_metrics': {},
                'console_logs': []
            }
            
            # Should handle the error gracefully
            await test_executor._execute_with_monitoring(
                execution_env, execution_result, test_config
            )
            
            # Should have captured the error
            assert len(execution_result['errors']) > 0 or execution_result.get('test_failed', False)