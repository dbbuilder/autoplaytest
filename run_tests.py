#!/usr/bin/env python3
"""
Test Runner for AI-Powered Playwright Test Generator
Runs all tests with proper configuration and reporting
"""

import sys
import os
import asyncio
from pathlib import Path
import pytest
import warnings

# Suppress asyncio warnings on Windows
warnings.filterwarnings("ignore", category=ResourceWarning)

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def run_tests(args=None):
    """
    Run the test suite with appropriate configuration
    
    Args:
        args: Optional list of pytest arguments
    """
    if args is None:
        args = []
    
    # Default pytest arguments
    default_args = [
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker validation
        "--asyncio-mode=auto",  # Auto async mode
        "--cov=src",  # Coverage for src directory
        "--cov-report=html",  # HTML coverage report
        "--cov-report=term-missing",  # Terminal coverage with missing lines
        "--cov-report=xml",  # XML coverage for CI
        "--html=reports/test_report.html",  # HTML test report
        "--self-contained-html",  # Include CSS/JS in HTML
        "tests/"  # Test directory
    ]
    
    # Combine arguments
    all_args = default_args + args
    
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Run pytest
    exit_code = pytest.main(all_args)
    
    # Print coverage report location
    if exit_code == 0:
        print("\n✅ All tests passed!")
        print(f"\n📊 Coverage report: {Path('htmlcov/index.html').absolute()}")
        print(f"📄 Test report: {Path('reports/test_report.html').absolute()}")
    else:
        print("\n❌ Some tests failed!")
    
    return exit_code


def run_specific_tests(test_type):
    """
    Run specific types of tests
    
    Args:
        test_type: Type of tests to run (unit, integration, all)
    """
    if test_type == "unit":
        return run_tests(["-m", "unit", "tests/unit/"])
    elif test_type == "integration":
        return run_tests(["-m", "integration", "tests/integration/"])
    elif test_type == "ai":
        return run_tests(["-m", "ai", "-k", "provider"])
    elif test_type == "fast":
        return run_tests(["-m", "not slow"])
    else:
        return run_tests()


def main():
    """Main entry point for test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run tests for AI Playwright Test Generator")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "ai", "fast"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    parser.add_argument(
        "-k",
        "--keyword",
        help="Run tests matching keyword expression"
    )
    parser.add_argument(
        "--failed-first",
        action="store_true",
        help="Run failed tests first"
    )
    parser.add_argument(
        "--pdb",
        action="store_true",
        help="Drop into debugger on failures"
    )
    parser.add_argument(
        "--no-cov",
        action="store_true",
        help="Disable coverage reporting"
    )
    
    args = parser.parse_args()
    
    # Build pytest arguments
    pytest_args = []
    
    if args.parallel:
        pytest_args.extend(["-n", "auto"])  # Use all CPU cores
    
    if args.keyword:
        pytest_args.extend(["-k", args.keyword])
    
    if args.failed_first:
        pytest_args.append("--failed-first")
    
    if args.pdb:
        pytest_args.append("--pdb")
    
    if args.no_cov:
        # Remove coverage args from defaults
        pytest_args.append("--no-cov")
    
    # Run tests based on type
    exit_code = run_specific_tests(args.type) if args.type != "all" else run_tests(pytest_args)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()