# File: minimal_test_runner.py
# Location: d:\dev2\autoplaytest\minimal_test_runner.py

"""Minimal test runner that works with core packages only."""

import asyncio
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not available")

try:
    from fastapi import FastAPI
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("Warning: FastAPI not available")

async def test_playwright():
    """Test basic Playwright functionality."""
    if not PLAYWRIGHT_AVAILABLE:
        print("Skipping Playwright test - not installed")
        return False    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://example.com')
            title = await page.title()
            await browser.close()
            print(f"✓ Playwright test successful - Page title: {title}")
            return True
    except Exception as e:
        print(f"✗ Playwright test failed: {e}")
        return False

def test_fastapi():
    """Test basic FastAPI functionality."""
    if not FASTAPI_AVAILABLE:
        print("Skipping FastAPI test - not installed")
        return False
    
    try:
        app = FastAPI()
        
        @app.get("/")
        def read_root():
            return {"Hello": "World"}
        
        print("✓ FastAPI app created successfully")
        return True
    except Exception as e:        print(f"✗ FastAPI test failed: {e}")
        return False

async def main():
    """Run all available tests."""
    print("=" * 50)
    print("Minimal AutoPlayTest Functionality Test")
    print("=" * 50)
    print(f"Python: {sys.version}")
    print("=" * 50)
    
    # Test core functionality
    print("\nTesting core components...")
    
    # Playwright test
    await test_playwright()
    
    # FastAPI test
    test_fastapi()
    
    print("\n" + "=" * 50)
    print("Test completed")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())