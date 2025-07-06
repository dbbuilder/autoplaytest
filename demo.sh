#!/bin/bash

# AutoPlayTest Demo Runner for Unix/Linux/macOS

echo "========================================"
echo "   AutoPlayTest Demo Runner"
echo "========================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo -e "${RED}[ERROR] Virtual environment not found!${NC}"
    echo "Please run setup.py first:"
    echo "   python setup.py"
    echo
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[WARNING] No .env file found!${NC}"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo
    echo "Please edit .env and add your API keys for full functionality."
    echo "The demo will run in mock mode without API keys."
    echo
    read -p "Press Enter to continue..."
fi

# Run the demo
python demo.py "$@"

# Deactivate virtual environment
deactivate

echo
echo "Demo completed!"