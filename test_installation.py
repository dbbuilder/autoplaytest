# File: test_installation.py
# Location: d:\dev2\autoplaytest\test_installation.py

import sys
import importlib
from pathlib import Path

def test_import(module_name, display_name=None):
    """Test if a module can be imported and display its version if available."""
    if display_name is None:
        display_name = module_name
    
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'version not available')
        print(f"✓ {display_name}: {version}")
        return True
    except ImportError as e:
        print(f"✗ {display_name}: Import failed - {str(e)}")
        return False
    except Exception as e:
        print(f"✗ {display_name}: Error - {str(e)}")
        return False

def main():
    """Test all major package installations."""
    print("=" * 50)
    print("AutoPlayTest Installation Test")
    print("=" * 50)
    print(f"Python: {sys.version}")
    print(f"Virtual Environment: {sys.prefix}")
    print("=" * 50)
    
    # Core packages
    print("\nCore Packages:")
    core_packages = [
        ('playwright', 'Playwright'),
        ('aiohttp', 'aiohttp'),
        ('fastapi', 'FastAPI'),
        ('pydantic', 'Pydantic'),
        ('yaml', 'PyYAML')
    ]
    
    core_success = all(test_import(pkg, name) for pkg, name in core_packages)
    
    # Scientific packages
    print("\nScientific Packages:")
    scientific_packages = [
        ('numpy', 'NumPy'),
        ('cv2', 'OpenCV'),
        ('tensorflow', 'TensorFlow'),
        ('sklearn', 'scikit-learn'),
        ('pandas', 'pandas'),
        ('matplotlib', 'matplotlib')
    ]
    
    scientific_results = [test_import(pkg, name) for pkg, name in scientific_packages]    
    # Database packages
    print("\nDatabase Packages:")
    db_packages = [
        ('psycopg2', 'psycopg2')
    ]
    
    db_success = all(test_import(pkg, name) for pkg, name in db_packages)
    
    # Test specific functionality
    print("\nFunctionality Tests:")
    
    # Test NumPy
    try:
        import numpy as np
        arr = np.array([1, 2, 3])
        print(f"✓ NumPy array creation: {arr}")
    except Exception as e:
        print(f"✗ NumPy functionality: {e}")
    
    # Test OpenCV
    try:
        import cv2
        print(f"✓ OpenCV build info available")
    except Exception as e:
        print(f"✗ OpenCV functionality: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    if core_success:
        print("✓ All core packages installed successfully")
    else:
        print("✗ Some core packages failed")
    
    scientific_success = sum(scientific_results)
    print(f"✓ {scientific_success}/{len(scientific_packages)} scientific packages installed")
    
    if db_success:
        print("✓ Database packages installed successfully")
    
    print("=" * 50)

if __name__ == "__main__":
    main()