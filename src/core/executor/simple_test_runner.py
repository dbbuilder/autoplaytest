"""
Simple test runner that executes pytest scripts
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

def run_pytest_script(script_path: str, timeout: int = 300) -> Dict[str, Any]:
    """
    Run a pytest script and capture results
    
    Args:
        script_path: Path to the test script
        timeout: Maximum execution time in seconds
        
    Returns:
        Dictionary with execution results
    """
    result = {
        'script': script_path,
        'status': 'unknown',
        'output': '',
        'error': '',
        'duration': 0,
        'timestamp': datetime.now().isoformat()
    }
    
    start_time = datetime.now()
    
    try:
        # Run pytest with JSON output
        cmd = [
            sys.executable, '-m', 'pytest',
            script_path,
            '-v',
            '--tb=short',
            '--json-report',
            '--json-report-file=test_report.json',
            '-s'  # Don't capture output
        ]
        
        # Execute the test
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        result['output'] = proc.stdout
        result['error'] = proc.stderr
        result['return_code'] = proc.returncode
        
        # Check if test passed
        if proc.returncode == 0:
            result['status'] = 'passed'
        else:
            result['status'] = 'failed'
            
        # Try to load JSON report if it exists
        report_file = Path('test_report.json')
        if report_file.exists():
            try:
                with open(report_file, 'r') as f:
                    json_report = json.load(f)
                    result['pytest_report'] = json_report
                    
                    # Extract test results
                    if 'tests' in json_report:
                        result['total_tests'] = len(json_report['tests'])
                        result['passed_tests'] = sum(1 for t in json_report['tests'] if t['outcome'] == 'passed')
                        result['failed_tests'] = sum(1 for t in json_report['tests'] if t['outcome'] == 'failed')
                
                # Clean up report file
                report_file.unlink()
                
            except Exception as e:
                result['report_error'] = str(e)
                
    except subprocess.TimeoutExpired:
        result['status'] = 'timeout'
        result['error'] = f'Test execution timed out after {timeout} seconds'
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
    
    # Calculate duration
    end_time = datetime.now()
    result['duration'] = (end_time - start_time).total_seconds()
    
    return result


async def run_test_script_async(script_path: str, timeout: int = 300) -> Dict[str, Any]:
    """
    Async wrapper for running pytest scripts
    """
    import asyncio
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, run_pytest_script, script_path, timeout)
    
    return result