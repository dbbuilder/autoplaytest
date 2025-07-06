# AutoPlayTest Quick Start Guide

Get up and running with AutoPlayTest in 5 minutes!

## 🚀 Installation

### Option 1: Quick Setup (Recommended)

```bash
git clone https://github.com/dbbuilder/autoplaytest.git
cd autoplaytest
python setup.py
```

### Option 2: Manual Setup

```bash
git clone https://github.com/dbbuilder/autoplaytest.git
cd autoplaytest

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

## 🔑 Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add at least one AI provider key:
```env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
# OR
OPENAI_API_KEY=sk-your-key-here
# OR
GOOGLE_API_KEY=AIza-your-key-here
```

## 🎯 Your First Test

### Simple Example
```bash
python src/simple_runner.py --url https://example.com --mode one-line
```

### With Authentication
```bash
python src/simple_runner.py \
  --url https://app.example.com \
  --username demo@example.com \
  --password demopass \
  --mode one-line
```

### Generate Tests Only
```bash
python src/simple_runner.py \
  --url https://example.com \
  --mode generate \
  --output-dir ./my_tests
```

## 📊 Understanding the Output

After running tests, you'll see:

```
🚀 Starting AI-powered test generation...
📍 Analyzing: https://example.com
🤖 Using AI Provider: Claude
📝 Generating test suite...

Generated Tests:
✅ test_homepage_loads_successfully
✅ test_navigation_menu_works
✅ test_search_functionality
✅ test_responsive_design

🎭 Executing tests with Playwright...

Test Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 4/4 tests passed
⏱️  Total duration: 15.3s
📸 Screenshots saved to: reports/screenshots/
📊 Full report: reports/test_report.html
```

## 🎯 Common Use Cases

### 1. Test Login Flow
```bash
python src/simple_runner.py \
  --url https://app.example.com/login \
  --username test@example.com \
  --password testpass \
  --test-types login \
  --mode one-line
```

### 2. Test E-commerce Site
```bash
python src/simple_runner.py \
  --url https://shop.example.com \
  --test-types navigation search cart checkout \
  --mode one-line
```

### 3. Accessibility Testing
```bash
python src/simple_runner.py \
  --url https://example.com \
  --test-types accessibility \
  --mode one-line
```

### 4. Performance Testing
```bash
python src/simple_runner.py \
  --url https://example.com \
  --test-types performance \
  --mode one-line
```

## 🔧 Advanced Options

### Specify AI Provider
```bash
python src/simple_runner.py \
  --url https://example.com \
  --ai-provider gpt \
  --mode one-line
```

### Use Different Browser
```bash
python src/simple_runner.py \
  --url https://example.com \
  --browser firefox \
  --mode one-line
```

### Run in Headed Mode (See Browser)
```bash
python src/simple_runner.py \
  --url https://example.com \
  --no-headless \
  --mode one-line
```

### Custom Timeout
```bash
python src/simple_runner.py \
  --url https://example.com \
  --timeout 60000 \
  --mode one-line
```

## 📁 Output Files

After running tests, check these locations:

- `reports/` - Test execution reports
- `reports/screenshots/` - Screenshots from test runs
- `reports/test_report.html` - Detailed HTML report
- `logs/` - Application logs
- `generated_tests/` - Generated test scripts (if using generate mode)

## 🐛 Troubleshooting

### "No API key found"
- Make sure you've created `.env` file
- Check that API key is correctly set
- Verify environment variables are loaded

### "Playwright not installed"
```bash
playwright install chromium
```

### "Import error"
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### "Timeout error"
- Increase timeout: `--timeout 60000`
- Check if target site is accessible
- Try with `--no-headless` to see what's happening

## 📚 Next Steps

1. **Explore Test Types**: Try different test types like `forms`, `api`, `e2e`
2. **CI/CD Integration**: Set up automated testing in your pipeline
3. **Custom Configuration**: Edit `config/config.yaml` for advanced settings
4. **Deploy to Cloud**: See [DEPLOYMENT.md](DEPLOYMENT.md) for AWS Lambda setup

## 💡 Tips

- Start with `--mode generate` to review tests before running
- Use `--test-types` to focus on specific functionality
- Add `--no-headless` to watch tests execute
- Check `reports/test_report.html` for detailed results

## 🆘 Getting Help

- 📖 Full Documentation: [README.md](README.md)
- 🐛 Report Issues: [GitHub Issues](https://github.com/dbbuilder/autoplaytest/issues)
- 💬 Community: [Discord Server](https://discord.gg/autoplaytest)

Happy Testing! 🎉