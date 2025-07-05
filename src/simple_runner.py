"""
Simple Runner Interface for AI Playwright Engine
Provides both one-line execution and two-part (generate + execute) workflows.
"""

import asyncio
import argparse
import json
import sys
import warnings
from pathlib import Path
from typing import Dict, Optional, Any
import yaml

# Suppress asyncio ResourceWarning on Windows
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", message="unclosed.*<socket.socket.*>")
warnings.filterwarnings("ignore", message="unclosed transport")
warnings.filterwarnings("ignore", message="Exception ignored in")

from core.engine.main_engine import AIPlaywrightEngine, TestConfiguration
from utils.logger import setup_logger


class SimpleRunner:
    """
    Simplified interface for running AI-based Playwright tests.
    Supports both one-line execution and separate generation/execution phases.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the Simple Runner.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.logger = setup_logger(__name__)
        self.engine = AIPlaywrightEngine(config_file)
        self.initialized = False
    
    async def _ensure_initialized(self) -> None:
        """Ensure the engine is initialized before use."""
        if not self.initialized:
            await self.engine.initialize()
            self.initialized = True
    
    async def run_one_line(
        self, 
        url: str, 
        username: str, 
        password: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a complete test suite in one line.
        Generates scripts, executes them, and returns results.
        
        Args:
            url: Target application URL
            username: Login username
            password: Login password
            **kwargs: Additional configuration options
            
        Returns:
            Dictionary containing test results and metrics
        """
        self.logger.info("Starting one-line test execution")
        self.logger.info(f"Target URL: {url}")
        
        await self._ensure_initialized()
        
        try:
            # Create test configuration
            config = TestConfiguration(
                url=url,
                username=username,
                password=password,
                **kwargs
            )
            
            # Execute comprehensive test
            results = await self.engine.run_comprehensive_test(config)
            
            # Convert results to dictionary for return
            results_dict = {
                'session_id': results.session_id,
                'status': results.status,
                'start_time': results.start_time.isoformat(),
                'end_time': results.end_time.isoformat() if results.end_time else None,
                'test_summary': {
                    'total_tests': results.total_tests,
                    'passed_tests': results.passed_tests,
                    'failed_tests': results.failed_tests,
                    'skipped_tests': results.skipped_tests,
                    'success_rate': (results.passed_tests / results.total_tests * 100) if results.total_tests > 0 else 0
                },
                'performance_metrics': results.performance_metrics,
                'errors': results.errors,
                'screenshots': results.screenshots,
                'video_paths': results.video_paths
            }
            
            self.logger.info("One-line execution completed successfully")
            return results_dict
            
        except Exception as e:
            self.logger.error(f"One-line execution failed: {str(e)}")
            raise    
    async def generate_scripts(
        self,
        url: str,
        username: str,
        password: str,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate Playwright test scripts without executing them.
        
        Args:
            url: Target application URL
            username: Login username
            password: Login password
            output_dir: Directory to store generated scripts
            **kwargs: Additional configuration options
            
        Returns:
            Path to directory containing generated scripts
        """
        self.logger.info("Starting script generation phase")
        self.logger.info(f"Target URL: {url}")
        
        await self._ensure_initialized()
        
        try:
            # Create test configuration
            config = TestConfiguration(
                url=url,
                username=username,
                password=password,
                **kwargs
            )
            
            # Generate scripts only
            scripts_path = await self.engine.generate_scripts_only(config, output_dir)
            
            self.logger.info(f"Scripts generated successfully at: {scripts_path}")
            return scripts_path
            
        except Exception as e:
            self.logger.error(f"Script generation failed: {str(e)}")
            raise    
    async def execute_scripts(
        self,
        scripts_dir: str,
        execution_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute previously generated Playwright scripts.
        
        Args:
            scripts_dir: Directory containing generated scripts
            execution_config: Optional execution configuration overrides
            
        Returns:
            Dictionary containing execution results
        """
        self.logger.info("Starting script execution phase")
        self.logger.info(f"Scripts directory: {scripts_dir}")
        
        await self._ensure_initialized()
        
        try:
            # Execute generated scripts
            results = await self.engine.execute_generated_scripts(scripts_dir, execution_config)
            
            # Convert results to dictionary for return
            results_dict = {
                'session_id': results.session_id,
                'status': results.status,
                'start_time': results.start_time.isoformat(),
                'end_time': results.end_time.isoformat() if results.end_time else None,
                'test_summary': {
                    'total_tests': results.total_tests,
                    'passed_tests': results.passed_tests,
                    'failed_tests': results.failed_tests,
                    'skipped_tests': results.skipped_tests,
                    'success_rate': (results.passed_tests / results.total_tests * 100) if results.total_tests > 0 else 0
                },
                'performance_metrics': results.performance_metrics,
                'errors': results.errors,
                'screenshots': results.screenshots,
                'video_paths': results.video_paths
            }
            
            self.logger.info("Script execution completed successfully")
            return results_dict
            
        except Exception as e:
            self.logger.error(f"Script execution failed: {str(e)}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the runner and cleanup resources."""
        if self.initialized:
            await self.engine.shutdown()
            self.initialized = False


# Convenience functions for direct usage
async def run_test_suite(url: str, username: str, password: str, **kwargs) -> Dict[str, Any]:
    """
    One-line function to run a complete test suite.
    
    Args:
        url: Target application URL
        username: Login username  
        password: Login password
        **kwargs: Additional configuration options
        
    Returns:
        Dictionary containing test results
        
    Example:
        results = await run_test_suite(
            "https://example.com",
            "testuser",
            "testpass",
            browser="firefox",
            headless=False,
            test_types=["login", "navigation", "forms"]
        )
    """
    runner = SimpleRunner()
    try:
        return await runner.run_one_line(url, username, password, **kwargs)
    finally:
        await runner.shutdown()


async def generate_test_scripts(
    url: str, 
    username: str, 
    password: str, 
    output_dir: Optional[str] = None,
    **kwargs
) -> str:
    """
    Generate Playwright test scripts for later execution.
    
    Args:
        url: Target application URL
        username: Login username
        password: Login password
        output_dir: Directory to store generated scripts
        **kwargs: Additional configuration options
        
    Returns:
        Path to directory containing generated scripts
        
    Example:
        scripts_path = await generate_test_scripts(
            "https://example.com",
            "testuser", 
            "testpass",
            output_dir="./my_tests",
            test_types=["login", "search", "checkout"]
        )
    """
    runner = SimpleRunner()
    try:
        return await runner.generate_scripts(url, username, password, output_dir, **kwargs)
    finally:
        await runner.shutdown()


async def execute_test_scripts(
    scripts_dir: str,
    execution_config: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Execute previously generated test scripts.
    
    Args:
        scripts_dir: Directory containing generated scripts
        execution_config: Optional execution configuration overrides
        
    Returns:
        Dictionary containing execution results
        
    Example:
        results = await execute_test_scripts(
            "./my_tests",
            execution_config={
                "browser": "chrome",
                "headless": True,
                "concurrent_users": 3
            }
        )
    """
    runner = SimpleRunner()
    try:
        return await runner.execute_scripts(scripts_dir, execution_config)
    finally:
        await runner.shutdown()


def load_config_from_file(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML or JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        if config_file.suffix.lower() in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        elif config_file.suffix.lower() == '.json':
            return json.load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_file.suffix}")


async def main():
    """Command-line interface for the Simple Runner."""
    # Suppress asyncio ResourceWarning on Windows
    import warnings
    warnings.filterwarnings("ignore", category=ResourceWarning)
    
    parser = argparse.ArgumentParser(description='AI Playwright Testing Engine')
    
    # Global arguments
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--url', type=str, required=True, help='Target application URL')
    parser.add_argument('--username', type=str, required=True, help='Login username')
    parser.add_argument('--password', type=str, required=True, help='Login password')
    
    # Mode selection
    parser.add_argument('--mode', choices=['one-line', 'generate', 'execute'], 
                       default='one-line', help='Execution mode')
    
    # Generation/execution specific arguments
    parser.add_argument('--output-dir', type=str, help='Output directory for generated scripts')
    parser.add_argument('--scripts-dir', type=str, help='Directory containing scripts to execute')
    
    # Test configuration arguments
    parser.add_argument('--browser', choices=['chromium', 'firefox', 'webkit'], 
                       default='chromium', help='Browser to use')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--test-types', nargs='+', 
                       default=['login', 'navigation', 'forms', 'search'],
                       help='Types of tests to generate')
    parser.add_argument('--concurrent-users', type=int, default=1,
                       help='Number of concurrent users to simulate')
    parser.add_argument('--test-duration', type=int, default=300,
                       help='Test duration in seconds')
    
    args = parser.parse_args()
    
    # Load additional configuration from file if provided
    extra_config = {}
    if args.config:
        extra_config = load_config_from_file(args.config)
    
    # Merge command line arguments with config file
    config = {
        'browser': args.browser,
        'headless': args.headless,
        'test_types': args.test_types,
        'concurrent_users': args.concurrent_users,
        'test_duration': args.test_duration,
        **extra_config
    }
    
    try:
        if args.mode == 'one-line':
            print("Running complete test suite...")
            results = await run_test_suite(args.url, args.username, args.password, **config)
            print(f"Test completed! Session ID: {results['session_id']}")
            print(f"Results: {results['test_summary']}")
            
        elif args.mode == 'generate':
            print("Generating test scripts...")
            scripts_path = await generate_test_scripts(
                args.url, args.username, args.password, args.output_dir, **config
            )
            print(f"Scripts generated at: {scripts_path}")
            print("Use the following command to execute them:")
            print(f"python simple_runner.py --mode execute --scripts-dir {scripts_path}")
            
        elif args.mode == 'execute':
            if not args.scripts_dir:
                print("Error: --scripts-dir is required for execute mode")
                sys.exit(1)
            
            print(f"Executing scripts from: {args.scripts_dir}")
            results = await execute_test_scripts(args.scripts_dir, config)
            print(f"Execution completed! Session ID: {results['session_id']}")
            print(f"Results: {results['test_summary']}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
