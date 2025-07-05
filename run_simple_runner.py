# Run Simple Runner Script
# File: run_simple_runner.py
# Location: d:\dev2\autoplaytest\run_simple_runner.py

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Now import and run the simple runner
from src.simple_runner import main

if __name__ == "__main__":
    # Pass command line arguments to the main function
    sys.argv[0] = 'simple_runner.py'  # Replace script name
    main()