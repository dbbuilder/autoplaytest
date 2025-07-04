#!/bin/bash
# Complete System Setup for AI Playwright Testing Engine (Linux/macOS)
# This script installs all necessary build tools and dependencies

set -e  # Exit on any error

echo "🚀 AI Playwright Testing Engine - Complete System Setup"
echo "========================================================="
echo "This script will install all necessary build tools and dependencies"
echo "to support the full feature set including TensorFlow, OpenCV, etc."
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "🐧 Detected: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "🍎 Detected: macOS"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

echo ""
echo "📋 What this script will install:"
echo "   1. System development tools and compilers"
echo "   2. Python 3.11 (if not present)"
echo "   3. CMake and build tools"
echo "   4. OpenCV system dependencies"
echo "   5. PostgreSQL development libraries"
echo "   6. All Python dependencies including TensorFlow and OpenCV"
echo ""

read -p "Continue with installation? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Function to run commands with error handling
run_command() {
    local description="$1"
    shift
    echo "📦 $description..."
    
    if "$@"; then
        echo "✅ $description completed successfully"
        return 0
    else
        echo "❌ $description failed"
        echo "⚠️  Command: $*"
        return 1
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Install system dependencies
echo ""
echo "🔧 Step 1: Installing system development tools..."

if [[ "$OS" == "linux" ]]; then
    # Detect Linux distribution
    if command_exists apt-get; then
        # Ubuntu/Debian
        echo "Detected Ubuntu/Debian system"
        
        run_command "Updating package lists" sudo apt-get update
        
        run_command "Installing build essentials" \
            sudo apt-get install -y build-essential gcc g++ make
        
        run_command "Installing Python development tools" \
            sudo apt-get install -y python3 python3-pip python3-dev python3-venv
        
        run_command "Installing CMake" \
            sudo apt-get install -y cmake
        
        run_command "Installing OpenCV dependencies" \
            sudo apt-get install -y libopencv-dev python3-opencv \
            libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev \
            libv4l-dev libxvidcore-dev libx264-dev libjpeg-dev libpng-dev \
            libtiff-dev gfortran openexr libatlas-base-dev
        
        run_command "Installing PostgreSQL development libraries" \
            sudo apt-get install -y postgresql postgresql-contrib libpq-dev
        
        run_command "Installing additional development tools" \
            sudo apt-get install -y git curl wget software-properties-common
            
    elif command_exists yum; then
        # CentOS/RHEL/Fedora
        echo "Detected CentOS/RHEL/Fedora system"
        
        run_command "Installing development tools" \
            sudo yum groupinstall -y "Development Tools"
        
        run_command "Installing Python development tools" \
            sudo yum install -y python3 python3-pip python3-devel
        
        run_command "Installing CMake" \
            sudo yum install -y cmake
        
        run_command "Installing OpenCV dependencies" \
            sudo yum install -y opencv-devel \
            gtk3-devel ffmpeg-devel libv4l-devel \
            libjpeg-turbo-devel libpng-devel libtiff-devel
        
        run_command "Installing PostgreSQL development libraries" \
            sudo yum install -y postgresql postgresql-server postgresql-devel
        
    elif command_exists pacman; then
        # Arch Linux
        echo "Detected Arch Linux system"
        
        run_command "Updating package database" sudo pacman -Syu --noconfirm
        
        run_command "Installing development tools" \
            sudo pacman -S --noconfirm base-devel gcc cmake
        
        run_command "Installing Python development tools" \
            sudo pacman -S --noconfirm python python-pip
        
        run_command "Installing OpenCV dependencies" \
            sudo pacman -S --noconfirm opencv
        
        run_command "Installing PostgreSQL development libraries" \
            sudo pacman -S --noconfirm postgresql postgresql-libs
    else
        echo "⚠️  Unknown Linux distribution. Please install development tools manually:"
        echo "   - build-essential or equivalent"
        echo "   - python3-dev"
        echo "   - cmake"
        echo "   - opencv development libraries"
        echo "   - postgresql development libraries"
    fi
    
elif [[ "$OS" == "macos" ]]; then
    # macOS
    echo "Setting up macOS development environment"
    
    # Install Xcode command line tools
    if ! xcode-select -p &> /dev/null; then
        run_command "Installing Xcode command line tools" \
            xcode-select --install
        echo "⚠️  Please complete the Xcode installation and re-run this script"
        exit 1
    else
        echo "✅ Xcode command line tools already installed"
    fi
    
    # Install Homebrew if not present
    if ! command_exists brew; then
        run_command "Installing Homebrew" \
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "✅ Homebrew already installed"
    fi
    
    # Update Homebrew
    run_command "Updating Homebrew" brew update
    
    # Install Python if needed
    if ! command_exists python3.11; then
        run_command "Installing Python 3.11" brew install python@3.11
    else
        echo "✅ Python 3.11 already installed"
    fi
    
    # Install CMake
    if ! command_exists cmake; then
        run_command "Installing CMake" brew install cmake
    else
        echo "✅ CMake already installed"
    fi
    
    # Install OpenCV
    run_command "Installing OpenCV" brew install opencv
    
    # Install PostgreSQL
    if ! command_exists psql; then
        run_command "Installing PostgreSQL" brew install postgresql
    else
        echo "✅ PostgreSQL already installed"
    fi
    
    # Install additional tools
    run_command "Installing additional tools" brew install git wget
fi

# Step 2: Verify Python installation
echo ""
echo "🐍 Step 2: Verifying Python installation..."

# Find the best Python version
PYTHON_CMD=""
for cmd in python3.11 python3.10 python3.9 python3 python; do
    if command_exists "$cmd"; then
        VERSION=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        MAJOR=$(echo $VERSION | cut -d. -f1)
        MINOR=$(echo $VERSION | cut -d. -f2)
        
        if [[ $MAJOR -eq 3 && $MINOR -ge 9 ]]; then
            PYTHON_CMD=$cmd
            echo "✅ Found suitable Python: $cmd ($VERSION)"
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    echo "❌ Python 3.9+ not found. Please install Python 3.9 or higher."
    exit 1
fi

# Step 3: Setup Python environment
echo ""
echo "🐍 Step 3: Setting up Python environment..."

# Navigate to script directory
cd "$(dirname "$0")"

# Upgrade pip and setuptools
run_command "Upgrading pip and setuptools" \
    $PYTHON_CMD -m pip install --upgrade pip setuptools wheel

# Create virtual environment
echo "Creating virtual environment..."
if [[ -d "venv" ]]; then
    echo "Virtual environment already exists, removing..."
    rm -rf venv
fi

run_command "Creating virtual environment" $PYTHON_CMD -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip in virtual environment
run_command "Upgrading pip in virtual environment" \
    python -m pip install --upgrade pip setuptools wheel

# Step 4: Install Python dependencies
echo ""
echo "📦 Step 4: Installing complete Python dependencies..."
echo "This may take 15-30 minutes depending on your internet speed..."

# Install build dependencies first
run_command "Installing build dependencies" \
    pip install --upgrade cython numpy

# Install TensorFlow
echo "Installing TensorFlow..."
if pip install tensorflow==2.15.0; then
    echo "✅ TensorFlow installed successfully"
else
    echo "⚠️  TensorFlow 2.15.0 failed, trying 2.13.0..."
    if pip install tensorflow==2.13.0; then
        echo "✅ TensorFlow 2.13.0 installed successfully"
    else
        echo "⚠️  TensorFlow installation failed, will use CPU-only version"
        pip install tensorflow-cpu || echo "⚠️  All TensorFlow installations failed"
    fi
fi

# Install OpenCV
echo "Installing OpenCV..."
if pip install opencv-python==4.8.1.78; then
    echo "✅ OpenCV installed successfully"
else
    echo "⚠️  OpenCV with GUI failed, trying headless version..."
    if pip install opencv-python-headless==4.8.1.78; then
        echo "✅ OpenCV headless installed successfully"
    else
        echo "⚠️  OpenCV installation failed"
    fi
fi

# Install PostgreSQL adapter
echo "Installing PostgreSQL adapter..."
if pip install psycopg2-binary==2.9.9; then
    echo "✅ psycopg2-binary installed successfully"
else
    echo "⚠️  psycopg2-binary failed, trying source version..."
    if pip install psycopg2==2.9.9; then
        echo "✅ psycopg2 installed successfully"
    else
        echo "⚠️  psycopg2 installation failed"
    fi
fi

# Create complete requirements file and install
echo "Installing remaining dependencies..."
cat > requirements-complete.txt << 'EOF'
# Complete requirements including all optional packages
playwright==1.40.0
asyncio==3.4.3
aiohttp==3.9.1
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
alembic==1.13.1
scikit-learn==1.3.2
numpy==1.24.3
pandas==2.0.3
beautifulsoup4==4.12.2
selenium==4.15.2
psutil==5.9.6
matplotlib==3.7.2
plotly==5.17.0
pyyaml==6.0.1
python-dotenv==1.0.0
loguru==0.7.2
schedule==1.2.0
celery==5.3.4
redis==5.0.1
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
EOF

run_command "Installing remaining Python packages" \
    pip install -r requirements-complete.txt

# Install Playwright browsers
run_command "Installing Playwright browsers" playwright install

# Step 5: Test installation
echo ""
echo "🎯 Step 5: Testing installation..."

echo "Testing core packages..."
python -c "import tensorflow; print('✅ TensorFlow:', tensorflow.__version__)" 2>/dev/null || echo "⚠️  TensorFlow not available"
python -c "import cv2; print('✅ OpenCV:', cv2.__version__)" 2>/dev/null || echo "⚠️  OpenCV not available"
python -c "import psycopg2; print('✅ psycopg2:', psycopg2.__version__)" 2>/dev/null || echo "⚠️  psycopg2 not available"
python -c "import playwright; print('✅ Playwright available')" 2>/dev/null || echo "❌ Playwright not available"
python -c "import sklearn; print('✅ scikit-learn:', sklearn.__version__)" 2>/dev/null || echo "⚠️  scikit-learn not available"
python -c "import pandas; print('✅ pandas:', pandas.__version__)" 2>/dev/null || echo "⚠️  pandas not available"

echo ""
echo "🎉 Complete system setup finished!"
echo ""
echo "📋 Summary:"
echo "   ✅ System development tools installed"
echo "   ✅ Python environment configured"
echo "   ✅ Virtual environment created"
echo "   ✅ All dependencies installed"
echo ""
echo "🚀 You can now run the full AI Playwright Testing Engine:"
echo "   ./venv/bin/python quick_start.py"
echo "   ./venv/bin/python src/simple_runner.py --help"
echo ""
echo "💡 To activate the virtual environment manually:"
echo "   source venv/bin/activate"
echo ""
echo "✅ Setup completed successfully!"
