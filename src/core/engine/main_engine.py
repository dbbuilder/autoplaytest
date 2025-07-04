"""
AI-Based Playwright Testing Engine - Main Engine
Orchestrates the entire testing process from script generation to execution and reporting.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import yaml

from ..script_generator.ai_script_generator import AIScriptGenerator
from ..executor.test_executor import TestExecutor
from ...ai.pattern_analyzer import PatternAnalyzer
from ...monitoring.performance.performance_monitor import PerformanceMonitor
from ...monitoring.errors.error_detector import ErrorDetector
from ...reporting.generators.report_generator import ReportGenerator
from ...utils.config_manager import ConfigManager
from ...utils.logger import setup_logger
from ...utils.database import DatabaseManager


@dataclass
class TestConfiguration:
    """Configuration class for test execution parameters."""
    url: str
    username: str
    password: str
    test_types: List[str] = None
    browser: str = "chromium"
    headless: bool = True
    viewport: Dict[str, int] = None
    timeout: int = 30000
    concurrent_users: int = 1
    test_duration: int = 300  # seconds
    performance_thresholds: Dict[str, float] = None
    custom_scenarios: List[Dict] = None

    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.test_types is None:
            self.test_types = ["login", "navigation", "forms", "search"]
        if self.viewport is None:
            self.viewport = {"width": 1920, "height": 1080}
        if self.performance_thresholds is None:
            self.performance_thresholds = {
                "page_load_time": 3.0,
                "first_contentful_paint": 1.5,
                "largest_contentful_paint": 2.5,
                "cumulative_layout_shift": 0.1
            }
        if self.custom_scenarios is None:
            self.custom_scenarios = []


@dataclass
class TestResults:
    """Container for comprehensive test execution results."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    performance_metrics: Dict[str, Any] = None
    errors: List[Dict] = None
    screenshots: List[str] = None
    video_paths: List[str] = None
    detailed_logs: List[Dict] = None

    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.errors is None:
            self.errors = []
        if self.screenshots is None:
            self.screenshots = []
        if self.video_paths is None:
            self.video_paths = []
        if self.detailed_logs is None:
            self.detailed_logs = []


