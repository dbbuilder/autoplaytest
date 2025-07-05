#!/usr/bin/env python3
"""
Launcher for AI Playwright Testing Engine Simple Runner
Properly sets up paths for imports
"""

import sys
from pathlib import Path

# Add the src directory to the Python path (same as quick_start.py)
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Now import and run main from simple_runner
from simple_runner import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
