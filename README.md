# AI-Based Playwright Testing Engine

An intelligent Python-based testing engine that automatically generates and executes Playwright scripts to simulate user experiences, identify performance bottlenecks, errors, and inconsistencies across web applications.

## 🚀 Quick Start

### One-Line Execution
```python
from src.simple_runner import run_test_suite

# Run complete test suite in one command
results = await run_test_suite(
    url="https://your-app.com",
    username="your_username",
    password="your_password",
    browser="chromium",
    headless=True
)
```

### Two-Part Execution
```python
from src.simple_runner import generate_test_scripts, execute_test_scripts

# Step 1: Generate test scripts
scripts_path = await generate_test_scripts(
    url="https://your-app.com",
    username="your_username", 
    password="your_password",
    output_dir="./my_tests"
)

# Step 2: Execute generated scripts (can be done later)
results = await execute_test_scripts(scripts_path)
```

### Command Line Usage
```bash
# One-line execution
python src/simple_runner.py \
  --url https://your-app.com \
  --username your_user \
  --password your_pass \
  --mode one-line \
  --browser chromium \
  --headless

# Generate scripts only
python src/simple_runner.py \
  --url https://your-app.com \
  --username your_user \
  --password your_pass \
  --mode generate \
  --output-dir ./generated_tests

# Execute generated scripts
python src/simple_runner.py \
  --mode execute \
  --scripts-dir ./generated_tests
```

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- Git
- Internet connection (for downloading Playwright browsers)

### 🚀 Quick Setup (Recommended)

#### Windows
```cmd
git clone https://github.com/dbbuilder/autoplaytest.git
cd autoplaytest
quick_setup.bat
```

#### Linux/macOS
```bash
git clone https://github.com/dbbuilder/autoplaytest.git
cd autoplaytest
chmod +x quick_setup.sh
./quick_setup.sh
```

### 📋 Manual Setup

```bash
# Clone the repository
git clone https://github.com/dbbuilder/autoplaytest.git
cd autoplaytest

# Run setup script (creates virtual environment and installs dependencies)
python setup.py

# Or manually:
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 🎯 Quick Start Demo
```bash
# After setup, run the demo
python quick_start.py

# Or with virtual environment directly (without activation)
# Windows:
venv\Scripts\python.exe quick_start.py
# Linux/macOS:
./venv/bin/python quick_start.py
```

### Required Dependencies
```txt
playwright==1.40.0
asyncio==3.4.3
aiohttp==3.9.1
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
scikit-learn==1.3.2
numpy==1.24.3
pandas==2.0.3
tensorflow==2.15.0
beautifulsoup4==4.12.2
psutil==5.9.6
matplotlib==3.7.2
plotly==5.17.0
opencv-python==4.8.1.78
pyyaml==6.0.1
python-dotenv==1.0.0
loguru==0.7.2
pytest==7.4.3
pytest-asyncio==0.21.1
```

## 🎯 Key Features

### Intelligent Test Generation
- **AI-Powered Analysis**: Automatically analyzes web application structure and user flows
- **Comprehensive Coverage**: Generates tests for login, navigation, forms, search, and custom scenarios
- **Pattern Recognition**: Identifies common UI patterns and interaction flows
- **Smart Prioritization**: Focuses on critical user journeys and high-impact areas

### Performance Monitoring
- **Real-Time Metrics**: Tracks page load times, resource loading, memory usage
- **Core Web Vitals**: Monitors First Contentful Paint, Largest Contentful Paint, Cumulative Layout Shift
- **Network Analysis**: Captures failed requests, slow responses, payload analysis
- **Resource Optimization**: Identifies optimization opportunities

### Error Detection
- **JavaScript Errors**: Captures console errors, unhandled exceptions, warnings
- **Network Failures**: Detects HTTP errors, timeouts, connectivity issues
- **Visual Regression**: Screenshot comparison for UI consistency
- **Accessibility Issues**: Basic WCAG compliance checking

### Comprehensive Reporting
- **Executive Dashboard**: High-level performance and reliability overview
- **Detailed Analytics**: In-depth analysis with screenshots, videos, logs
- **Trend Analysis**: Historical performance tracking and baseline comparison
- **Alerting System**: Configurable alerts for failures and performance degradation

## 📁 Project Structure

```
autoplaytest/
├── src/
│   ├── core/
│   │   ├── engine/
│   │   │   └── main_engine.py          # Main orchestration engine
│   │   ├── script_generator/
│   │   │   └── ai_script_generator.py  # AI-powered script generation
│   │   └── executor/
│   │       └── test_executor.py        # Test execution with monitoring
│   ├── ai/
│   │   ├── pattern_analyzer.py         # Application pattern analysis
│   │   ├── test_generator.py          # Intelligent test generation
│   │   └── anomaly_detector.py        # Performance anomaly detection
│   ├── monitoring/
│   │   ├── performance/
│   │   │   └── performance_monitor.py  # Performance metrics collection
│   │   ├── errors/
│   │   │   └── error_detector.py       # Error detection and logging
│   │   └── network/
│   │       └── network_monitor.py      # Network request monitoring
│   ├── reporting/
│   │   ├── generators/
│   │   │   └── report_generator.py     # Report generation
│   │   └── templates/                  # Report templates
│   ├── api/
│   │   ├── routes/                     # REST API endpoints
│   │   └── models/                     # Data models
│   ├── utils/
│   │   ├── config_manager.py          # Configuration management
│   │   ├── logger.py                  # Logging utilities
│   │   └── database.py                # Database operations
│   └── simple_runner.py               # Simplified interface
├── setup.py                           # Automated setup script
├── quick_setup.bat                    # Windows quick setup
├── quick_setup.sh                     # Unix/Linux/macOS quick setup
├── quick_start.py                     # Demo script
├── usage_examples.py                  # Comprehensive examples
├── tests/                             # Test suite
├── config/                            # Configuration files
├── reports/                           # Generated reports
├── logs/                              # Application logs
└── data/                             # Data storage
```

## ⚙️ Configuration

### Basic Configuration
```yaml
# config/config.yaml
application:
  url: "https://your-application.com"
  credentials:
    username: "test_user"
    password: "test_password"

