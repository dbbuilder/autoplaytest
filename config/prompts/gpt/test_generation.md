# Test Generation Prompt

Generate a complete Playwright test for the {test_type} functionality based on the following page analysis:

## Page Analysis
```json
{page_analysis}
```

## Test Context
- URL: {url}
- Additional Context: {context}

## Requirements

1. Generate a complete, executable Playwright test script in Python
2. Use async/await syntax
3. Include all necessary imports
4. Follow the Page Object Model pattern if applicable
5. Include proper error handling
6. Add meaningful assertions
7. Use data-testid selectors when possible, fallback to other reliable selectors

## Test Structure

The test should follow this structure:

```python
import asyncio
from playwright.async_api import async_playwright, expect

async def test_{test_type}_functionality():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Test implementation here
            pass
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_{test_type}_functionality())
```

## Output Format

Return the test code in a Python code block:

```python
# Your complete test code here
```

If you need to create a Page Object, include it in a separate code block labeled "page_object":

```python
# page_object
# Page object code here
```

Generate the test now: