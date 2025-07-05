#!/usr/bin/env python3
"""
Demo script for AI-powered test generation
Shows how to use different AI providers to generate Playwright tests
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from simple_runner import run_test_suite, generate_test_scripts


async def demo_ai_test_generation():
    """
    Demonstrate AI-powered test generation with different providers
    """
    print("🤖 AI-Powered Playwright Test Generator Demo")
    print("=" * 60)
    
    # Check available AI providers
    providers = {
        'claude': os.getenv('ANTHROPIC_API_KEY'),
        'gemini': os.getenv('GOOGLE_API_KEY'),
        'gpt': os.getenv('OPENAI_API_KEY')
    }
    
    available_providers = [name for name, key in providers.items() if key]
    
    if not available_providers:
        print("❌ No AI providers configured!")
        print("\nPlease set at least one of these environment variables:")
        print("  - ANTHROPIC_API_KEY (for Claude)")
        print("  - GOOGLE_API_KEY (for Gemini)")
        print("  - OPENAI_API_KEY (for GPT)")
        return
    
    print(f"✅ Available AI providers: {', '.join(available_providers)}")
    print()
    
    # Demo URL - you can change this to your application
    demo_url = "https://demo.playwright.dev/todomvc"
    
    # Generate tests with each available provider
    for provider in available_providers:
        print(f"\n🔧 Generating tests with {provider.upper()}...")
        
        try:
            output_dir = f"./generated_tests_{provider}"
            
            # Generate test scripts
            scripts_path = await generate_test_scripts(
                url=demo_url,
                username="demo_user",  # Not needed for demo site
                password="demo_pass",  # Not needed for demo site
                output_dir=output_dir,
                ai_provider=provider,  # Specify the AI provider
                test_types=['navigation', 'form_interaction', 'accessibility'],
                browser='chromium',
                headless=True
            )
            
            print(f"✅ Tests generated successfully at: {scripts_path}")
            
            # List generated files
            scripts_dir = Path(scripts_path)
            if scripts_dir.exists():
                print(f"\n📁 Generated files:")
                for file in scripts_dir.glob("*.py"):
                    print(f"  - {file.name}")
                
                # Check for page objects
                po_dir = scripts_dir / "page_objects"
                if po_dir.exists():
                    print(f"\n📁 Page Objects:")
                    for file in po_dir.glob("*.py"):
                        print(f"  - {file.name}")
            
        except Exception as e:
            print(f"❌ Error with {provider}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✨ Demo completed!")
    print("\nTo execute the generated tests:")
    print("python simple_runner.py --mode execute --scripts-dir ./generated_tests_claude")


async def demo_tdd_workflow():
    """
    Demonstrate the complete TDD workflow
    """
    print("\n\n🔄 TDD Workflow Demo")
    print("=" * 60)
    
    # This would demonstrate:
    # 1. Red Phase - Generate failing tests
    # 2. Green Phase - Run tests (they should fail initially)
    # 3. Refactor Phase - Improve test structure
    
    print("1️⃣ RED PHASE: Generating tests that will fail initially...")
    print("   (Tests are written before implementation)")
    
    print("\n2️⃣ GREEN PHASE: Running tests to see failures...")
    print("   (This validates our test generation)")
    
    print("\n3️⃣ REFACTOR PHASE: Tests are already well-structured!")
    print("   (AI generates maintainable tests with Page Object Model)")


async def main():
    """Main demo function"""
    # Run the AI test generation demo
    await demo_ai_test_generation()
    
    # Show TDD workflow
    await demo_tdd_workflow()
    
    print("\n\n📚 Next Steps:")
    print("1. Set up your API keys (see AI_PROVIDERS_README.md)")
    print("2. Install AI dependencies: pip install -r requirements-ai.txt")
    print("3. Run test generation for your app")
    print("4. Execute and refine the generated tests")


if __name__ == "__main__":
    # Suppress asyncio warnings on Windows
    import warnings
    warnings.filterwarnings("ignore", category=ResourceWarning)
    
    asyncio.run(main())