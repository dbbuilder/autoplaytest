# Claude Test Generation Prompt
# Generates TDD-focused Playwright tests based on page analysis

Based on the page analysis provided, generate comprehensive Playwright tests following TDD principles.

## Context
- Page Analysis: {page_analysis}
- Test Type: {test_type}
- Application URL: {url}
- Additional Context: {context}

## Requirements

### 1. Test Structure
Generate a complete test file with:
- Proper imports and setup
- Test class with descriptive name
- Individual test methods for each scenario
- Proper async/await usage
- Cleanup and teardown when needed

### 2. TDD Approach
For each test:
- Write it to fail first (test the behavior, not implementation)
- Include clear Given-When-Then documentation
- One assertion per test (or grouped related assertions)
- Test both positive and negative scenarios

### 3. Test Scenarios to Include

#### For Login Pages:
- Valid login with correct credentials
- Invalid login with wrong password
- Invalid login with non-existent user
- Empty field validation
- SQL injection attempts
- XSS attempts in input fields
- Remember me functionality
- Password visibility toggle
- Redirect after login
- Session persistence

#### For Forms:
- Valid submission with all fields
- Required field validation
- Field format validation (email, phone, etc.)
- Min/max length validation
- Special character handling
- Form reset functionality
- Progress saving (if applicable)
- File upload (if applicable)
- Dynamic field dependencies

#### For Navigation:
- All menu items accessible
- Correct page routing
- Active state indicators
- Breadcrumb functionality
- Back button behavior
- Deep linking
- 404 handling

### 4. Code Requirements
```python
# Use this structure:
import pytest
from playwright.async_api import Page, expect, BrowserContext
import asyncio
from typing import Dict, Any
from page_objects.base_page import BasePage  # Update with actual page object

@pytest.mark.asyncio
class TestLogin:  # Update class name based on test type
    """
    Test suite for login functionality.  # Update description
    Follows TDD principles - tests written to fail first.
    """
    
    async def setup_method(self):
        """Setup test data and prerequisites"""
        self.test_data = {
            'username': 'test_user',
            'password': 'test_pass123'
        }
    
    async def test_should_succeed_when_valid_credentials(self, page: Page):
        """
        Given: User is on login page with valid credentials
        When: User enters credentials and clicks login
        Then: User should be redirected to dashboard
        """
        # Arrange
        page_object = BasePage(page)  # Update with specific page object
        await page_object.navigate()
        
        # Act
        # Perform the action being tested
        
        # Assert
        # Verify the expected outcome
        
    async def teardown_method(self):
        """Clean up test data"""
        pass
```

### 5. Best Practices
- Use Page Object Model pattern
- Implement explicit waits, not hard-coded delays
- Use data-testid attributes when available
- Include accessibility checks
- Add performance assertions where relevant
- Group related tests logically
- Use parameterized tests for similar scenarios
- Include edge cases and boundary testing

### 6. Assertions to Include
- Element visibility: `await expect(element).to_be_visible()`
- Text content: `await expect(element).to_have_text("expected")`
- Input values: `await expect(input).to_have_value("expected")`
- URL changes: `await expect(page).to_have_url("expected")`
- Element count: `await expect(elements).to_have_count(n)`
- Attribute values: `await expect(element).to_have_attribute("attr", "value")`
- CSS classes: `await expect(element).to_have_class("class-name")`
- Enabled/disabled state: `await expect(element).to_be_enabled()`

Generate complete, runnable test code that follows these guidelines.