#!/usr/bin/env python3
"""
Fixed launcher for AI Playwright Testing Engine
This properly handles the import structure issues
"""

import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.absolute()

# Change to project directory
os.chdir(project_root)

# Add BOTH the project root AND src to Python path
# This allows imports to work from both perspectives
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Set PYTHONPATH environment variable as well
os.environ['PYTHONPATH'] = f"{project_root}{os.pathsep}{project_root / 'src'}"

# Import and run
if __name__ == "__main__":
    try:
        # Try importing from src first
        from src.simple_runner import main
    except ImportError:
        # If that fails, try direct import
        from simple_runner import main
    
    import asyncio
    asyncio.run(main())