class AIPlaywrightEngine:
    """
    Main orchestration engine for AI-based Playwright testing.
    Coordinates script generation, execution, monitoring, and reporting.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the AI Playwright Engine.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.logger = setup_logger(__name__)
        self.config_manager = ConfigManager(config_path)
        self.db_manager = DatabaseManager(self.config_manager.get_database_config())
        
        # Initialize core components
        self.script_generator = AIScriptGenerator()
        self.test_executor = TestExecutor()
        self.pattern_analyzer = PatternAnalyzer()
        self.performance_monitor = PerformanceMonitor()
        self.error_detector = ErrorDetector()
        self.report_generator = ReportGenerator()
        
        # Runtime state
        self.active_sessions: Dict[str, TestResults] = {}
        self.is_running = False
        
        self.logger.info("AI Playwright Engine initialized successfully")

    async def initialize(self) -> None:
        """Initialize all engine components and dependencies."""
        try:
            self.logger.info("Initializing AI Playwright Engine components...")
            
            # Initialize database
            await self.db_manager.initialize()
            
            # Initialize AI components
            await self.script_generator.initialize()
            await self.pattern_analyzer.initialize()
            
            # Initialize monitoring components
            await self.performance_monitor.initialize()
            await self.error_detector.initialize()
            
            # Initialize executor
            await self.test_executor.initialize()
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize engine components: {str(e)}")
            raise

    async def run_comprehensive_test(self, config: TestConfiguration) -> TestResults:
        """
        Execute a comprehensive test suite based on the provided configuration.
        
        Args:
            config: Test configuration parameters
            
        Returns:
            TestResults object containing all test execution data
        """
        session_id = f"test_{int(time.time())}"
        start_time = datetime.now()
        
        self.logger.info(f"Starting comprehensive test session: {session_id}")
        self.logger.info(f"Target URL: {config.url}")
        self.logger.info(f"Test types: {config.test_types}")
        
        # Initialize test results container
        results = TestResults(
            session_id=session_id,
            start_time=start_time
        )
        self.active_sessions[session_id] = results
        
        try:
            # Phase 1: Analyze target application and generate test scripts
            self.logger.info("Phase 1: Analyzing application and generating test scripts...")
            await self._analyze_and_generate_scripts(config, results)
            
            # Phase 2: Execute generated test scripts
            self.logger.info("Phase 2: Executing test scripts...")
            await self._execute_test_scripts(config, results)
            
            # Phase 3: Analyze results and generate reports
            self.logger.info("Phase 3: Analyzing results and generating reports...")
            await self._analyze_and_report(config, results)
            
            results.end_time = datetime.now()
            results.status = "completed"
            
            self.logger.info(f"Test session {session_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Test session {session_id} failed: {str(e)}")
            results.status = "failed"
            results.end_time = datetime.now()
            raise
        
        return results

    async def generate_scripts_only(self, config: TestConfiguration, output_dir: str = None) -> str:
        """
        Generate Playwright scripts without executing them.
        
        Args:
            config: Test configuration parameters
            output_dir: Directory to store generated scripts (optional)
            
        Returns:
            Path to the directory containing generated scripts
        """
        session_id = f"generate_{int(time.time())}"
        
        if output_dir is None:
            output_dir = f"generated_scripts/{session_id}"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Generating scripts for session: {session_id}")
        self.logger.info(f"Output directory: {output_path.absolute()}")
        
        try:
            # Analyze the target application
            self.logger.info("Analyzing target application structure...")
            analysis_results = await self.pattern_analyzer.analyze_application(
                url=config.url,
                username=config.username,
                password=config.password
            )
            
            # Generate test scripts based on analysis
            self.logger.info("Generating AI-powered test scripts...")
            generated_scripts = await self.script_generator.generate_test_suite(
                analysis_results=analysis_results,
                config=config
            )
            
            # Save scripts to files
            script_manifest = []
            for i, script in enumerate(generated_scripts):
                script_filename = f"test_{script['type']}_{i:03d}.py"
                script_path = output_path / script_filename
                
                # Write the complete Playwright script
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(script['code'])
                
                # Create script metadata
                metadata = {
                    'filename': script_filename,
                    'type': script['type'],
                    'description': script['description'],
                    'estimated_duration': script.get('estimated_duration', 30),
                    'dependencies': script.get('dependencies', []),
                    'priority': script.get('priority', 'medium')
                }
                script_manifest.append(metadata)
                
                self.logger.info(f"Generated script: {script_filename} ({script['type']})")
            
            # Save script manifest
            manifest_path = output_path / "script_manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(script_manifest, f, indent=2)
            
            # Save configuration used for generation
            config_path = output_path / "generation_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(config), f, indent=2, default=str)
            
            # Create execution script
            runner_script = self._generate_runner_script(output_path, script_manifest)
            runner_path = output_path / "run_tests.py"
            with open(runner_path, 'w', encoding='utf-8') as f:
                f.write(runner_script)
            
            self.logger.info(f"Generated {len(generated_scripts)} test scripts")
            self.logger.info(f"Scripts saved to: {output_path.absolute()}")
            
            return str(output_path.absolute())
            
        except Exception as e:
            self.logger.error(f"Failed to generate scripts: {str(e)}")
            raise

    async def execute_generated_scripts(self, scripts_dir: str, execution_config: Optional[Dict] = None) -> TestResults:
        """
        Execute previously generated Playwright scripts.
        
        Args:
            scripts_dir: Directory containing generated scripts
            execution_config: Optional execution configuration overrides
            
        Returns:
            TestResults object containing execution results
        """
        session_id = f"execute_{int(time.time())}"
        start_time = datetime.now()
        scripts_path = Path(scripts_dir)
        
        self.logger.info(f"Executing scripts from: {scripts_path.absolute()}")
        
        # Load script manifest
        manifest_path = scripts_path / "script_manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Script manifest not found: {manifest_path}")
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            script_manifest = json.load(f)
        
        # Load original configuration
        config_path = scripts_path / "generation_config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                config = TestConfiguration(**config_data)
        else:
            # Create minimal config if not available
            config = TestConfiguration(url="", username="", password="")
        
        # Apply execution config overrides
        if execution_config:
            for key, value in execution_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        # Initialize test results
        results = TestResults(
            session_id=session_id,
            start_time=start_time,
            total_tests=len(script_manifest)
        )
        self.active_sessions[session_id] = results
        
        try:
            # Execute each script in the manifest
            for script_info in script_manifest:
                script_path = scripts_path / script_info['filename']
                
                if not script_path.exists():
                    self.logger.warning(f"Script file not found: {script_path}")
                    results.skipped_tests += 1
                    continue
                
                self.logger.info(f"Executing script: {script_info['filename']}")
                
                # Execute the individual script
                script_result = await self.test_executor.execute_script_file(
                    script_path=str(script_path),
                    config=config,
                    session_id=session_id
                )
                
                # Update results based on script execution
                if script_result['status'] == 'passed':
                    results.passed_tests += 1
                elif script_result['status'] == 'failed':
                    results.failed_tests += 1
                    results.errors.extend(script_result.get('errors', []))
                else:
                    results.skipped_tests += 1
                
                # Collect performance metrics
                if 'performance_metrics' in script_result:
                    script_name = script_info['filename']
                    results.performance_metrics[script_name] = script_result['performance_metrics']
                
                # Collect screenshots and videos
                results.screenshots.extend(script_result.get('screenshots', []))
                results.video_paths.extend(script_result.get('videos', []))
                
                # Add detailed logs
                results.detailed_logs.append({
                    'script': script_info['filename'],
                    'timestamp': datetime.now().isoformat(),
                    'result': script_result
                })
            
            results.end_time = datetime.now()
            results.status = "completed"
            
            # Generate execution report
            await self._generate_execution_report(results, scripts_path)
            
            self.logger.info(f"Script execution completed for session: {session_id}")
            self.logger.info(f"Results: {results.passed_tests} passed, {results.failed_tests} failed, {results.skipped_tests} skipped")
            
        except Exception as e:
            self.logger.error(f"Script execution failed: {str(e)}")
            results.status = "failed"
            results.end_time = datetime.now()
            raise
        
        return results

    def _generate_runner_script(self, output_path: Path, script_manifest: List[Dict]) -> str:
        """Generate a standalone script runner for the generated tests."""
        runner_code = '''#!/usr/bin/env python3
"""
Standalone runner for generated Playwright test scripts.
This script can be executed independently to run all generated tests.
"""

import asyncio
import json
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_execution.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class StandaloneTestRunner:
    """Standalone test runner for generated Playwright scripts."""
    
    def __init__(self, scripts_dir: str):
        self.scripts_dir = Path(scripts_dir)
        self.results = {
            'session_id': f'standalone_{int(datetime.now().timestamp())}',
            'start_time': datetime.now().isoformat(),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'errors': [],
            'detailed_results': []
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Execute all test scripts in the manifest."""
        manifest_path = self.scripts_dir / 'script_manifest.json'
        
        if not manifest_path.exists():
            raise FileNotFoundError(f"Script manifest not found: {manifest_path}")
        
        with open(manifest_path, 'r') as f:
            script_manifest = json.load(f)
        
        self.results['total_tests'] = len(script_manifest)
        logger.info(f"Starting execution of {len(script_manifest)} test scripts")
        
        for script_info in script_manifest:
            script_path = self.scripts_dir / script_info['filename']
            
            if not script_path.exists():
                logger.warning(f"Script not found: {script_path}")
                self.results['skipped_tests'] += 1
                continue
            
            logger.info(f"Executing: {script_info['filename']}")
            
            try:
                # Execute the script using subprocess
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout per script
                )
                
                if result.returncode == 0:
                    self.results['passed_tests'] += 1
                    status = 'passed'
                    logger.info(f"✓ {script_info['filename']} - PASSED")
                else:
                    self.results['failed_tests'] += 1
                    status = 'failed'
                    error_info = {
                        'script': script_info['filename'],
                        'error': result.stderr,
                        'timestamp': datetime.now().isoformat()
                    }
                    self.results['errors'].append(error_info)
                    logger.error(f"✗ {script_info['filename']} - FAILED: {result.stderr}")
                
                # Store detailed results
                self.results['detailed_results'].append({
                    'script': script_info['filename'],
                    'status': status,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'execution_time': datetime.now().isoformat()
                })
                
            except subprocess.TimeoutExpired:
                self.results['failed_tests'] += 1
                logger.error(f"✗ {script_info['filename']} - TIMEOUT")
            except Exception as e:
                self.results['failed_tests'] += 1
                logger.error(f"✗ {script_info['filename']} - ERROR: {str(e)}")
        
        self.results['end_time'] = datetime.now().isoformat()
        
        # Save results
        results_path = self.scripts_dir / 'execution_results.json'
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Execution completed. Results saved to: {results_path}")
        logger.info(f"Summary: {self.results['passed_tests']} passed, "
                   f"{self.results['failed_tests']} failed, "
                   f"{self.results['skipped_tests']} skipped")
        
        return self.results


