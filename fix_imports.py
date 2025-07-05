#!/usr/bin/env python3
"""
Script to fix all relative imports in the AutoPlayTest project
Converts relative imports (with ...) to absolute imports
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix relative imports in a single file."""
    print(f"Processing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match relative imports with triple dots
    # from ...utils.logger import setup_logger -> from utils.logger import setup_logger
    content = re.sub(r'from \.\.\.(\w+)', r'from \1', content)
    
    # Pattern to match relative imports with double dots
    # from ..executor.test_executor import -> from core.executor.test_executor import
    content = re.sub(r'from \.\.(\w+)', r'from core.\1', content)
    
    # Pattern to match single dot imports
    # from .script_generator import -> from core.script_generator import
    if 'core' in str(file_path):
        content = re.sub(r'from \.(\w+)', r'from core.\1', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Fixed imports in {file_path}")
        return True
    return False

def main():
    """Fix all imports in the src directory."""
    src_dir = Path("D:/Dev2/autoplaytest/src")
    
    print("Fixing relative imports in AutoPlayTest project...")
    print("=" * 50)
    
    fixed_files = 0
    total_files = 0
    
    # Process all Python files
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" not in str(py_file):
            total_files += 1
            if fix_imports_in_file(py_file):
                fixed_files += 1
    
    print("=" * 50)
    print(f"Fixed {fixed_files} out of {total_files} files")
    print("\nNext steps:")
    print("1. Test the imports: python src/simple_runner.py --help")
    print("2. Run your command with the standard Python module syntax:")
    print("   python -m src.simple_runner --url http://localhost:5173 --username admin@faithvision.net --password admin123 --mode generate --output-dir ./generated_tests")

if __name__ == "__main__":
    main()
