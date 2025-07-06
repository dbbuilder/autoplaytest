# AutoPlayTest - AI-Powered Web Testing Framework

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-green.svg)](https://playwright.dev/)

An intelligent testing framework that uses AI (Claude, GPT, Gemini) to automatically generate and execute Playwright test scripts for web applications. It analyzes your web pages, generates comprehensive test suites following TDD principles, and provides detailed reports on performance, errors, and user experience issues.

## 🎬 Demo

![AutoPlayTest Demo](https://github.com/dbbuilder/autoplaytest/assets/demo.gif)

Try it yourself:
```bash
# Quick demo - no API key required!
python demo.py
```

## 🌟 Features

- **AI-Powered Test Generation**: Leverages Claude, GPT-4, or Gemini to understand your web application and generate meaningful tests
- **Interactive Demo**: Try the framework instantly with built-in demo sites - no setup required!
- **Multiple Test Types**: Login flows, navigation, forms, CRUD operations, API integration, accessibility, and more
- **TDD Approach**: Generates tests following Test-Driven Development principles
- **Async Architecture**: Built for performance and scalability
- **Comprehensive Reporting**: Detailed test results with screenshots, performance metrics, and error tracking
- **Multiple Deployment Options**: Run locally, deploy to AWS Lambda, or use as a Docker container

## 📋 Prerequisites

- Python 3.9 or higher
- At least one AI provider API key:
  - [Claude API Key](https://console.anthropic.com/) (Anthropic)
  - [OpenAI API Key](https://platform.openai.com/) (GPT-4)
  - [Google API Key](https://makersuite.google.com/app/apikey) (Gemini)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/dbbuilder/autoplaytest.git
cd autoplaytest

# Quick setup (recommended)
python setup.py
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```env
# Add at least one AI provider key
ANTHROPIC_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Set default provider (claude, gpt, or gemini)
DEFAULT_AI_PROVIDER=claude
```

### 3. Run Your First Test

#### Option A: Run the Demo (Recommended)
```bash
# Windows
demo.bat

# Linux/macOS
./demo.sh
```

The demo will guide you through testing popular demo sites with or without API keys.

#### Option B: Test Your Own Site
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run a test
python src/simple_runner.py \
  --url https://example.com \
  --mode one-line \
  --ai-provider claude
```

## 📖 Usage Examples

### Command Line Interface

```bash
# Generate and execute tests in one command
python src/simple_runner.py \
  --url https://your-app.com \
  --username testuser \
  --password testpass \
  --mode one-line \
  --ai-provider claude

# Generate test scripts only
python src/simple_runner.py \
  --url https://your-app.com \
  --mode generate \
  --output-dir ./my_tests \
  --test-types login navigation forms

# Execute previously generated tests
python src/simple_runner.py \
  --mode execute \
  --scripts-dir ./my_tests
```

### Python API

```python
from src.simple_runner import run_test_suite
import asyncio

async def main():
    # Run complete test suite
    results = await run_test_suite(
        url="https://your-app.com",
        username="testuser",
        password="testpass",
        test_types=["login", "navigation", "forms"],
        ai_provider="claude",
        browser="chromium",
        headless=True
    )
    
    print(f"Tests passed: {results['passed']}/{results['total']}")
    print(f"Duration: {results['duration']}s")

# Run the async function
asyncio.run(main())
```

## 🧪 Test Types

AutoPlayTest can generate the following test types:

- **login**: Authentication and authorization flows
- **navigation**: Page routing and menu navigation
- **forms**: Form validation and submission
- **search**: Search functionality testing
- **crud**: Create, Read, Update, Delete operations
- **api**: API endpoint integration tests
- **accessibility**: WCAG compliance checks
- **performance**: Page load and response times
- **visual**: UI consistency and visual regression
- **e2e**: End-to-end user workflows

## 🏗️ Project Structure

```
autoplaytest/
├── src/
│   ├── ai/                    # AI provider integrations
│   │   ├── providers/         # Claude, GPT, Gemini implementations
│   │   └── test_generator.py  # Test generation logic
│   ├── core/
│   │   ├── engine/           # Main orchestration engine
│   │   ├── executor/         # Test execution
│   │   └── script_generator/ # Script generation
│   ├── monitoring/           # Performance and error tracking
│   └── simple_runner.py      # Main CLI interface
├── config/                   # Configuration files
│   ├── config.yaml          # Main configuration
│   └── prompts/             # AI prompt templates
├── tests/                   # Test suite for the framework
├── terraform/               # AWS Lambda deployment
├── requirements.txt         # Production dependencies
└── setup.py                # Setup script
```

## 🚀 Deployment Options

### Local Development
```bash
python src/simple_runner.py --url https://example.com
```

### Docker Container
```bash
docker build -t autoplaytest .
docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY autoplaytest \
  --url https://example.com
```

### AWS Lambda (Serverless)
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your API keys
./deploy.sh
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 📊 Example Output

```
🚀 Starting AI-powered test generation...
📍 Analyzing: https://example.com/login
🤖 Using AI Provider: Claude
📝 Generating test suite...

Generated Tests:
✅ test_successful_login_with_valid_credentials
✅ test_failed_login_with_invalid_password  
✅ test_validation_for_empty_fields
✅ test_password_reset_flow
✅ test_remember_me_functionality

🎭 Executing tests with Playwright...

Test Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 5/5 tests passed
⏱️  Total duration: 23.5s
📸 Screenshots saved to: reports/screenshots/
📊 Full report: reports/test_report.html
```

## 🔧 Configuration

### config/config.yaml
```yaml
ai_providers:
  default: claude
  
test_settings:
  timeout: 30000
  retry_attempts: 3
  screenshot_on_failure: true
  
browser:
  headless: true
  viewport:
    width: 1920
    height: 1080
```

### Environment Variables
- `ANTHROPIC_API_KEY` - Claude API key
- `OPENAI_API_KEY` - OpenAI API key  
- `GOOGLE_API_KEY` - Google API key
- `DEFAULT_AI_PROVIDER` - Default AI provider
- `LOG_LEVEL` - Logging level (INFO, DEBUG, ERROR)

## 📝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🧪 Running Tests

```bash
# Run all tests
make test

# Run with coverage
make coverage

# Run specific test file
pytest tests/unit/test_ai_providers.py -v
```

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Deployment Guide](DEPLOYMENT.md)
- [AWS Lambda Setup](TERRAFORM.md)
- [Development Guide](docs/development.md)

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**: Ensure virtual environment is activated
2. **API key errors**: Check your .env file and environment variables
3. **Playwright errors**: Run `playwright install` to install browsers
4. **Timeout errors**: Increase timeout in config.yaml

See [Troubleshooting Guide](docs/troubleshooting.md) for more solutions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) for browser automation
- [Anthropic](https://www.anthropic.com/), [OpenAI](https://openai.com/), and [Google](https://ai.google.dev/) for AI capabilities
- All contributors and testers

## 📞 Support

- 📧 Email: support@autoplaytest.com
- 💬 Discord: [Join our community](https://discord.gg/autoplaytest)
- 🐛 Issues: [GitHub Issues](https://github.com/dbbuilder/autoplaytest/issues)
- 📖 Docs: [Documentation](https://autoplaytest.readthedocs.io/)

---

Made with ❤️ by the AutoPlayTest Team