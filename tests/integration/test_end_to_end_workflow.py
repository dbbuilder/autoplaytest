"""
End-to-End Integration Tests
Tests the complete workflow from analysis to test generation
"""

import pytest
import asyncio
import json
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from core.engine.main_engine import AIPlaywrightEngine, TestConfiguration
from ai.providers import AIProviderFactory, AIProviderType


class TestEndToEndWorkflow:
    """Test complete TDD workflow from start to finish"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_complete_tdd_workflow(self, tmp_path, mock_env_vars):
        """Test the entire TDD workflow: Red -> Green -> Refactor"""
        
        # Create temporary output directory
        output_dir = tmp_path / "generated_tests"
        output_dir.mkdir()
        
        # Mock the AI provider responses
        with patch('ai.providers.claude_provider.AsyncAnthropic') as mock_anthropic:
            # Setup mock client
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            
            # Mock page analysis response
            analysis_response = Mock(content=[Mock(text=json.dumps({
                "page_info": {
                    "url": "https://example.com/login",
                    "title": "Login Page",
                    "type": "login"
                },
                "elements": [
                    {
                        "selector": "#username",
                        "type": "input",
                        "attributes": {"type": "text", "name": "username"},
                        "interactive": True
                    },
                    {
                        "selector": "#password",
                        "type": "input",
                        "attributes": {"type": "password", "name": "password"},
                        "interactive": True
                    },
                    {
                        "selector": "#login-btn",
                        "type": "button",
                        "text": "Login",
                        "interactive": True
                    }
                ],
                "forms": [{"action": "/auth/login", "method": "post"}],
                "navigation": [],
                "api_endpoints": ["/api/auth/login"],
                "has_authentication": True,
                "user_flows": ["login", "logout"],
                "test_scenarios": ["valid_login", "invalid_login", "empty_fields"]
            }))])
            
            # Mock test generation response (TDD - failing test first)
            test_generation_response = Mock(content=[Mock(text='''
```python
"""
TDD Test for Login Functionality
Generated to fail first (Red phase)
"""

import pytest
from playwright.async_api import Page, expect
from page_objects.login_page import LoginPage


@pytest.mark.asyncio
class TestLoginTDD:
    """Login tests following TDD approach"""
    
    async def test_should_login_successfully_when_valid_credentials(self, page: Page):
        """
        Given: User is on login page with valid credentials
        When: User enters username and password and clicks login
        Then: User should be redirected to dashboard
        """
        # Arrange
        login_page = LoginPage(page)
        await login_page.navigate()
        
        # Act
        await login_page.enter_username("testuser@example.com")
        await login_page.enter_password("SecurePass123!")
        await login_page.click_login()
        
        # Assert - These will fail initially (Red phase)
        await expect(page).to_have_url("https://example.com/dashboard")
        await expect(page.locator("h1")).to_have_text("Welcome, Test User")
        
    async def test_should_show_error_when_invalid_credentials(self, page: Page):
        """
        Given: User is on login page with invalid credentials
        When: User enters wrong username/password
        Then: Error message should be displayed
        """
        # Arrange
        login_page = LoginPage(page)
        await login_page.navigate()
        
        # Act
        await login_page.enter_username("invalid@example.com")
        await login_page.enter_password("wrongpass")
        await login_page.click_login()
        
        # Assert
        error_message = page.locator(".error-message")
        await expect(error_message).to_be_visible()
        await expect(error_message).to_have_text("Invalid username or password")
        
    async def test_should_validate_empty_fields(self, page: Page):
        """
        Given: User is on login page
        When: User clicks login without entering credentials
        Then: Validation errors should be shown
        """
        # Arrange
        login_page = LoginPage(page)
        await login_page.navigate()
        
        # Act - Click login without entering anything
        await login_page.click_login()
        
        # Assert
        await expect(page.locator("#username-error")).to_have_text("Username is required")
        await expect(page.locator("#password-error")).to_have_text("Password is required")
```

```python # page_object
"""
Page Object for Login Page
Following Page Object Model pattern
"""

from playwright.async_api import Page


class LoginPage:
    """Login page object model"""
    
    def __init__(self, page: Page):
        self.page = page
        self.url = "https://example.com/login"
        
        # Locators
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("#login-btn")
        self.error_message = page.locator(".error-message")
        
    async def navigate(self):
        """Navigate to login page"""
        await self.page.goto(self.url)
        await self.page.wait_for_load_state("networkidle")
        
    async def enter_username(self, username: str):
        """Enter username"""
        await self.username_input.fill(username)
        
    async def enter_password(self, password: str):
        """Enter password"""
        await self.password_input.fill(password)
        
    async def click_login(self):
        """Click login button"""
        await self.login_button.click()
        
    async def login(self, username: str, password: str):
        """Complete login flow"""
        await self.enter_username(username)
        await self.enter_password(password)
        await self.click_login()
```
''')])
            
            # Mock validation response
            validation_response = Mock(content=[Mock(text=json.dumps({
                "is_valid": True,
                "issues": [],
                "suggestions": ["Consider adding retry logic for flaky tests"]
            }))])
            
            # Setup mock to return different responses
            mock_client.messages.create = AsyncMock(
                side_effect=[analysis_response, test_generation_response, validation_response]
            )
            
            # Initialize engine
            engine = AIPlaywrightEngine()
            await engine.initialize()
            
            # Create test configuration
            config = TestConfiguration(
                url="https://example.com/login",
                username="testuser",
                password="testpass",
                test_types=["login"]
            )
            
            # Phase 1: Generate scripts (Red phase)
            scripts_path = await engine.generate_scripts_only(config, str(output_dir))
            
            # Verify scripts were generated
            assert Path(scripts_path).exists()
            
            # Check generated files
            test_files = list(Path(scripts_path).glob("test_*.py"))
            assert len(test_files) > 0
            
            # Verify TDD structure in generated test
            test_file = test_files[0]
            test_content = test_file.read_text()
            
            # TDD markers
            assert "TDD" in test_content
            assert "Given:" in test_content
            assert "When:" in test_content
            assert "Then:" in test_content
            assert "Red phase" in test_content or "fail first" in test_content
            
            # Verify page object was created
            po_dir = Path(scripts_path) / "page_objects"
            assert po_dir.exists()
            po_files = list(po_dir.glob("*.py"))
            assert len(po_files) > 0
            
            # Phase 2: Validate generated tests
            # In real scenario, tests would fail here (Red)
            # Then developer implements functionality (Green)
            # Then refactor while keeping tests passing
            
            print(f"\n✅ TDD Workflow completed successfully!")
            print(f"📁 Generated tests at: {scripts_path}")
            print(f"🔴 Red phase: Tests written to fail")
            print(f"🟢 Green phase: Implement functionality to pass")
            print(f"🔵 Refactor phase: Improve code with passing tests")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_multi_provider_generation(self, tmp_path, mock_env_vars):
        """Test generating tests with multiple AI providers"""
        
        providers_to_test = []
        
        # Check which providers are available
        availability = AIProviderFactory.get_available_providers()
        
        if availability.get('claude'):
            providers_to_test.append('claude')
        if availability.get('gpt'):
            providers_to_test.append('gpt')
            
        if not providers_to_test:
            pytest.skip("No AI providers available for testing")
        
        # Test with each available provider
        for provider_name in providers_to_test:
            output_dir = tmp_path / f"tests_{provider_name}"
            output_dir.mkdir()
            
            # Mock the provider
            if provider_name == 'claude':
                with patch('ai.providers.claude_provider.AsyncAnthropic'):
                    await self._test_provider_generation(provider_name, output_dir)
            elif provider_name == 'gpt':
                with patch('ai.providers.gpt_provider.AsyncOpenAI'):
                    await self._test_provider_generation(provider_name, output_dir)
    
    async def _test_provider_generation(self, provider_name: str, output_dir: Path):
        """Test generation with specific provider"""
        from core.script_generator.ai_script_generator import AIScriptGenerator
        
        generator = AIScriptGenerator(provider_name)
        
        # Basic smoke test - ensure provider initializes
        assert generator.provider_type.value == provider_name
        assert generator.provider is not None