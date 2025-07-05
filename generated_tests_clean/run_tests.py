#!/usr/bin/env python3
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