testing:
  browser: "chromium"  # chromium, firefox, webkit
  headless: true
  viewport:
    width: 1920
    height: 1080
  timeout: 30000
  concurrent_users: 1
  test_duration: 300

test_types:
  - login
  - navigation
  - forms
  - search
  - accessibility

performance_thresholds:
  page_load_time: 3.0
  first_contentful_paint: 1.5
  largest_contentful_paint: 2.5
  cumulative_layout_shift: 0.1

monitoring:
  capture_screenshots: true
  record_videos: true
  collect_console_logs: true
  track_network_requests: true

reporting:
  generate_html_report: true
  generate_json_report: true
  include_screenshots: true
  include_performance_charts: true
```

## 🔧 Usage Examples

### Example 1: Basic Website Testing
```python
import asyncio
from src.simple_runner import run_test_suite

async def test_ecommerce_site():
    results = await run_test_suite(
        url="https://demo-shop.com",
        username="customer@example.com",
        password="password123",
        test_types=["login", "navigation", "search", "checkout"],
        browser="chromium",
        headless=True,
        test_duration=300
    )
    
    print(f"Tests completed: {results['test_summary']}")
    return results

# Run the test
results = asyncio.run(test_ecommerce_site())
```

### Example 2: Multi-Browser Testing
```python
import asyncio
from src.simple_runner import SimpleRunner

async def multi_browser_testing():
    runner = SimpleRunner()
    
    browsers = ["chromium", "firefox", "webkit"]
    results = {}
    
    # Generate scripts once
    scripts_path = await runner.generate_scripts(
        url="https://your-app.com",
        username="test_user",
        password="test_pass",
        output_dir="./cross_browser_tests"
    )
    
    # Execute on each browser
    for browser in browsers:
        print(f"Testing on {browser}...")
        browser_results = await runner.execute_scripts(
            scripts_path,
            execution_config={"browser": browser, "headless": True}
        )
        results[browser] = browser_results
    
    await runner.shutdown()
    return results

# Run multi-browser tests
results = asyncio.run(multi_browser_testing())
```

## 📊 Generated Reports

### Performance Report Structure
```json
{
  "session_id": "test_20241203_143022",
  "execution_summary": {
    "start_time": "2024-12-03T14:30:22",
    "end_time": "2024-12-03T14:35:45",
    "duration": "00:05:23",
    "total_tests": 12,
    "passed_tests": 10,
    "failed_tests": 1,
    "skipped_tests": 1,
    "success_rate": 83.3
  },
  "performance_metrics": {
    "page_load_times": {
      "average": 1.85,
      "min": 0.92,
      "max": 3.21,
      "p95": 2.87
    },
    "core_web_vitals": {
      "first_contentful_paint": 1.2,
      "largest_contentful_paint": 2.1,
      "cumulative_layout_shift": 0.08
    }
  }
}
```

## 🚥 CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/playwright-tests.yml
name: AI Playwright Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 */6 * * *'  # Run every 6 hours

jobs:
  playwright-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Setup and run tests
      env:
        TEST_TARGET_URL: ${{ secrets.TEST_TARGET_URL }}
        TEST_USERNAME: ${{ secrets.TEST_USERNAME }}
        TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
      run: |
        python setup.py
        source venv/bin/activate
        python src/simple_runner.py --url $TEST_TARGET_URL --username $TEST_USERNAME --password $TEST_PASSWORD --mode one-line --headless
    
    - name: Upload test reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: reports/
        retention-days: 30
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Virtual Environment Issues
```bash
# If virtual environment creation fails
python -m pip install --upgrade pip
python -m pip install virtualenv
python -m virtualenv venv

# If activation fails on Windows
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Playwright Installation Issues
```bash
# Fix Playwright browser installation
playwright install --force

# Install system dependencies (Linux)
sudo playwright install-deps
```

#### 3. Permission Issues
```bash
# Windows: Run as Administrator if needed
# Linux/macOS: Fix permissions
chmod +x quick_setup.sh
chmod +x venv/bin/activate
```

#### 4. Memory Issues
```python
# Reduce concurrent users for resource-constrained environments
config = {
    "concurrent_users": 1,
    "headless": True,
    "test_duration": 60  # Shorter duration
}
```

### Getting Help
- Check the logs in the `logs/` directory
- Review the `PROJECT_SUMMARY.md` for detailed information
- Run `python quick_start.py` for a working demo
- Examine `usage_examples.py` for more examples

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup
git clone https://github.com/dbbuilder/autoplaytest.git
cd autoplaytest
python setup.py

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black flake8

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Code Quality
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include comprehensive docstrings
- Write unit tests for new features
- Update documentation for API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) for the excellent browser automation framework
- [FastAPI](https://fastapi.tiangolo.com/) for the modern API framework
- [Scikit-learn](https://scikit-learn.org/) for machine learning capabilities
- [TensorFlow](https://tensorflow.org/) for AI pattern recognition

## 📞 Support

- **Repository**: https://github.com/dbbuilder/autoplaytest
- **Issues**: [GitHub Issues](https://github.com/dbbuilder/autoplaytest/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dbbuilder/autoplaytest/discussions)

---

**Made with ❤️ for automated testing and performance monitoring**