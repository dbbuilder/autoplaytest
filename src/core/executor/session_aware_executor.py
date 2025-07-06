"""
Session-Aware Test Executor for AI Playwright Engine
Extends the base TestExecutor with session management capabilities.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from core.executor.test_executor import TestExecutor
from core.session.session_manager import SessionManager, SessionData
from utils.logger import setup_logger


class SessionAwareTestExecutor(TestExecutor):
    """
    Enhanced test executor that manages authentication sessions.
    Executes login tests first and maintains session state for subsequent tests.
    """
    
    def __init__(self):
        """Initialize the Session-Aware Test Executor."""
        super().__init__()
        self.logger = setup_logger(__name__)
        self.session_manager = SessionManager()
        
        # Session state tracking
        self.current_session: Optional[SessionData] = None
        self.session_config: Optional[Dict[str, Any]] = None
        
    async def initialize(self) -> None:
        """Initialize the executor and its dependencies."""
        await super().initialize()
        await self.session_manager.initialize()
        self.logger.info("Session-Aware Test Executor initialized")
    
    async def execute_test_suite(
        self,
        test_scripts: List[Dict[str, Any]],
        config: Any,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute a test suite with proper session management.
        
        Args:
            test_scripts: List of test script metadata
            config: Test configuration object
            session_id: Unique session identifier
            
        Returns:
            Dictionary containing execution results for all tests
        """
        self.logger.info(f"Executing test suite with session management: {session_id}")
        
        # Store session config for reuse
        self.session_config = {
            'url': config.url,
            'username': config.username,
            'password': config.password
        }
        
        # Sort tests to execute login first
        sorted_scripts = self._sort_tests_for_session(test_scripts)
        
        # Execute tests with session management
        suite_results = {
            'session_id': session_id,
            'start_time': datetime.now().isoformat(),
            'tests': [],
            'session_created': False,
            'session_reused_count': 0
        }
        
        for script_info in sorted_scripts:
            test_result = await self._execute_single_test_with_session(
                script_info, config, session_id
            )
            
            suite_results['tests'].append(test_result)
            
            # Track session usage
            if test_result.get('session_created'):
                suite_results['session_created'] = True
            if test_result.get('session_reused'):
                suite_results['session_reused_count'] += 1
        
        suite_results['end_time'] = datetime.now().isoformat()
        return suite_results
    
    async def _execute_single_test_with_session(
        self,
        script_info: Dict[str, Any],
        config: Any,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute a single test with session management.
        
        Args:
            script_info: Test script metadata
            config: Test configuration
            session_id: Session identifier
            
        Returns:
            Test execution results
        """
        test_type = script_info.get('type', 'unknown')
        script_path = script_info.get('path')
        
        self.logger.info(f"Executing {test_type} test with session awareness")
        
        # Prepare the script with session injection
        if test_type != 'login' and self.current_session:
            # Inject session restoration for non-login tests
            script_path = await self._prepare_script_with_session(
                script_path, self.current_session, test_type
            )
        
        # Execute the test
        result = await self.execute_script_file(script_path, config, session_id)
        
        # If this was a login test and successful, capture the session
        if test_type == 'login' and result['status'] == 'passed':
            await self._capture_session_after_login(config)
            result['session_created'] = True
        elif test_type != 'login' and self.current_session:
            result['session_reused'] = True
        
        return result
    
    async def _prepare_script_with_session(
        self,
        script_path: str,
        session_data: SessionData,
        test_type: str
    ) -> str:
        """
        Prepare a test script with session injection.
        
        Args:
            script_path: Original script path
            session_data: Session data to inject
            test_type: Type of test
            
        Returns:
            Path to modified script
        """
        # Read original script
        with open(script_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        # Inject session restoration
        modified_code = await self.session_manager.inject_auth_steps(
            original_code, session_data, test_type
        )
        
        # Write to temporary file
        temp_path = Path(script_path).parent / f"session_{Path(script_path).name}"
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(modified_code)
        
        return str(temp_path)
    
    async def _capture_session_after_login(self, config: Any) -> None:
        """
        Capture session data after successful login.
        
        Args:
            config: Test configuration with credentials
        """
        # Create a temporary browser context to capture session
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            try:
                # Get or create session
                self.current_session, _ = await self.session_manager.get_or_create_session(
                    config.url,
                    config.username,
                    config.password,
                    context,
                    force_new=False  # Try to reuse if valid
                )
                
                self.logger.info("Session captured and stored for reuse")
                
            finally:
                await context.close()
                await browser.close()
    
    async def _enhance_script_with_monitoring(
        self,
        script_content: str,
        temp_dir: Path,
        config: Any
    ) -> str:
        """
        Enhance script with monitoring and session capabilities.
        
        Args:
            script_content: Original script content
            temp_dir: Temporary directory for artifacts
            config: Test configuration
            
        Returns:
            Enhanced script content
        """
        # First, check if we need session injection
        if self.current_session and 'test_login' not in script_content:
            # This is not a login test, inject session
            script_content = await self.session_manager.inject_auth_steps(
                script_content,
                self.current_session,
                self._detect_test_type(script_content)
            )
        
        # Add monitoring imports and setup
        monitoring_imports = """
import json
import time
from pathlib import Path
from datetime import datetime

# Performance tracking
performance_metrics = {
    'start_time': time.time(),
    'page_loads': [],
    'api_calls': [],
    'errors': []
}

# Original imports follow...
"""
        
        # Add monitoring hooks
        monitoring_hooks = f"""

# Monitoring configuration
SCREENSHOTS_DIR = Path(r"{temp_dir / 'screenshots'}")
LOGS_DIR = Path(r"{temp_dir / 'logs'}")
SCREENSHOTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Enhanced page creation with monitoring
async def create_monitored_page(context):
    page = await context.new_page()
    
    # Add performance tracking
    page.on("load", lambda: performance_metrics['page_loads'].append({{
        'url': page.url,
        'timestamp': time.time()
    }}))
    
    # Add error tracking
    page.on("pageerror", lambda error: performance_metrics['errors'].append({{
        'message': str(error),
        'timestamp': time.time()
    }}))
    
    # Add console logging
    console_logs = []
    page.on("console", lambda msg: console_logs.append({{
        'type': msg.type,
        'text': msg.text,
        'timestamp': time.time()
    }}))
    
    return page, console_logs

# Save metrics at test end
async def save_performance_metrics():
    performance_metrics['end_time'] = time.time()
    performance_metrics['duration'] = performance_metrics['end_time'] - performance_metrics['start_time']
    
    metrics_file = LOGS_DIR / f"metrics_{{int(time.time())}}.json"
    with open(metrics_file, 'w') as f:
        json.dump(performance_metrics, f, indent=2)
"""
        
        # Inject monitoring code
        lines = script_content.split('\n')
        enhanced_lines = []
        imports_added = False
        
        for i, line in enumerate(lines):
            # Add monitoring imports after initial imports
            if not imports_added and (line.startswith('import ') or line.startswith('from ')):
                if i + 1 < len(lines) and not (lines[i + 1].startswith('import ') or lines[i + 1].startswith('from ')):
                    enhanced_lines.append(line)
                    enhanced_lines.append('')
                    enhanced_lines.extend(monitoring_imports.strip().split('\n'))
                    enhanced_lines.extend(monitoring_hooks.strip().split('\n'))
                    imports_added = True
                    continue
            
            # Replace page creation with monitored version
            if 'page = await context.new_page()' in line:
                enhanced_lines.append(line.replace(
                    'page = await context.new_page()',
                    'page, console_logs = await create_monitored_page(context)'
                ))
                continue
            
            # Add metrics saving before script end
            if 'if __name__ == "__main__":' in line and i > 0:
                enhanced_lines.append('    # Save performance metrics')
                enhanced_lines.append('    await save_performance_metrics()')
                enhanced_lines.append('')
            
            enhanced_lines.append(line)
        
        # Ensure metrics are saved at the end
        if 'save_performance_metrics()' not in '\n'.join(enhanced_lines):
            enhanced_lines.extend([
                '',
                '    # Ensure metrics are saved',
                '    await save_performance_metrics()'
            ])
        
        return '\n'.join(enhanced_lines)
    
    async def _execute_with_monitoring(
        self,
        execution_env: Dict[str, Any],
        execution_result: Dict[str, Any],
        config: Any
    ) -> None:
        """
        Execute the enhanced script with monitoring.
        
        Args:
            execution_env: Execution environment details
            execution_result: Result dictionary to populate
            config: Test configuration
        """
        import subprocess
        import sys
        
        enhanced_script_path = execution_env['enhanced_script_path']
        logs_dir = Path(execution_env['logs_dir'])
        
        # Prepare execution command
        cmd = [sys.executable, enhanced_script_path]
        
        # Setup logging
        stdout_log = logs_dir / "stdout.log"
        stderr_log = logs_dir / "stderr.log"
        
        try:
            # Execute the script
            with open(stdout_log, 'w') as stdout_file, open(stderr_log, 'w') as stderr_file:
                process = subprocess.Popen(
                    cmd,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    cwd=str(Path(enhanced_script_path).parent)
                )
                
                # Monitor process with timeout
                timeout = config.timeout / 1000 if hasattr(config, 'timeout') else 60
                process.wait(timeout=timeout)
                
                if process.returncode == 0:
                    execution_result['status'] = 'passed'
                else:
                    execution_result['status'] = 'failed'
                    execution_result['errors'].append({
                        'type': 'execution_error',
                        'message': f'Script exited with code {process.returncode}',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Collect artifacts
            self._collect_execution_artifacts(execution_env, execution_result)
            
        except subprocess.TimeoutExpired:
            process.kill()
            execution_result['status'] = 'timeout'
            execution_result['errors'].append({
                'type': 'timeout_error',
                'message': f'Script execution timed out after {timeout} seconds',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            execution_result['status'] = 'failed'
            execution_result['errors'].append({
                'type': 'execution_error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def _collect_execution_artifacts(
        self,
        execution_env: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> None:
        """
        Collect artifacts from test execution.
        
        Args:
            execution_env: Execution environment details
            execution_result: Result dictionary to populate
        """
        # Collect screenshots
        screenshots_dir = Path(execution_env['screenshots_dir'])
        if screenshots_dir.exists():
            execution_result['screenshots'] = [
                str(f) for f in screenshots_dir.glob('*.png')
            ]
        
        # Collect performance metrics
        logs_dir = Path(execution_env['logs_dir'])
        metrics_files = list(logs_dir.glob('metrics_*.json'))
        if metrics_files:
            with open(metrics_files[-1], 'r') as f:
                execution_result['performance_metrics'] = json.load(f)
        
        # Collect logs
        stdout_log = logs_dir / "stdout.log"
        stderr_log = logs_dir / "stderr.log"
        
        if stdout_log.exists():
            with open(stdout_log, 'r') as f:
                execution_result['console_logs'].append({
                    'type': 'stdout',
                    'content': f.read()
                })
        
        if stderr_log.exists():
            with open(stderr_log, 'r') as f:
                content = f.read()
                if content.strip():
                    execution_result['console_logs'].append({
                        'type': 'stderr',
                        'content': content
                    })
    
    def _sort_tests_for_session(self, test_scripts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort tests to ensure login tests run first.
        
        Args:
            test_scripts: List of test scripts
            
        Returns:
            Sorted list with login tests first
        """
        login_tests = []
        other_tests = []
        
        for script in test_scripts:
            if script.get('type') == 'login':
                login_tests.append(script)
            else:
                other_tests.append(script)
        
        # Return login tests first, then others
        return login_tests + other_tests
    
    def _detect_test_type(self, script_content: str) -> str:
        """
        Detect the type of test from script content.
        
        Args:
            script_content: Test script content
            
        Returns:
            Test type string
        """
        content_lower = script_content.lower()
        
        if 'login' in content_lower or 'sign in' in content_lower:
            return 'login'
        elif 'navigation' in content_lower or 'navigate' in content_lower:
            return 'navigation'
        elif 'form' in content_lower or 'input' in content_lower:
            return 'form_interaction'
        elif 'search' in content_lower:
            return 'search'
        else:
            return 'general'
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the executor and cleanup resources."""
        await super().shutdown()
        await self.session_manager.shutdown()
        self.logger.info("Session-Aware Test Executor shutdown completed")