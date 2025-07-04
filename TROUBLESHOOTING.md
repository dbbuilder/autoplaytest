# 🔧 Troubleshooting Guide

## Installation Issues

### ❌ Error: "Cannot import 'setuptools.build_meta'"

This error typically occurs when setuptools is outdated or missing.

**Solution:**
```bash
# Upgrade pip and setuptools first
python -m pip install --upgrade pip setuptools wheel

# Then try setup again
python setup.py
```

### ❌ Error: "Microsoft Visual C++ 14.0 is required" (Windows)

Some packages require compilation tools on Windows.

**Solutions:**
1. **Install Visual Studio Build Tools** (Recommended):
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Install "C++ build tools" workload

2. **Use Minimal Setup** (Faster):
   ```bash
   python minimal_setup.py
   ```

3. **Skip problematic packages**:
   - Use the simplified requirements.txt (already updated)
   - Install optional packages later as needed

### ❌ Error: "Package installation timed out"

Network or server issues can cause timeouts.

**Solutions:**
```bash
# Increase timeout
pip install --timeout 300 -r requirements.txt

# Use different index
pip install -i https://pypi.org/simple/ -r requirements.txt

# Try minimal setup
python minimal_setup.py
```

### ❌ Error: "Permission denied" (Linux/macOS)

Permission issues when installing packages.

**Solutions:**
```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or install with user flag
pip install --user -r requirements.txt
```

### ❌ Error: "Command 'playwright' not found"

Playwright wasn't installed correctly.

**Solutions:**
```bash
# Install Playwright explicitly
pip install playwright

# Install browsers
python -m playwright install

# If still fails, try
playwright install chromium
```

## Quick Fixes

### 🚀 Method 1: Minimal Setup (Fastest)
```bash
cd autoplaytest
python minimal_setup.py
python quick_start.py
```

### 🚀 Method 2: Manual Virtual Environment
```bash
cd autoplaytest
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install --upgrade pip setuptools
pip install playwright aiohttp fastapi pydantic pyyaml pytest
playwright install
python quick_start.py
```

### 🚀 Method 3: Essential Only
```bash
cd autoplaytest
pip install playwright fastapi pyyaml
playwright install chromium
python quick_start.py
```

## Common Platform Issues

### Windows Specific
- **Run as Administrator** if you get permission errors
- **Install Visual Studio Build Tools** for packages that need compilation
- **Check Windows Defender** - may block some operations
- **Use PowerShell or Command Prompt** (not Git Bash) for setup

### Linux Specific
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install python3-pip python3-venv python3-dev build-essential

# Install system dependencies (CentOS/RHEL)
sudo yum install python3-pip python3-devel gcc gcc-c++
```

### macOS Specific
```bash
# Install Xcode command line tools
xcode-select --install

# Or install via Homebrew
brew install python
```

## Testing Your Installation

### Quick Test
```bash
# Test basic functionality
python -c "import asyncio; print('✅ Python async works')"
python -c "import playwright; print('✅ Playwright works')"
python -c "import yaml; print('✅ YAML works')"
```

### Run Demo
```bash
# Test the actual application
python quick_start.py
```

### Manual Test
```bash
# Test one-line execution
python src/simple_runner.py --url https://demo.playwright.dev/todomvc --username demo --password demo --mode one-line --headless --test-duration 30
```

## Still Having Issues?

### Get Help
1. **Check Python Version**: Must be 3.9 or higher
   ```bash
   python --version
   ```

2. **Check Internet Connection**: Some packages are large
   ```bash
   ping pypi.org
   ```

3. **Check Disk Space**: Playwright browsers need ~1GB
   ```bash
   # Windows: dir
   # Linux/macOS: df -h
   ```

4. **Report Issues**: 
   - GitHub Issues: https://github.com/dbbuilder/autoplaytest/issues
   - Include your Python version, OS, and error message

### Emergency Fallback
If all else fails, you can run basic tests without full installation:

```bash
# Install only Playwright
pip install playwright
playwright install chromium

# Create a simple test
cat > test.py << 'EOF'
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://example.com")
        title = await page.title()
        print(f"Page title: {title}")
        await browser.close()

asyncio.run(main())
EOF

python test.py
```

This verifies that basic Playwright functionality works on your system.
