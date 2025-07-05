# Simple Playwright Test Script
# File: test_playwright_basic.py
# Location: d:\dev2\autoplaytest\test_playwright_basic.py

import asyncio
from playwright.async_api import async_playwright

async def test_basic_navigation():
    """Test basic Playwright functionality by navigating to a website."""
    print("Starting Playwright test...")
    
    async with async_playwright() as p:
        # Launch browser
        print("Launching browser...")
        browser = await p.chromium.launch(
            headless=False,  # Set to False to see the browser
            slow_mo=1000     # Slow down actions by 1 second for visibility
        )
        
        # Create a new page
        page = await browser.new_page()
        
        # Navigate to example.com
        print("Navigating to example.com...")
        await page.goto('https://example.com')
        
        # Get the page title
        title = await page.title()
        print(f"Page title: {title}")
        
        # Take a screenshot
        print("Taking screenshot...")
        await page.screenshot(path='example_screenshot.png')
        print("Screenshot saved as 'example_screenshot.png'")
        
        # Wait a bit before closing
        await page.wait_for_timeout(2000)
        
        # Close browser
        await browser.close()
        print("Browser closed.")

async def test_form_interaction():
    """Test interacting with a login form."""
    print("\nStarting form interaction test...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        
        # Navigate to a test login page
        print("Navigating to test login page...")
        await page.goto('https://the-internet.herokuapp.com/login')
        
        # Fill in the username
        print("Filling username...")
        await page.fill('#username', 'tomsmith')
        
        # Fill in the password
        print("Filling password...")
        await page.fill('#password', 'SuperSecretPassword!')
        
        # Click the login button
        print("Clicking login button...")
        await page.click('button[type="submit"]')
        
        # Wait for navigation
        await page.wait_for_load_state('networkidle')
        
        # Check if login was successful
        success_message = await page.text_content('.flash.success')
        if success_message:
            print(f"Login successful! Message: {success_message.strip()}")
        
        # Take a screenshot of the logged-in page
        await page.screenshot(path='login_success_screenshot.png')
        print("Screenshot saved as 'login_success_screenshot.png'")
        
        await page.wait_for_timeout(2000)
        await browser.close()
        print("Test completed!")

async def main():
    """Run all tests."""
    print("=" * 50)
    print("Playwright Basic Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Basic navigation
        await test_basic_navigation()
        
        # Test 2: Form interaction
        await test_form_interaction()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())