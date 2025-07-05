#!/usr/bin/env python
"""
Runner wrapper for AutoPlayTest
This script properly sets up the Python path and runs the simple_runner
"""

import sys
import os
from pathlib import Path

# Add the project root and src to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Change to project directory
os.chdir(project_root)

# Now we can import and run
from src.simple_runner import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
