# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-Based Playwright Testing Engine that automatically generates and executes Playwright scripts to test web applications. It uses AI providers (Claude, Gemini, GPT) to analyze web pages and generate comprehensive test suites following TDD principles.

## Key Commands

### Setup & Installation
```bash
# Create/activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
make install         # Production dependencies + Playwright browsers
make install-dev     # All dependencies including dev/test
```

### Testing
```bash
# Run all tests
make test
python run_tests.py

# Run specific test types
make test-unit       # Unit tests only
make test-integration # Integration tests only
make test-parallel   # Run tests in parallel
make coverage        # Tests with coverage report

# Run a single test
pytest tests/unit/test_specific.py::TestClass::test_method -v
```

### Linting & Formatting
```bash
make lint    # Run flake8, mypy, pylint
make format  # Format with black and isort
```

### AI Test Generation
```bash
# Generate tests using AI
python src/simple_runner.py --url https://example.com --username user --password pass --mode generate --output-dir ./generated_tests

# Execute generated tests
python src/simple_runner.py --mode execute --scripts-dir ./generated_tests

# One-line execution (generate and run)
python src/simple_runner.py --url https://example.com --username user --password pass --mode one-line

# Specify AI provider
python src/simple_runner.py --url https://example.com --username user --password pass --mode generate --ai-provider claude
```

### Development
```bash
make clean      # Clean generated files
make run-demo   # Run AI generation demo
```

## Architecture Overview

### Core Components

1. **AI Integration** (`src/ai/`)
   - `providers/` - AI provider implementations (Claude, Gemini, GPT)
   - `intelligent_page_analyzer.py` - Web page analysis using AI
   - `test_generator.py` - AI-powered test generation

2. **Core Engine** (`src/core/`)
   - `engine/main_engine.py` - Main orchestration engine
   - `script_generator/ai_script_generator.py` - Script generation logic
   - `executor/test_executor.py` - Test execution with monitoring

3. **Monitoring** (`src/monitoring/`)
   - `performance/performance_monitor.py` - Performance metrics collection
   - `errors/error_detector.py` - Error detection and logging
   - `network/network_monitor.py` - Network request monitoring

4. **Simple Interface** (`src/simple_runner.py`)
   - Simplified API for common operations
   - Supports one-line execution, two-part execution (generate then execute)
   - Command-line interface

### Configuration System

- **Main config**: `config/config.yaml`
- **AI provider configs**: `config/ai_providers/*.yaml`
- **Prompt templates**: `config/prompts/{provider}/*.md`
- **Environment variables**: `.env` file (copy from `.env.example`)

### Key Design Patterns

1. **Async/Await Architecture** - All core operations are async for scalability
2. **Provider Pattern** - AI providers implement common interface
3. **TDD Focus** - Generated tests follow Given-When-Then structure
4. **Page Object Model** - Tests use POM for maintainability

## Environment Setup

### Required Environment Variables
```bash
# AI Provider API Keys (at least one required)
ANTHROPIC_API_KEY=your_claude_api_key
GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional settings
DEFAULT_AI_PROVIDER=claude  # claude, gemini, or gpt
```

### Python Version
- Requires Python 3.9+ (tested with 3.12.6)
- Uses type hints and modern async features

## Important Patterns

### Error Handling
- All async functions use try-except blocks
- Errors are logged to `logs/` directory
- Failed tests generate screenshots in `reports/`

### Test Generation Flow
1. Page analysis using AI to understand structure
2. Test scenario generation based on page elements
3. Script creation following TDD principles
4. Validation and execution

### Database Operations
- Uses SQLAlchemy for async database operations
- Connection pooling configured in `src/utils/database.py`
- Test results stored for historical analysis

## Testing Approach

### Test Categories
- `login` - Authentication flows
- `navigation` - Page routing and menu navigation
- `form_interaction` - Form validation and submission
- `search` - Search functionality
- `crud_operations` - Data operations
- `api_integration` - API endpoint testing
- `accessibility` - WCAG compliance
- `performance` - Load times and metrics
- `visual_regression` - UI consistency
- `e2e_workflow` - Complete user journeys

### Running Specific Tests
```bash
# Run tests with specific markers
pytest -m unit
pytest -m "not slow"
pytest -m ai

# Run with specific browser
python src/simple_runner.py --browser firefox
```

## CI/CD Integration

The project includes GitHub Actions workflow (`.github/workflows/ci.yml`) that:
- Runs on push to main/develop and PRs
- Sets up Python environment
- Installs dependencies and Playwright browsers
- Executes test suite
- Uploads test reports as artifacts