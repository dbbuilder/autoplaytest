#!/usr/bin/env python3
"""
Example: Testing SauceDemo E-commerce Site
This example shows how to use the AI Playwright Testing Engine
to generate and execute tests for an e-commerce site.
"""

import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from simple_runner import SimpleRunner


async def test_saucedemo():
    """Test SauceDemo e-commerce site with AI-generated tests."""
    runner = SimpleRunner()
    
    try:
        # Configuration for SauceDemo
        config = {
            'url': 'https://www.saucedemo.com',
            'username': 'standard_user',
            'password': 'secret_sauce',
            'test_types': ['login', 'navigation', 'forms'],
            'ai_provider': 'gpt',  # Change to 'claude' or 'gemini' as needed
            'headless': True,
            'browser': 'chromium'
        }
        
        print("🚀 Starting AI-powered test generation and execution...")
        print(f"📍 Target: {config['url']}")
        print(f"🤖 AI Provider: {config['ai_provider'].upper()}")
        
        # Generate test scripts
        print("\n1️⃣ Generating test scripts with AI...")
        scripts_dir = await runner.generate_scripts(**config)
        print(f"   ✅ Scripts generated at: {scripts_dir}")
        
        # Execute the generated tests
        print("\n2️⃣ Executing generated tests...")
        results = await runner.execute_scripts(scripts_dir)
        
        # Display results
        test_summary = results.get('test_summary', {})
        print("\n3️⃣ Test Results:")
        print(f"   📊 Total tests: {test_summary.get('total_tests', 0)}")
        print(f"   ✅ Passed: {test_summary.get('passed_tests', 0)}")
        print(f"   ❌ Failed: {test_summary.get('failed_tests', 0)}")
        print(f"   📈 Success rate: {test_summary.get('success_rate', 0):.1f}%")
        
        await runner.shutdown()
        
        return test_summary.get('failed_tests', 1) == 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        await runner.shutdown()
        return False


if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_saucedemo())
    sys.exit(0 if success else 1)