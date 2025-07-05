# AI-Powered Playwright Test Generator

## 🚀 Overview

This is a comprehensive, AI-powered test generation system that uses Claude (Anthropic), Gemini (Google), and GPT (OpenAI) to automatically generate Test-Driven Development (TDD) focused Playwright tests.

## 🤖 AI Providers

The system supports three AI providers:

1. **Claude (Anthropic)** - Recommended for best test generation quality
2. **Gemini (Google)** - Good for large-scale test generation
3. **GPT (OpenAI)** - Excellent for complex test scenarios

## 📋 Prerequisites

- Python 3.12.6 or higher
- Playwright installed
- API keys for at least one AI provider

## 🔧 Setup

### 1. Install Dependencies

```bash
cd d:\dev2\autoplaytest
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium firefox webkit
```

### 2. Configure AI Providers

Set environment variables for the AI providers you want to use:

#### Windows (Command Prompt)
```cmd
set ANTHROPIC_API_KEY=your_claude_api_key_here
set GOOGLE_API_KEY=your_gemini_api_key_here
set OPENAI_API_KEY=your_gpt_api_key_here
```

#### Windows (PowerShell)
```powershell
$env:ANTHROPIC_API_KEY = "your_claude_api_key_here"
$env:GOOGLE_API_KEY = "your_gemini_api_key_here"
$env:OPENAI_API_KEY = "your_gpt_api_key_here"
```

#### Linux/Mac
```bash
export ANTHROPIC_API_KEY="your_claude_api_key_here"
export GOOGLE_API_KEY="your_gemini_api_key_here"
export OPENAI_API_KEY="your_gpt_api_key_here"
```

### 3. Install AI Provider Libraries

```bash
# For Claude
pip install anthropic

# For Gemini
pip install google-generativeai

# For GPT
pip install openai
```

## 🎯 Usage

### Basic Usage

Generate tests using the default AI provider (first available):

```bash
run.bat --url https://your-app.com --username testuser --password testpass --mode generate --output-dir ./tests
```

### Specify AI Provider

Use a specific AI provider:

```bash
# Use Claude
run.bat --url https://your-app.com --username testuser --password testpass --mode generate --output-dir ./tests --ai-provider claude

# Use Gemini
run.bat --url https://your-app.com --username testuser --password testpass --mode generate --output-dir ./tests --ai-provider gemini

# Use GPT
run.bat --url https://your-app.com --username testuser --password testpass --mode generate --output-dir ./tests --ai-provider gpt
```

### Test Types

Specify which types of tests to generate:

```bash
run.bat --url https://your-app.com --username testuser --password testpass --mode generate --output-dir ./tests --test-types login navigation form_interaction accessibility
```

Available test types:
- `login` - Authentication and login flow tests
- `navigation` - Page navigation and routing tests
- `form_interaction` - Form filling and validation tests
- `search` - Search functionality tests
- `crud` - Create, Read, Update, Delete operation tests
- `api` - API integration tests
- `performance` - Performance and load time tests
- `accessibility` - Accessibility compliance tests
- `visual` - Visual regression tests
- `e2e` - End-to-end workflow tests

### Execute Generated Tests

After generating tests, execute them:

```bash
run.bat --mode execute --scripts-dir ./tests
```

## 📁 Configuration Files

### Main Configuration
`config/config.yaml` - Main system configuration

### AI Provider Configurations
- `config/ai_providers/claude.yaml` - Claude-specific settings
- `config/ai_providers/gemini.yaml` - Gemini-specific settings
- `config/ai_providers/gpt.yaml` - GPT-specific settings

### Prompt Templates
- `config/prompts/claude/` - Claude-optimized prompts
- `config/prompts/gemini/` - Gemini-optimized prompts
- `config/prompts/gpt/` - GPT-optimized prompts

## 🧪 TDD Approach

The system follows Test-Driven Development principles:

1. **Red Phase** - Generates tests that initially fail
2. **Green Phase** - Tests are written to pass once implementation is complete
3. **Refactor Phase** - Tests are structured for maintainability

Each generated test includes:
- Clear Given-When-Then documentation
- Proper async/await handling
- Comprehensive assertions
- Error handling
- Page Object Model implementation

## 📊 Generated Test Structure

```
generated_tests/
├── test_login_001.py          # Login functionality tests
├── test_navigation_002.py     # Navigation tests
├── test_forms_003.py          # Form interaction tests
├── page_objects/              # Page Object Model classes
│   ├── login_page.py
│   ├── dashboard_page.py
│   └── base_page.py
├── test_data/                 # Test data fixtures
├── run_tests.py              # Test runner script
└── requirements.txt          # Test dependencies
```

## 🔍 Troubleshooting

### No AI Provider Available
```
ValueError: No AI providers available. Please set API keys.
```
**Solution**: Set at least one API key environment variable.

### API Key Invalid
```
ValueError: Claude API key not found in environment variables
```
**Solution**: Ensure your API key is correctly set and valid.

### Import Errors
```
ModuleNotFoundError: No module named 'anthropic'
```
**Solution**: Install the required AI provider library.

## 🚀 Advanced Features

### Custom Test Templates
Edit prompt files in `config/prompts/{provider}/` to customize test generation.

### Parallel Test Generation
Use multiple AI providers simultaneously:

```python
# In your code
providers = ['claude', 'gemini', 'gpt']
for provider in providers:
    generator = AIScriptGenerator(provider)
    # Generate tests
```

### Performance Optimization
- Use `--headless` flag for faster analysis
- Limit test types to only what's needed
- Use `--parallel` flag for concurrent execution

## 📝 Example Generated Test

```python
"""
Test: Login functionality with TDD approach
Generated by Claude AI
"""

import pytest
from playwright.async_api import Page, expect
from page_objects.login_page import LoginPage

@pytest.mark.asyncio
class TestLoginFunctionality:
    """
    Test suite for login functionality
    Following TDD principles - tests written to fail first
    """
    
    async def test_should_login_successfully_when_valid_credentials(self, page: Page):
        """
        Given: User is on the login page with valid credentials
        When: User enters username and password and clicks login
        Then: User should be redirected to dashboard
        """
        # Arrange
        login_page = LoginPage(page)
        await login_page.navigate()
        
        # Act
        await login_page.login("testuser", "testpass")
        
        # Assert
        await expect(page).to_have_url("/dashboard")
        await expect(page.locator("h1")).to_have_text("Welcome")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your AI provider or feature
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details