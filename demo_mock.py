#!/usr/bin/env python3
"""
AutoPlayTest Mock Demo
Demonstrates the framework without requiring AI provider dependencies
"""

import asyncio
import sys
import random
from datetime import datetime
import time


class MockDemo:
    """Simple mock demo that simulates AutoPlayTest execution"""
    
    def __init__(self):
        self.demo_sites = {
            "1": {
                "name": "SauceDemo",
                "url": "https://www.saucedemo.com",
                "description": "E-commerce demo site",
                "tests": [
                    "test_login_with_valid_credentials",
                    "test_login_with_invalid_password",
                    "test_product_listing_page",
                    "test_add_product_to_cart",
                    "test_checkout_workflow",
                    "test_logout_functionality"
                ]
            },
            "2": {
                "name": "The Internet",
                "url": "https://the-internet.herokuapp.com",
                "description": "UI testing playground",
                "tests": [
                    "test_navigation_menu",
                    "test_form_authentication",
                    "test_dropdown_selection",
                    "test_checkboxes_interaction",
                    "test_javascript_alerts"
                ]
            }
        }
    
    def print_banner(self):
        """Print demo banner"""
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           🚀 AutoPlayTest Mock Demo 🚀                       ║
║                                                               ║
║   See how AI-powered test generation works                   ║
║   (Running in mock mode - no API keys required)              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """)
    
    async def run(self):
        """Run the mock demo"""
        self.print_banner()
        
        # Show available sites
        print("📋 Available Demo Sites:\n")
        for key, site in self.demo_sites.items():
            print(f"  {key}. {site['name']} - {site['url']}")
            print(f"     {site['description']}")
            print()
        
        # Get user choice
        choice = input("Select a demo site (1-2) or press Enter for default: ").strip() or "1"
        
        if choice not in self.demo_sites:
            choice = "1"
        
        site = self.demo_sites[choice]
        
        print(f"\n{'='*60}")
        print(f"🌐 Testing: {site['url']}")
        print(f"🤖 AI Provider: Claude (Mock Mode)")
        print(f"🧪 Test Suite: {site['name']}")
        print(f"{'='*60}\n")
        
        # Simulate page analysis
        print("📍 Analyzing page structure...")
        await self.simulate_progress(2)
        
        print("🤖 Generating test scenarios...")
        await self.simulate_progress(2)
        
        print("📝 Creating test scripts...")
        await self.simulate_progress(1)
        
        print("\n✅ Generated {} test cases\n".format(len(site['tests'])))
        
        # Simulate test execution
        print("🎭 Executing tests with Playwright...\n")
        
        results = await self.run_tests(site['tests'])
        
        # Display results
        self.display_results(results, site['name'])
    
    async def simulate_progress(self, seconds):
        """Simulate progress with dots"""
        for _ in range(seconds * 2):
            print(".", end="", flush=True)
            await asyncio.sleep(0.5)
        print()
    
    async def run_tests(self, tests):
        """Simulate test execution"""
        results = {
            "total": len(tests),
            "passed": 0,
            "failed": 0,
            "duration": 0,
            "tests": []
        }
        
        for test in tests:
            # Random duration and result
            duration = round(random.uniform(0.5, 3.0), 2)
            passed = random.random() > 0.15  # 85% pass rate
            
            status = "✅" if passed else "❌"
            print(f"{status} {test} ({duration}s)")
            
            results["duration"] += duration
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            results["tests"].append({
                "name": test,
                "passed": passed,
                "duration": duration
            })
            
            await asyncio.sleep(0.3)
        
        return results
    
    def display_results(self, results, site_name):
        """Display test results"""
        print(f"\n{'='*60}")
        print("📊 Test Results")
        print(f"{'='*60}")
        
        print(f"\n✅ Passed:  {results['passed']}/{results['total']}")
        print(f"❌ Failed:  {results['failed']}/{results['total']}")
        print(f"⏱️  Duration: {results['duration']:.1f}s")
        
        success_rate = (results['passed'] / results['total']) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n📁 Output Files:")
        print(f"   📸 Screenshots: ./reports/{site_name.lower()}/screenshots/")
        print(f"   📊 HTML Report: ./reports/{site_name.lower()}_report.html")
        print(f"   📄 Test Scripts: ./generated_tests/{site_name.lower()}/")
        
        print(f"\n{'='*60}")
        print("\n✨ Demo completed successfully!")
        print("\n💡 To run real tests with AI-powered generation:")
        print("   1. Add your AI provider API key to .env file")
        print("   2. Run: python src/simple_runner.py --url <your-site>")
        print("\n📚 Learn more at: https://github.com/dbbuilder/autoplaytest")


async def main():
    """Main entry point"""
    demo = MockDemo()
    await demo.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")