async def main():
    """Main execution function."""
    scripts_dir = Path(__file__).parent
    runner = StandaloneTestRunner(str(scripts_dir))
    
    try:
        results = await runner.run_all_tests()
        exit_code = 0 if results['failed_tests'] == 0 else 1
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Runner failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
'''
        return runner_code

    async def _analyze_and_generate_scripts(self, config: TestConfiguration, results: TestResults) -> None:
        """Internal method to analyze application and generate test scripts."""
        # Analyze the target application
        analysis_results = await self.pattern_analyzer.analyze_application(
            url=config.url,
            username=config.username,
            password=config.password
        )
        
        # Generate test scripts based on analysis
        generated_scripts = await self.script_generator.generate_test_suite(
            analysis_results=analysis_results,
            config=config
        )
        
        results.total_tests = len(generated_scripts)
        self.logger.info(f"Generated {len(generated_scripts)} test scripts")

    async def _execute_test_scripts(self, config: TestConfiguration, results: TestResults) -> None:
        """Internal method to execute generated test scripts."""
        # Implementation for script execution would go here
        pass

    async def _analyze_and_report(self, config: TestConfiguration, results: TestResults) -> None:
        """Internal method to analyze results and generate reports."""
        # Implementation for result analysis and reporting would go here
        pass

    async def _generate_execution_report(self, results: TestResults, scripts_path: Path) -> None:
        """Generate a comprehensive execution report."""
        report_data = {
            'session_id': results.session_id,
            'execution_summary': {
                'start_time': results.start_time.isoformat(),
                'end_time': results.end_time.isoformat() if results.end_time else None,
                'duration': str(results.end_time - results.start_time) if results.end_time else None,
                'total_tests': results.total_tests,
                'passed_tests': results.passed_tests,
                'failed_tests': results.failed_tests,
                'skipped_tests': results.skipped_tests,
                'success_rate': (results.passed_tests / results.total_tests * 100) if results.total_tests > 0 else 0
            },
            'performance_metrics': results.performance_metrics,
            'errors': results.errors,
            'detailed_logs': results.detailed_logs
        }
        
        # Save execution report
        report_path = scripts_path / f"execution_report_{results.session_id}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        self.logger.info(f"Execution report saved to: {report_path}")

    async def shutdown(self) -> None:
        """Gracefully shutdown the engine and cleanup resources."""
        self.logger.info("Shutting down AI Playwright Engine...")
        
        try:
            # Cleanup active sessions
            for session_id in list(self.active_sessions.keys()):
                self.logger.info(f"Cleaning up session: {session_id}")
                del self.active_sessions[session_id]
            
            # Shutdown components
            await self.test_executor.shutdown()
            await self.performance_monitor.shutdown()
            await self.error_detector.shutdown()
            await self.db_manager.shutdown()
            
            self.logger.info("Engine shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
            raise
