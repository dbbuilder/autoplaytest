#!/usr/bin/env python3
"""
Quick Start Script for AI Playwright Testing Engine
This script helps users get started quickly with the testing engine.
"""

import asyncio
import sys
import warnings
from pathlib import Path

# Suppress asyncio ResourceWarning on Windows
warnings.filterwarnings("ignore", category=ResourceWarning)

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from simple_runner import run_test_suite, generate_test_scripts, execute_test_scripts


async def quick_start_demo():
    """
    Quick start demonstration of the AI Playwright Testing Engine.
    Tests the TodoMVC demo application to show basic functionality.
    """
    print("🚀 AI Playwright Testing Engine - Quick Start Demo")
    print("=" * 60)
    
    demo_url = "https://demo.playwright.dev/todomvc"
    
    print(f"\n🎯 Running quick test on demo application: {demo_url}")
    print("This will demonstrate the one-line execution workflow...")
    
    try:
        # One-line execution demo
        results = await run_test_suite(
            url=demo_url,
            username="demo_user",  # Not used for this demo site
            password="demo_pass",  # Not used for this demo site
            browser="chromium",
            headless=True,
            test_types=["navigation", "forms"],
            test_duration=60,  # 1 minute quick test
            concurrent_users=1
        )
        
        print("\n✅ Quick start demo completed!")
        print(f"📊 Session ID: {results['session_id']}")
        print(f"📈 Results Summary:")
        print(f"   - Total Tests: {results['test_summary']['total_tests']}")
        print(f"   - Passed: {results['test_summary']['passed_tests']}")
        print(f"   - Failed: {results['test_summary']['failed_tests']}")
        print(f"   - Success Rate: {results['test_summary']['success_rate']:.1f}%")
        
        if results['screenshots']:
            print(f"📷 Screenshots captured: {len(results['screenshots'])}")
        
        if results['errors']:
            print(f"⚠️  Errors detected: {len(results['errors'])}")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"\n💡 Next steps:")
        print(f"   1. Check the generated reports and logs")
        print(f"   2. Try the two-part workflow: generate then execute")
        print(f"   3. Customize the configuration for your application")
        print(f"   4. Review the documentation in README.md")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Ensure you have installed all dependencies: pip install -r requirements.txt")
        print(f"   2. Install Playwright browsers: playwright install")
        print(f"   3. Check your internet connection")
        print(f"   4. Review the logs for detailed error information")


async def two_part_demo():
    """
    Demonstration of the two-part workflow: generate scripts then execute them.
    """
    print("\n" + "=" * 60)
    print("🔄 Two-Part Workflow Demo")
    print("=" * 60)
    
    demo_url = "https://demo.playwright.dev/todomvc"
    
    try:
        # Step 1: Generate scripts
        print("\n📝 Step 1: Generating test scripts...")
        scripts_path = await generate_test_scripts(
            url=demo_url,
            username="demo_user",
            password="demo_pass",
            output_dir="./quick_start_demo",
            browser="chromium",
            headless=True,
            test_types=["navigation", "forms"],
            test_duration=60
        )
        
        print(f"✅ Scripts generated at: {scripts_path}")
        
        # List the generated files
        scripts_dir = Path(scripts_path)
        if scripts_dir.exists():
            script_files = list(scripts_dir.glob("*.py"))
            print(f"📄 Generated files:")
            for script_file in script_files:
                print(f"   - {script_file.name}")
        
        # Step 2: Execute scripts
        print(f"\n🚀 Step 2: Executing generated scripts...")
        results = await execute_test_scripts(
            scripts_path,
            execution_config={
                "browser": "chromium",
                "headless": True
            }
        )
        
        print(f"✅ Execution completed!")
        print(f"📊 Session ID: {results['session_id']}")
        print(f"📈 Results Summary:")
        print(f"   - Total Tests: {results['test_summary']['total_tests']}")
        print(f"   - Passed: {results['test_summary']['passed_tests']}")
        print(f"   - Failed: {results['test_summary']['failed_tests']}")
        print(f"   - Success Rate: {results['test_summary']['success_rate']:.1f}%")
        
        print(f"\n🎉 Two-part demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Two-part demo failed: {str(e)}")


async def main():
    """Main entry point for the quick start script."""
    try:
        # Run the one-line demo
        await quick_start_demo()
        
        # Ask if user wants to see the two-part demo
        print(f"\n🤔 Would you like to see the two-part workflow demo? (y/n): ", end="")
        
        # For automation purposes, we'll run it automatically
        # In a real scenario, you could uncomment the input() line below
        # response = input().lower().strip()
        response = "y"  # Auto-run for demo
        
        if response in ['y', 'yes']:
            await two_part_demo()
        
        print(f"\n🚀 Quick start completed!")
        print(f"📚 For more examples, check out usage_examples.py")
        print(f"📖 Full documentation is available in README.md")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Quick start interrupted by user")
    except Exception as e:
        print(f"\n❌ Quick start failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    print("Starting AI Playwright Testing Engine Quick Start...")
    asyncio.run(main())
