#!/usr/bin/env python3
"""
Minimal Setup Script for AI Playwright Testing Engine
Installs only the most essential packages that are most likely to work.
"""

import subprocess
import sys
from pathlib import Path

# Essential packages that usually install without issues
ESSENTIAL_PACKAGES = [
    "playwright>=1.40.0",
    "aiohttp>=3.9.0",
    "fastapi>=0.100.0", 
    "pydantic>=2.0.0",
    "pyyaml>=6.0.0",
    "pytest>=7.0.0"
]

def run_pip_command(args, description):
    """Run a pip command with error handling."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip"] + args,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"   ✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        if e.stderr:
            print(f"   Details: {e.stderr.strip()}")
        return False

def main():
    """Install essential packages only."""
    print("🚀 AI Playwright Testing Engine - Minimal Setup")
    print("===============================================")
    print("Installing only essential packages...")
    print()
    
    # Upgrade pip first
    run_pip_command(["install", "--upgrade", "pip"], "Upgrading pip")
    
    # Install essential packages one by one
    failed_packages = []
    for package in ESSENTIAL_PACKAGES:
        success = run_pip_command(["install", package], f"Installing {package}")
        if not success:
            failed_packages.append(package)
    
    print("\n" + "=" * 50)
    
    if not failed_packages:
        print("✅ All essential packages installed successfully!")
        
        # Try to install Playwright browsers
        print("\n🌐 Installing Playwright browsers...")
        try:
            subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
            print("✅ Playwright browsers installed!")
        except subprocess.CalledProcessError:
            print("⚠️  Playwright browser installation failed")
            print("   You can install them manually later with:")
            print("   python -m playwright install")
        
    else:
        print(f"⚠️  Some packages failed to install: {failed_packages}")
        print("   The basic functionality should still work with installed packages")
    
    print("\n💡 Next steps:")
    print("   python quick_start.py")
    print("   python src/simple_runner.py --help")
    
    if failed_packages:
        print(f"\n🔧 To install failed packages manually:")
        for package in failed_packages:
            print(f"   pip install {package}")

if __name__ == "__main__":
    main()
