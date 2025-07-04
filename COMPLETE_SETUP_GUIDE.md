# 🛠️ Complete System Setup Guide

## 🎯 **Full Feature Installation with All Dependencies**

This guide provides **comprehensive system setup scripts** that install all necessary build tools, compilers, and system dependencies to support the **complete AI Playwright Testing Engine** with all features including TensorFlow, OpenCV, and advanced ML capabilities.

## 🚀 **Quick Start (Complete Setup)**

### **Windows Users**

#### **Option 1: Batch Script (Recommended)**
```cmd
# Download and run (as Administrator)
cd d:\dev2\autoplaytest
complete_setup_windows.bat
```

#### **Option 2: PowerShell Script**
```powershell
# Run PowerShell as Administrator, then:
Set-ExecutionPolicy Bypass -Scope Process -Force
cd d:\dev2\autoplaytest
.\complete_setup_windows.ps1
```

### **Linux/macOS Users**
```bash
cd /path/to/autoplaytest
chmod +x complete_setup_unix.sh
sudo ./complete_setup_unix.sh
```

## 📦 **What Gets Installed**

### **🔧 System Tools and Compilers**

#### **Windows:**
- **Chocolatey** - Package manager for Windows
- **Python 3.11** - Latest stable Python
- **Visual Studio Build Tools 2022** - C++ compiler and build tools
- **CMake** - Cross-platform build system
- **Git** - Version control system
- **PostgreSQL** - Database with development libraries

#### **Linux (Ubuntu/Debian):**
- **build-essential** - GCC, G++, Make
- **python3-dev** - Python development headers
- **cmake** - Build system
- **libopencv-dev** - OpenCV development libraries
- **libpq-dev** - PostgreSQL development libraries
- **Additional libraries** - GTK, FFmpeg, image processing libs

#### **Linux (CentOS/RHEL/Fedora):**
- **Development Tools** group
- **python3-devel** - Python development packages
- **cmake** - Build system
- **opencv-devel** - OpenCV development packages
- **postgresql-devel** - PostgreSQL development libraries

#### **macOS:**
- **Xcode Command Line Tools** - Apple's development tools
- **Homebrew** - Package manager for macOS
- **Python 3.11** - Via Homebrew
- **CMake** - Build system
- **OpenCV** - Computer vision library
- **PostgreSQL** - Database system

### **🐍 Python Packages (Complete Set)**

All packages from `requirements-complete.txt`:

#### **Core Functionality:**
- `playwright==1.40.0` - Web automation
- `aiohttp==3.9.1` - Async HTTP client
- `fastapi==0.104.1` - Web framework
- `pydantic==2.5.0` - Data validation
- `sqlalchemy==2.0.23` - Database ORM

#### **AI/ML Packages:**
- `tensorflow==2.15.0` - Machine learning framework
- `scikit-learn==1.3.2` - Machine learning tools
- `numpy==1.24.3` - Numerical computing
- `pandas==2.0.3` - Data analysis

#### **Computer Vision:**
- `opencv-python==4.8.1.78` - Computer vision library

#### **Database Support:**
- `psycopg2-binary==2.9.9` - PostgreSQL adapter
- `alembic==1.13.1` - Database migrations

#### **Visualization:**
- `matplotlib==3.7.2` - Plotting library
- `plotly==5.17.0` - Interactive visualizations

#### **Distributed Processing:**
- `celery==5.3.4` - Task queue
- `redis==5.0.1` - In-memory data store

#### **Additional Tools:**
- `selenium==4.15.2` - Alternative web automation
- `beautifulsoup4==4.12.2` - HTML parsing
- `pytest==7.4.3` - Testing framework

## 🎯 **Features Enabled by Complete Setup**

### **✅ AI-Powered Capabilities**
- **TensorFlow Integration** - Deep learning models for pattern recognition
- **Computer Vision** - Screenshot analysis, visual regression detection
- **Machine Learning** - Predictive test failure analysis
- **Natural Language Processing** - Test description to script conversion

### **✅ Advanced Monitoring**
- **Performance Profiling** - Detailed metrics with ML analysis
- **Visual Regression** - AI-powered screenshot comparison
- **Anomaly Detection** - Statistical models for performance issues
- **Predictive Analytics** - Forecast performance trends

### **✅ Enterprise Features**
- **Database Integration** - Full PostgreSQL support for large-scale data
- **Distributed Testing** - Celery-based task distribution
- **Advanced Reporting** - Interactive Plotly visualizations
- **Cross-Browser Analysis** - Selenium fallback support

### **✅ Developer Tools**
- **Code Generation** - AI-assisted test script creation
- **Smart Selectors** - ML-optimized element detection
- **Test Optimization** - Automated test case prioritization
- **Coverage Analysis** - Advanced test coverage metrics

