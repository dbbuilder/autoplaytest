"""
Test Executor for AI Playwright Engine
Handles the execution of generated Playwright test scripts with comprehensive monitoring.
"""

import asyncio
import json
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import psutil
import traceback

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from utils.logger import setup_logger
from monitoring.performance.performance_monitor import PerformanceMonitor
from monitoring.errors.error_detector import ErrorDetector


class TestExecutor:
    """
    Executes Playwright test scripts with comprehensive monitoring and error detection.
    Supports both direct script execution and file-based execution.
    """
    
    def __init__(self):
        """Initialize the Test Executor."""
        self.logger = setup_logger(__name__)
        self.performance_monitor = PerformanceMonitor()
        self.error_detector = ErrorDetector()
        
        # Runtime state
        self.playwright = None
        self.active_browsers: Dict[str, Browser] = {}
        self.active_contexts: Dict[str, BrowserContext] = {}
        self.execution_metrics: Dict[str, Any] = {}
        
    async def initialize(self) -> None:
        """Initialize the executor and its dependencies."""
        try:
            self.logger.info("Initializing Test Executor...")
            
            # Initialize Playwright
            self.playwright = await async_playwright().start()
            
            # Initialize monitoring components
            await self.performance_monitor.initialize()
            await self.error_detector.initialize()
            
            self.logger.info("Test Executor initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Test Executor: {str(e)}")
            raise    
    async def execute_script_file(
        self,
        script_path: str,
        config: Any,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute a Playwright script file with comprehensive monitoring.
        
        Args:
            script_path: Path to the script file to execute
            config: Test configuration object
            session_id: Unique session identifier
            
        Returns:
            Dictionary containing execution results and metrics
        """
        script_path_obj = Path(script_path)
        script_name = script_path_obj.name
        
        self.logger.info(f"Executing script file: {script_name}")
        
        start_time = time.time()
        execution_result = {
            'script_name': script_name,
            'script_path': str(script_path),
            'session_id': session_id,
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'errors': [],
            'performance_metrics': {},
            'screenshots': [],
            'videos': [],
            'console_logs': [],
            'network_logs': [],
            'execution_duration': 0
        }
        
        try:
            # Verify script file exists
            if not script_path_obj.exists():
                raise FileNotFoundError(f"Script file not found: {script_path}")
            
            # Create a temporary directory for this execution
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Prepare the execution environment
                execution_env = await self._prepare_execution_environment(
                    script_path_obj, temp_path, config
                )
                
                # Execute the script with monitoring
                await self._execute_with_monitoring(
                    execution_env, execution_result, config
                )
            
            execution_result['status'] = 'passed'
            execution_result['execution_duration'] = time.time() - start_time
            
            self.logger.info(f"Script execution completed successfully: {script_name}")
            
        except Exception as e:
            execution_result['status'] = 'failed'
            execution_result['execution_duration'] = time.time() - start_time
            execution_result['errors'].append({
                'type': 'execution_error',
                'message': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            })
            
            self.logger.error(f"Script execution failed: {script_name} - {str(e)}")
        
        return execution_result    
    async def execute_script_code(
        self,
        script_code: str,
        script_name: str,
        config: Any,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute Playwright script code directly with comprehensive monitoring.
        
        Args:
            script_code: The Playwright script code to execute
            script_name: Name identifier for the script
            config: Test configuration object
            session_id: Unique session identifier
            
        Returns:
            Dictionary containing execution results and metrics
        """
        self.logger.info(f"Executing script code: {script_name}")
        
        # Create a temporary file for the script code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(script_code)
            temp_script_path = temp_file.name
        
        try:
            # Execute the temporary script file
            result = await self.execute_script_file(temp_script_path, config, session_id)
            result['script_name'] = script_name  # Override with provided name
            return result
            
        finally:
            # Clean up temporary file
            Path(temp_script_path).unlink(missing_ok=True)
    
    async def _prepare_execution_environment(
        self,
        script_path: Path,
        temp_dir: Path,
        config: Any
    ) -> Dict[str, Any]:
        """
        Prepare the execution environment for a script.
        
        Args:
            script_path: Path to the script file
            temp_dir: Temporary directory for execution artifacts
            config: Test configuration
            
        Returns:
            Dictionary containing execution environment details
        """
        # Create subdirectories for artifacts
        screenshots_dir = temp_dir / "screenshots"
        videos_dir = temp_dir / "videos"
        logs_dir = temp_dir / "logs"
        
        screenshots_dir.mkdir(exist_ok=True)
        videos_dir.mkdir(exist_ok=True)
        logs_dir.mkdir(exist_ok=True)
        
        # Read and prepare the script content
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Inject monitoring and configuration into the script
        enhanced_script = await self._enhance_script_with_monitoring(
            script_content, temp_dir, config
        )
        
        # Write the enhanced script
        enhanced_script_path = temp_dir / f"enhanced_{script_path.name}"
        with open(enhanced_script_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_script)
        
        return {
            'original_script_path': str(script_path),
            'enhanced_script_path': str(enhanced_script_path),
            'temp_dir': str(temp_dir),
            'screenshots_dir': str(screenshots_dir),
            'videos_dir': str(videos_dir),
            'logs_dir': str(logs_dir),
            'script_content': script_content,
            'enhanced_script': enhanced_script
        }
    
    async def shutdown(self) -> None:
        """
        Gracefully shutdown the Test Executor and cleanup resources.
        """
        self.logger.info("Shutting down Test Executor...")
        
        try:
            # Cleanup any running browser instances
            if hasattr(self, 'browser') and self.browser:
                await self.browser.close()
                
            # Cleanup temporary directories
            if hasattr(self, 'temp_dirs'):
                for temp_dir in self.temp_dirs:
                    if temp_dir.exists():
                        import shutil
                        shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Clear execution metrics
            self.execution_metrics.clear()
            
            self.logger.info("Test Executor shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during Test Executor shutdown: {str(e)}")
            # Don't raise, just log the error
    
    async def _execute_with_monitoring(
        self,
        execution_env: Dict[str, Any],
        execution_result: Dict[str, Any],
        config: Any
    ) -> None:
        """
        Execute the test script with comprehensive monitoring.
        
        Args:
            execution_env: Dictionary containing execution environment details
            execution_result: Dictionary to store execution results
            config: Test configuration
        """
        import subprocess
        import sys
        import json
        from pathlib import Path
        
        script_path = execution_env['enhanced_script_path']
        temp_dir = execution_env['temp_dir']
        
        self.logger.info(f"Executing script with monitoring: {script_path}")
        
        try:
            # Prepare pytest command
            cmd = [
                sys.executable,
                '-m', 'pytest',
                script_path,
                '-v',
                '--json-report',
                '--json-report-file=' + str(Path(temp_dir) / 'report.json'),
                '--tb=short'
            ]
            
            # Add performance monitoring
            start_time = time.time()
            
            # Execute the script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Capture performance metrics
            execution_result['performance_metrics'] = {
                'duration': duration,
                'start_time': start_time,
                'end_time': end_time
            }
            
            # Mark that pytest was used
            execution_result['pytest_used'] = True
            
            # Parse test results
            report_file = Path(temp_dir) / 'report.json'
            if report_file.exists():
                with open(report_file, 'r') as f:
                    test_report = json.load(f)
                    execution_result['test_results'] = test_report
                    
                    # Check if tests passed
                    if test_report.get('summary', {}).get('failed', 0) > 0:
                        execution_result['test_failed'] = True
                        execution_result['errors'].append({
                            'type': 'test_failure',
                            'message': f"Tests failed: {test_report['summary']['failed']} failures",
                            'details': test_report
                        })
            
            # Capture console output
            if result.stdout:
                execution_result['console_logs'].append({
                    'type': 'stdout',
                    'content': result.stdout,
                    'timestamp': datetime.now().isoformat()
                })
            
            if result.stderr:
                execution_result['console_logs'].append({
                    'type': 'stderr',
                    'content': result.stderr,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Check return code
            if result.returncode != 0:
                execution_result['errors'].append({
                    'type': 'execution_error',
                    'message': f"Script execution failed with return code: {result.returncode}",
                    'stdout': result.stdout,
                    'stderr': result.stderr
                })
                
        except subprocess.TimeoutExpired:
            execution_result['errors'].append({
                'type': 'timeout',
                'message': 'Script execution timed out after 300 seconds'
            })
        except Exception as e:
            execution_result['errors'].append({
                'type': 'execution_error',
                'message': str(e),
                'traceback': traceback.format_exc()
            })
            
        self.logger.info("Script execution with monitoring completed")