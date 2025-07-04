"""
Usage Examples for AI Playwright Testing Engine
Demonstrates both one-line execution and two-part workflows.
"""

import asyncio
import json
from pathlib import Path
from src.simple_runner import (
    run_test_suite,
    generate_test_scripts,
    execute_test_scripts,
    SimpleRunner
)


async def example_one_line_execution():
    """
    Example 1: One-line execution - Complete test suite in a single call.
    This is the simplest way to run comprehensive tests.
    """
    print("=== Example 1: One-Line Execution ===")
    
    try:
        # Execute complete test suite in one call
        results = await run_test_suite(
            url="https://demo.playwright.dev/todomvc",
            username="demo_user",  # Not needed for this demo site
            password="demo_pass",  # Not needed for this demo site
            browser="chromium",
            headless=True,
            test_types=["navigation", "forms", "search"],
            concurrent_users=1,
            test_duration=120  # 2 minutes
        )
        
        print(f"✅ Test completed successfully!")
        print(f"Session ID: {results['session_id']}")
        print(f"Test Summary: {json.dumps(results['test_summary'], indent=2)}")
        print(f"Screenshots captured: {len(results['screenshots'])}")
        print(f"Videos recorded: {len(results['video_paths'])}")
        
        if results['errors']:
            print(f"⚠️  Errors encountered: {len(results['errors'])}")
            for error in results['errors'][:3]:  # Show first 3 errors
                print(f"  - {error.get('type', 'unknown')}: {error.get('message', 'No message')}")
        
    except Exception as e:
        print(f"❌ One-line execution failed: {str(e)}")


async def example_two_part_execution():
    """
    Example 2: Two-part execution - Generate scripts first, then execute them.
    This approach allows for script inspection and modification between phases.
    """
    print("\n=== Example 2: Two-Part Execution ===")
    
    try:
        # Phase 1: Generate test scripts
        print("📝 Phase 1: Generating test scripts...")
        
        scripts_path = await generate_test_scripts(
            url="https://demo.playwright.dev/todomvc",
            username="demo_user",
            password="demo_pass",
            output_dir="./generated_tests_example",
            browser="firefox",
            headless=False,  # Run with UI for debugging
            test_types=["login", "navigation", "forms"],
            test_duration=180  # 3 minutes
        )
        
        print(f"✅ Scripts generated at: {scripts_path}")
        
        # List generated files
        scripts_dir = Path(scripts_path)
        script_files = list(scripts_dir.glob("*.py"))
        print(f"📄 Generated {len(script_files)} script files:")
        for script_file in script_files:
            print(f"  - {script_file.name}")
        
        # Show manifest
        manifest_file = scripts_dir / "script_manifest.json"
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            print(f"\n📋 Script Manifest:")
            for script_info in manifest:
                print(f"  - {script_info['filename']}: {script_info['description']}")
        
        # Phase 2: Execute generated scripts
        print(f"\n🚀 Phase 2: Executing generated scripts...")
        
        # Optional: Modify execution configuration
        execution_config = {
            "browser": "chromium",  # Switch browser for execution
            "headless": True,       # Run headless for faster execution
            "concurrent_users": 2   # Run with multiple concurrent users
        }
        
        results = await execute_test_scripts(scripts_path, execution_config)
        
        print(f"✅ Execution completed!")
        print(f"Session ID: {results['session_id']}")
        print(f"Test Summary: {json.dumps(results['test_summary'], indent=2)}")
        
        # Show performance metrics summary
        if results['performance_metrics']:
            print(f"\n📊 Performance Summary:")
            for script_name, metrics in results['performance_metrics'].items():
                if 'page_load_times' in metrics and metrics['page_load_times']:
                    avg_load_time = sum(
                        m['metrics'].get('load_complete', 0) 
                        for m in metrics['page_load_times']
                    ) / len(metrics['page_load_times'])
                    print(f"  - {script_name}: Avg load time {avg_load_time:.2f}ms")
        
    except Exception as e:
        print(f"❌ Two-part execution failed: {str(e)}")


async def main():
    """
    Run all usage examples to demonstrate the AI Playwright Engine capabilities.
    """
    print("🚀 AI Playwright Testing Engine - Usage Examples")
    print("=" * 60)
    
    examples = [
        ("One-Line Execution", example_one_line_execution),
        ("Two-Part Execution", example_two_part_execution)
    ]
    
    for example_name, example_func in examples:
        try:
            print(f"\n🎯 Running {example_name}...")
            await example_func()
            print(f"✅ {example_name} completed successfully")
        except Exception as e:
            print(f"❌ {example_name} failed: {str(e)}")
        
        print("-" * 60)
    
    print("\n🎉 Examples completed!")
    print("\n💡 Next steps:")
    print("   1. Review the generated test scripts in the example directories")
    print("   2. Examine the execution reports and performance metrics")
    print("   3. Customize the configuration for your specific application")
    print("   4. Integrate the engine into your CI/CD pipeline")


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
