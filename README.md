matplotlib==3.7.2
plotly==5.17.0
opencv-python==4.8.1.78
pyyaml==6.0.1
python-dotenv==1.0.0
loguru==0.7.2
pytest==7.4.3
pytest-asyncio==0.21.1
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
    print(f"Performance score: {results['performance_score']}")
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
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        playwright install
    
    - name: Run AI Playwright Tests
      env:
        TEST_TARGET_URL: ${{ secrets.TEST_TARGET_URL }}
        TEST_USERNAME: ${{ secrets.TEST_USERNAME }}
        TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
      run: |
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

#### 1. Playwright Installation Issues
```bash
# Fix Playwright browser installation
playwright install --force

# Install system dependencies (Linux)
sudo playwright install-deps
```

#### 2. Permission Issues
```bash
# Fix file permissions
chmod +x scripts/*.py
sudo chown -R $USER:$GROUP ai-playwright-engine/
```

#### 3. Memory Issues
```python
# Reduce concurrent users for resource-constrained environments
config = {
    "concurrent_users": 1,
    "headless": True,
    "disable_gpu": True,
    "disable_dev_shm_usage": True
}
```

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

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

- Documentation: [Read the full docs](docs/)
- Issues: [GitHub Issues](https://github.com/your-repo/issues)
- Discussions: [GitHub Discussions](https://github.com/your-repo/discussions)
- Email: support@your-domain.com

---

**Made with ❤️ for automated testing and performance monitoring**