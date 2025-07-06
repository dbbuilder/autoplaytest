#!/usr/bin/env python3
"""
AutoPlayTest Demo Script
Demonstrates the testing framework against a public demo site
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any

# Check for required dependencies
try:
    import playwright
except ImportError:
    print("❌ Playwright is not installed!")
    print("\nPlease install dependencies first:")
    print("  pip install -r requirements.txt")
    print("  playwright install chromium")
    print("\nOr for a quick demo installation:")
    print("  pip install playwright aiohttp pydantic python-dotenv pyyaml")
    print("  playwright install chromium")
    sys.exit(1)

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.simple_runner import run_test_suite, generate_test_scripts
    from src.utils.logger import setup_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nPlease ensure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    print("\nFor AI providers, also install:")
    print("  pip install anthropic openai google-generativeai")
    print("\nOr continue with mock mode (no AI providers needed)")
    print()
    
    # Try to import without AI providers for mock mode
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    try:
        from src.utils.logger import setup_logger
        from src.utils.mock_generator import MockTestGenerator
        MOCK_MODE_ONLY = True
    except ImportError:
        print("❌ Cannot run even in mock mode. Please install base dependencies:")
        print("  pip install aiohttp pydantic python-dotenv pyyaml")
        sys.exit(1)

# Demo configuration
DEMO_SITES = {
    "saucedemo": {
        "url": "https://www.saucedemo.com",
        "username": "standard_user",
        "password": "secret_sauce",
        "description": "E-commerce demo site with login, products, and checkout",
        "test_types": ["login", "navigation", "forms", "e2e"]
    },
    "herokuapp": {
        "url": "https://the-internet.herokuapp.com",
        "username": None,
        "password": None,
        "description": "Collection of common web elements and scenarios",
        "test_types": ["navigation", "forms", "ui_elements"]
    },
    "reqres": {
        "url": "https://reqres.in",
        "username": None,
        "password": None,
        "description": "REST API testing demo site",
        "test_types": ["api", "forms"]
    },
    "automationexercise": {
        "url": "https://automationexercise.com",
        "username": "demo@autoplaytest.com",
        "password": "Demo123!",
        "description": "Full e-commerce site with registration and checkout",
        "test_types": ["login", "navigation", "forms", "search", "cart"]
    }
}


class DemoRunner:
    """Runs AutoPlayTest demonstrations"""
    
    def __init__(self):
        self.logger = setup_logger("DemoRunner")
        self.results = {}
    
    def print_banner(self):
        """Print demo banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           🚀 AutoPlayTest Demo Runner 🚀                     ║
