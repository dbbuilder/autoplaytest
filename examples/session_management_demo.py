"""
Session Management Demo for AI Playwright Engine
Demonstrates how the engine handles login sessions across multiple tests.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from simple_runner import SimpleRunner, TestConfiguration


async def demo_session_management():
    """
    Demonstrate session management capabilities.
    """
    print("=" * 60)
    print("AI Playwright Engine - Session Management Demo")
    print("=" * 60)
    
    # Initialize the runner
    runner = SimpleRunner()
    
    try:
        # Demo configuration
        config = {
            'url': 'https://demo.opencart.com/admin',  # Example site
            'username': 'demo',
            'password': 'demo',
            'test_types': ['login', 'navigation', 'form_interaction', 'search'],
            'browser': 'chromium',
            'headless': False,  # Set to False to see the browser
            'ai_provider': 'claude'  # or 'gemini', 'gpt'
        }
        
        print("\n1. Generating test scripts with AI...")
        scripts_dir = await runner.generate_scripts(**config)
        print(f"   Scripts generated at: {scripts_dir}")
        
        print("\n2. Executing tests with session management...")
        print("   - Login test will run first and create a session")
        print("   - Subsequent tests will reuse the authenticated session")
        print("   - No need to login again for each test!")
        
        results = await runner.execute_scripts(scripts_dir)
        
        # Display results
        print("\n3. Test Results:")
        print(f"   - Total tests: {results['test_summary']['total_tests']}")
        print(f"   - Passed: {results['test_summary']['passed_tests']}")
        print(f"   - Failed: {results['test_summary']['failed_tests']}")
        print(f"   - Success rate: {results['test_summary']['success_rate']:.1f}%")
        
        # Show session management details
        print("\n4. Session Management Details:")
        for test_name, metrics in results.get('performance_metrics', {}).items():
            print(f"   - {test_name}: {metrics.get('status', 'unknown')}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await runner.shutdown()
        print("\nDemo completed!")


async def demo_with_custom_login():
    """
    Demonstrate using custom login function with session management.
    """
    print("\n" + "=" * 60)
    print("Custom Login Function Demo")
    print("=" * 60)
    
    from playwright.async_api import Page
    
    async def custom_login(page: Page, url: str, username: str, password: str):
        """Custom login function for specific application."""
        await page.goto(url)
        
        # Custom login logic here
        await page.fill('#username', username)
        await page.fill('#password', password)
        await page.click('button[type="submit"]')
        
        # Wait for login to complete
        await page.wait_for_load_state('networkidle')
    
    # This would be integrated into the test execution
    print("Custom login functions can be provided for specific applications")
    print("The session manager will use them to establish authenticated sessions")


async def demo_session_persistence():
    """
    Demonstrate session persistence across multiple test runs.
    """
    print("\n" + "=" * 60)
    print("Session Persistence Demo")
    print("=" * 60)
    
    print("Sessions are persisted to disk and can be reused across test runs:")
    print("1. First run creates and saves the session")
    print("2. Subsequent runs within the timeout period reuse the session")
    print("3. Expired sessions are automatically cleaned up")
    print("4. Sessions are isolated by domain and username")
    
    sessions_dir = Path("sessions")
    if sessions_dir.exists():
        session_files = list(sessions_dir.glob("*.json"))
        print(f"\nCurrently persisted sessions: {len(session_files)}")
        for session_file in session_files:
            print(f"  - {session_file.name}")


async def main():
    """Run all demos."""
    await demo_session_management()
    await demo_with_custom_login()
    await demo_session_persistence()


if __name__ == "__main__":
    asyncio.run(main())