## 🔧 **System Requirements**

### **Minimum Requirements:**
- **OS**: Windows 10+, Ubuntu 18.04+, macOS 10.15+
- **RAM**: 8GB (16GB recommended for ML features)
- **Disk Space**: 10GB free space
- **Internet**: Stable connection for downloads

### **Recommended Requirements:**
- **OS**: Windows 11, Ubuntu 20.04+, macOS 12+
- **RAM**: 16GB+ (for TensorFlow and computer vision)
- **Disk Space**: 20GB+ free space
- **CPU**: Multi-core processor (for parallel processing)
- **GPU**: CUDA-compatible GPU (optional, for TensorFlow acceleration)

## ⚡ **Installation Time Estimates**

| Component | Windows | Linux | macOS |
|-----------|---------|-------|-------|
| System Tools | 10-15 min | 5-10 min | 10-15 min |
| Python Packages | 15-30 min | 10-20 min | 15-25 min |
| Playwright Browsers | 5-10 min | 5-10 min | 5-10 min |
| **Total** | **30-55 min** | **20-40 min** | **30-50 min** |

*Times vary based on internet speed and system performance*

## 🚀 **Usage After Complete Setup**

### **Full Feature Testing:**
```bash
# Activate virtual environment
# Windows: .\venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# Run with all features enabled
python src/simple_runner.py \
  --url https://your-app.com \
  --username your_user \
  --password your_pass \
  --mode one-line \
  --test-types login navigation forms search ai-analysis \
  --enable-ml-features \
  --enable-cv-analysis \
  --browser chromium \
  --concurrent-users 3 \
  --test-duration 600
```

### **AI-Enhanced Script Generation:**
```python
from src.simple_runner import SimpleRunner

runner = SimpleRunner()

# Generate scripts with AI analysis
scripts_path = await runner.generate_scripts(
    url="https://your-app.com",
    username="user",
    password="pass",
    ai_enhanced=True,           # ✅ Enabled with complete setup
    computer_vision=True,       # ✅ Enabled with OpenCV
    ml_optimization=True,       # ✅ Enabled with TensorFlow
    advanced_analytics=True     # ✅ Enabled with full stack
)
```

## 🎯 **Verification Commands**

After complete setup, verify all components:

```bash
# Test core packages
python -c "import tensorflow; print('✅ TensorFlow:', tensorflow.__version__)"
python -c "import cv2; print('✅ OpenCV:', cv2.__version__)"
python -c "import psycopg2; print('✅ PostgreSQL:', psycopg2.__version__)"
python -c "import sklearn; print('✅ scikit-learn:', sklearn.__version__)"
python -c "import plotly; print('✅ Plotly:', plotly.__version__)"

# Test AI features
python -c "import tensorflow as tf; print('✅ TensorFlow GPU:', tf.config.list_physical_devices('GPU'))"

# Test the full application
python quick_start.py
```

## 🔧 **Troubleshooting Complete Setup**

### **Common Issues:**

#### **Windows: "Visual Studio not found"**
```cmd
# Manual installation
choco install visualstudio2022buildtools -y
# Or download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

#### **Linux: "cmake not found"**
```bash
# Ubuntu/Debian
sudo apt-get install cmake

# CentOS/RHEL
sudo yum install cmake
```

#### **macOS: "Xcode not installed"**
```bash
xcode-select --install
# Follow the GUI installation prompts
```

#### **All Platforms: "TensorFlow installation failed"**
```bash
# Try CPU-only version
pip install tensorflow-cpu==2.15.0

# Or specific version
pip install tensorflow==2.13.0
```

### **Fallback Options:**

If complete setup fails, you can still use advanced features by installing packages individually:

```bash
# Essential + some advanced features
pip install playwright aiohttp fastapi pydantic
pip install numpy pandas matplotlib
pip install scikit-learn
playwright install

# Add TensorFlow later
pip install tensorflow-cpu

# Add OpenCV later  
pip install opencv-python-headless
```

## 🎉 **Benefits of Complete Setup**

### **🚀 Performance Benefits:**
- **Faster script generation** with AI assistance
- **Smarter element detection** using computer vision
- **Predictive failure analysis** with machine learning
- **Advanced performance insights** with statistical analysis

### **🎯 Feature Benefits:**
- **Visual regression testing** with AI comparison
- **Natural language test generation** from requirements
- **Automated test optimization** and prioritization
- **Enterprise-grade reporting** with interactive dashboards

### **🛡️ Reliability Benefits:**
- **Self-healing test scripts** that adapt to UI changes
- **Anomaly detection** for performance issues
- **Predictive maintenance** for test suites
- **Advanced error classification** and resolution suggestions

**The complete setup unlocks the full potential of the AI Playwright Testing Engine!** 🚀