║                                                               ║
║   AI-Powered Web Testing Framework Demonstration             ║
║   Using Claude, GPT, or Gemini to generate tests             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def print_site_menu(self):
        """Print available demo sites"""
        print("\n📋 Available Demo Sites:\n")
        for idx, (key, site) in enumerate(DEMO_SITES.items(), 1):
            print(f"  {idx}. {site['url']}")
            print(f"     📝 {site['description']}")
            print(f"     🧪 Test types: {', '.join(site['test_types'])}")
            print()
    
    async def run_demo(self, site_key: str, ai_provider: str = "claude", 
                      mode: str = "one-line", headless: bool = True):
        """Run demo for a specific site"""
        site = DEMO_SITES.get(site_key)
        if not site:
            self.logger.error(f"Unknown site: {site_key}")
            return None
        
        print(f"\n{'='*60}")
        print(f"🌐 Testing: {site['url']}")
        print(f"🤖 AI Provider: {ai_provider}")
        print(f"🧪 Test Types: {', '.join(site['test_types'])}")
        print(f"{'='*60}\n")
        
        try:
            # Check if AI provider key is set
            env_key_map = {
                "claude": "ANTHROPIC_API_KEY",
                "gpt": "OPENAI_API_KEY",
                "gemini": "GOOGLE_API_KEY"
            }
            
            if not os.getenv(env_key_map.get(ai_provider, "")):
                print(f"⚠️  Warning: {env_key_map.get(ai_provider)} not set in environment")
                print("   Using mock mode for demonstration...")
                return await self.run_mock_demo(site_key)
            
            # Run actual test suite
            start_time = datetime.now()
            
            if mode == "generate":
                # Generate tests only
                print("📝 Generating test scripts...\n")
                scripts_path = await generate_test_scripts(
                    url=site["url"],
                    username=site.get("username"),
                    password=site.get("password"),
                    test_types=site["test_types"],
                    output_dir=f"./demo_tests/{site_key}",
                    ai_provider=ai_provider
                )
                
                print(f"\n✅ Test scripts generated at: {scripts_path}")
                
                # Display generated files
                scripts_dir = Path(scripts_path)
                test_files = list(scripts_dir.glob("test_*.py"))
                print(f"\n📁 Generated {len(test_files)} test files:")
                for test_file in test_files:
                    print(f"   - {test_file.name}")
                
                return {"status": "generated", "path": scripts_path}
                
            else:
                # Run tests
                print("🚀 Starting test execution...\n")
                results = await run_test_suite(
                    url=site["url"],
                    username=site.get("username"),
                    password=site.get("password"),
                    test_types=site["test_types"],
                    ai_provider=ai_provider,
                    browser="chromium",
                    headless=headless,
                    timeout=30000
                )
                
                duration = (datetime.now() - start_time).total_seconds()
                
                # Display results
                self.display_results(results, duration)
                
                return results
                
        except Exception as e:
            self.logger.error(f"Demo failed: {str(e)}")
            print(f"\n❌ Demo failed: {str(e)}")
            return None
    
    async def run_mock_demo(self, site_key: str) -> Dict[str, Any]:
        """Run a mock demo when API keys are not available"""
        print("🎭 Running in MOCK MODE (no AI provider key set)\n")
        
        # Simulate test generation
        print("📍 Analyzing page structure...")
        await asyncio.sleep(1)
        
        print("🤖 Generating test scenarios...")
        await asyncio.sleep(1)
        
        print("📝 Creating test scripts...")
        await asyncio.sleep(1)
        
        # Mock results based on site
        mock_results = {
            "saucedemo": {
                "total_tests": 8,
                "passed": 7,
                "failed": 1,
                "skipped": 0,
                "duration": 23.5,
                "tests": [
                    {"name": "test_successful_login", "status": "passed", "duration": 2.1},
                    {"name": "test_invalid_login", "status": "passed", "duration": 1.8},
                    {"name": "test_product_listing", "status": "passed", "duration": 3.2},
                    {"name": "test_add_to_cart", "status": "passed", "duration": 2.5},
                    {"name": "test_remove_from_cart", "status": "passed", "duration": 2.3},
                    {"name": "test_checkout_flow", "status": "failed", "duration": 5.1, 
                     "error": "Element not found: #checkout-complete"},
                    {"name": "test_sorting_products", "status": "passed", "duration": 3.4},
                    {"name": "test_logout", "status": "passed", "duration": 1.1}
                ]
            },
            "herokuapp": {
                "total_tests": 6,
                "passed": 6,
                "failed": 0,
                "skipped": 0,
                "duration": 18.2,
                "tests": [
                    {"name": "test_navigation_menu", "status": "passed", "duration": 2.8},
                    {"name": "test_form_authentication", "status": "passed", "duration": 3.1},
                    {"name": "test_dropdown_selection", "status": "passed", "duration": 2.4},
                    {"name": "test_checkboxes", "status": "passed", "duration": 2.2},
                    {"name": "test_dynamic_content", "status": "passed", "duration": 4.3},
                    {"name": "test_javascript_alerts", "status": "passed", "duration": 3.4}
                ]
            }
        }
        
        results = mock_results.get(site_key, {
            "total_tests": 5,
            "passed": 4,
            "failed": 1,
            "skipped": 0,
            "duration": 15.0,
            "tests": []
        })
        
        # Simulate test execution
        print("\n🎭 Executing tests with Playwright...\n")
        
        for test in results.get("tests", []):
            status_icon = "✅" if test["status"] == "passed" else "❌"
            print(f"{status_icon} {test['name']} ({test['duration']:.1f}s)")
            await asyncio.sleep(0.5)
        
        self.display_results(results, results["duration"])
        
        print("\n💡 Note: This was a mock demo. To run actual tests:")
        print("   1. Set your AI provider API key in .env file")
        print("   2. Run the demo again")
        
        return results
    
    def display_results(self, results: Dict[str, Any], duration: float):
        """Display test results in a formatted way"""
        print(f"\n{'='*60}")
        print("📊 Test Results")
        print(f"{'='*60}")
        
        total = results.get("total_tests", 0)
        passed = results.get("passed", 0)
        failed = results.get("failed", 0)
        skipped = results.get("skipped", 0)
        
        # Summary
        print(f"\n✅ Passed:  {passed}/{total}")
        print(f"❌ Failed:  {failed}/{total}")
        print(f"⏭️  Skipped: {skipped}/{total}")
        print(f"⏱️  Duration: {duration:.1f}s")
        
        # Success rate
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Test details
        if "tests" in results and results["tests"]:
            print(f"\n📋 Test Details:")
            for test in results["tests"]:
                status_icon = {
                    "passed": "✅",
                    "failed": "❌",
                    "skipped": "⏭️"
                }.get(test.get("status", "unknown"), "❓")
                
                print(f"   {status_icon} {test.get('name', 'Unknown')} "
                      f"({test.get('duration', 0):.1f}s)")
                
                if test.get("status") == "failed" and test.get("error"):
                    print(f"      └─ Error: {test.get('error')}")
        
        # Output locations
        print(f"\n📁 Output Files:")
        print(f"   📸 Screenshots: ./reports/screenshots/")
        print(f"   📊 HTML Report: ./reports/test_report.html")
        print(f"   📄 Logs: ./logs/test_execution.log")
        
        print(f"\n{'='*60}\n")


