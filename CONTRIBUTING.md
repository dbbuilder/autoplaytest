# Contributing to AutoPlayTest

First off, thank you for considering contributing to AutoPlayTest! It's people like you that make AutoPlayTest such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to support@autoplaytest.com.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs if possible**
* **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and explain which behavior you expected to see instead**
* **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Process

### Setting Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/your-username/autoplaytest.git
cd autoplaytest

# Add upstream remote
git remote add upstream https://github.com/dbbuilder/autoplaytest.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Code Style

We use several tools to maintain code quality:

* **Black** for code formatting
* **isort** for import sorting
* **flake8** for linting
* **mypy** for type checking

Run all checks:
```bash
make lint
```

Format code:
```bash
make format
```

### Testing

We aim for high test coverage. Please write tests for any new functionality.

```bash
# Run all tests
make test

# Run specific test file
pytest tests/unit/test_your_feature.py -v

# Run with coverage
make coverage
```

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

* `feat:` A new feature
* `fix:` A bug fix
* `docs:` Documentation only changes
* `style:` Changes that don't affect code meaning
* `refactor:` Code change that neither fixes a bug nor adds a feature
* `perf:` Code change that improves performance
* `test:` Adding missing tests
* `chore:` Changes to the build process or auxiliary tools

Examples:
```
feat: add support for webkit browser
fix: handle timeout errors in AI provider
docs: update installation instructions
test: add unit tests for login flow generation
```

### Branch Naming

Use descriptive branch names:
* `feature/add-webkit-support`
* `fix/timeout-error-handling`
* `docs/update-readme`
* `test/login-flow-coverage`

## Project Structure

```
autoplaytest/
├── src/
│   ├── ai/              # AI provider integrations
│   ├── core/            # Core engine and execution
│   ├── monitoring/      # Performance and error tracking
│   └── utils/           # Utility functions
├── tests/
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── fixtures/       # Test fixtures
├── config/             # Configuration files
└── docs/               # Documentation
```

### Adding a New AI Provider

1. Create a new provider in `src/ai/providers/`
2. Implement the `BaseAIProvider` interface
3. Add provider configuration in `config/ai_providers/`
4. Add prompt templates in `config/prompts/{provider}/`
5. Add tests in `tests/unit/test_{provider}_provider.py`
6. Update documentation

Example:
```python
# src/ai/providers/new_provider.py
from ai.providers.base_provider import BaseAIProvider

class NewProvider(BaseAIProvider):
    """Implementation of NewAI provider"""
    
    async def analyze_page(self, page_content: str) -> PageAnalysis:
        # Implementation
        pass
        
    async def generate_test(self, request: TestGenerationRequest) -> GeneratedTest:
        # Implementation
        pass
```

### Adding a New Test Type

1. Add the test type to `TestType` enum
2. Create prompt template in `config/prompts/`
3. Update test generator logic
4. Add examples in documentation
5. Write tests for the new type

## Documentation

* Use docstrings for all public functions and classes
* Include type hints for all parameters and return values
* Add usage examples in docstrings
* Update README.md for user-facing changes
* Update API documentation for new features

## Review Process

1. All submissions require review before merging
2. We use GitHub pull request reviews
3. Address all review comments
4. Ensure CI/CD passes
5. Maintain backwards compatibility when possible

## Community

* Join our [Discord server](https://discord.gg/autoplaytest)
* Follow us on [Twitter](https://twitter.com/autoplaytest)
* Read our [blog](https://blog.autoplaytest.com)

## Recognition

Contributors will be recognized in:
* The project README
* Release notes
* Our website's contributors page

Thank you for contributing to AutoPlayTest! 🎉