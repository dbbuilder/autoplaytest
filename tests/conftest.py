"""
Pytest Configuration and Shared Fixtures
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configure asyncio for Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        'ANTHROPIC_API_KEY': 'test-claude-key',
        'GOOGLE_API_KEY': 'test-gemini-key',
        'OPENAI_API_KEY': 'test-gpt-key'
    }):
        yield


@pytest.fixture
def sample_page_analysis():
    """Sample page analysis data for testing"""
    return {
        'url': 'https://example.com/login',
        'title': 'Login Page',
        'page_type': 'login',
        'elements': [
            {
                'selector': '#username',
                'type': 'input',
                'attributes': {'type': 'text', 'name': 'username'},
                'visible': True,
                'enabled': True
            },
            {
                'selector': '#password',
                'type': 'input',
                'attributes': {'type': 'password', 'name': 'password'},
                'visible': True,
                'enabled': True
            },
            {
                'selector': '#submit',
                'type': 'button',
                'text': 'Login',
                'visible': True,
                'enabled': True
            }
        ],
        'forms': [
            {
                'action': '/auth/login',
                'method': 'post',
                'fields': [
                    {'name': 'username', 'type': 'text', 'required': True},
                    {'name': 'password', 'type': 'password', 'required': True}
                ]
            }
        ],
        'navigation': [
            {'text': 'Home', 'href': '/'},
            {'text': 'About', 'href': '/about'},
            {'text': 'Contact', 'href': '/contact'}
        ],
        'api_endpoints': ['/api/auth/login', '/api/user/profile'],
        'authentication': {
            'has_login_form': True,
            'has_logout_button': False,
            'is_authenticated': False
        }
    }


@pytest.fixture
def mock_claude_response():
    """Mock Claude API response"""
    return Mock(content=[Mock(text='''
    {
        "page_info": {
            "url": "https://example.com/login",
            "title": "Login Page",
            "type": "login"
        },
        "elements": [
            {
                "selector": "#username",
                "type": "input",
                "text": "",
                "attributes": {"type": "text", "name": "username"},
                "interactive": true
            }
        ],
        "forms": [{"action": "/login", "method": "post"}],
        "navigation": ["/home", "/about"],
        "api_endpoints": ["/api/login"],
        "has_authentication": true,
        "user_flows": [],
        "test_scenarios": []
    }
    
    ```python
    import pytest
    from playwright.async_api import Page, expect
    
    @pytest.mark.asyncio
    async def test_login_with_valid_credentials(page: Page):
        """Test successful login"""
        await page.goto("https://example.com/login")
        await page.fill("#username", "testuser")
        await page.fill("#password", "testpass")
        await page.click("#submit")
        await expect(page).to_have_url("/dashboard")
    ```
    ''')])


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return Mock(
        choices=[
            Mock(
                message=Mock(
                    content='''```python
import pytest
from playwright.async_api import Page, expect

@pytest.mark.asyncio
async def test_login_flow(page: Page):
    """Test the login flow"""
    await page.goto("https://example.com/login")
    await page.fill("#username", "user")
    await page.fill("#password", "pass")
    await page.click("button[type='submit']")
    await expect(page).to_have_url("/dashboard")
```'''
                )
            )
        ]
    )


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary config directory structure"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create AI provider configs
    ai_providers_dir = config_dir / "ai_providers"
    ai_providers_dir.mkdir()
    
    # Create prompt directories
    prompts_dir = config_dir / "prompts"
    prompts_dir.mkdir()
    
    for provider in ['claude', 'gemini', 'gpt']:
        provider_dir = prompts_dir / provider
        provider_dir.mkdir()
        
        # Create sample prompts
        (provider_dir / "system_prompt.md").write_text(f"System prompt for {provider}")
        (provider_dir / "page_analysis.md").write_text(f"Page analysis prompt for {provider}")
        (provider_dir / "test_generation.md").write_text(f"Test generation prompt for {provider}")
    
    return config_dir