async def main():
    """Main demo function"""
    demo = DemoRunner()
    demo.print_banner()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Quick mode with arguments
        site_key = sys.argv[1] if sys.argv[1] in DEMO_SITES else "saucedemo"
        ai_provider = sys.argv[2] if len(sys.argv) > 2 else "claude"
        mode = sys.argv[3] if len(sys.argv) > 3 else "one-line"
        headless = "--no-headless" not in sys.argv
        
        await demo.run_demo(site_key, ai_provider, mode, headless)
    else:
        # Interactive mode
        demo.print_site_menu()
        
        # Get user selection
        try:
            choice = input("Select a demo site (1-4) or press Enter for default: ").strip()
            
            if not choice:
                site_key = "saucedemo"
            else:
                site_keys = list(DEMO_SITES.keys())
                site_key = site_keys[int(choice) - 1]
            
            # Get AI provider
            print("\n🤖 Select AI Provider:")
            print("  1. Claude (Anthropic)")
            print("  2. GPT (OpenAI)")
            print("  3. Gemini (Google)")
            
            provider_choice = input("\nSelect provider (1-3) or press Enter for Claude: ").strip()
            providers = ["claude", "gpt", "gemini"]
            ai_provider = providers[int(provider_choice) - 1] if provider_choice else "claude"
            
            # Get mode
            print("\n📋 Select Mode:")
            print("  1. One-line (generate and execute)")
            print("  2. Generate only")
            print("  3. Execute with browser visible")
            
            mode_choice = input("\nSelect mode (1-3) or press Enter for one-line: ").strip()
            
            if mode_choice == "2":
                mode = "generate"
                headless = True
            elif mode_choice == "3":
                mode = "one-line"
                headless = False
            else:
                mode = "one-line"
                headless = True
            
            # Run demo
            await demo.run_demo(site_key, ai_provider, mode, headless)
            
        except (ValueError, IndexError):
            print("\n❌ Invalid selection. Using defaults...")
            await demo.run_demo("saucedemo", "claude", "one-line", True)
        except KeyboardInterrupt:
            print("\n\n👋 Demo cancelled by user")
            sys.exit(0)
    
    print("🏁 Demo completed!")
    print("\n💡 To run your own tests:")
    print("   python src/simple_runner.py --url https://your-site.com --mode one-line")


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)
    
    # Run the demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        sys.exit(1)