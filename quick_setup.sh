#!/bin/bash
# Setup and Quick Start Script for AI Playwright Testing Engine (Unix/Linux/macOS)

echo "🚀 AI Playwright Testing Engine - Quick Setup"
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9+ and try again"
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ $(echo "$python_version < 3.9" | bc -l) -eq 1 ]]; then
    echo "❌ Python 3.9+ required. Current version: $python_version"
    echo "Please upgrade Python and try again"
    exit 1
fi

# Run the setup script
echo "📦 Running setup script..."
python3 setup.py

if [ $? -ne 0 ]; then
    echo "❌ Setup failed"
    exit 1
fi

echo ""
echo "🎯 Would you like to run the quick start demo now? (y/n)"
read -p "> " choice

if [[ $choice =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Running quick start demo..."
    ./venv/bin/python quick_start.py
else
    echo ""
    echo "💡 To run the demo later, use:"
    echo "   source venv/bin/activate"
    echo "   python quick_start.py"
fi

echo ""
echo "✅ All done!"
