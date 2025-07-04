#!/usr/bin/env python3
"""
Setup Script for AI Playwright Testing Engine
Creates virtual environment and installs all dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description, check=True):
    """Run a command with error handling and user feedback."""
    print(f"📦 {description}...")
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=check, capture_output=True, text=True)
        
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   Details: {e.stderr.strip()}")
        if check:
            sys.exit(1)
        return None


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required. Current version: {version.major}.{version.minor}")
        print("   Please upgrade Python and try again.")
        sys.exit(1)
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")


def setup_virtual_environment():
    """Create and setup virtual environment."""
    project_dir = Path(__file__).parent
    venv_dir = project_dir / "venv"
    
    print(f"🚀 Setting up AI Playwright Testing Engine")
    print(f"📁 Project directory: {project_dir.absolute()}")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    if venv_dir.exists():
        print(f"📂 Virtual environment already exists at: {venv_dir}")
        response = input("   Do you want to recreate it? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("🗑️  Removing existing virtual environment...")
            import shutil
            shutil.rmtree(venv_dir)
        else:
            print("   Using existing virtual environment...")
    
    if not venv_dir.exists():
        run_command([sys.executable, "-m", "venv", str(venv_dir)], "Creating virtual environment")
    
    # Determine activation script path
    if os.name == 'nt':  # Windows
        activate_script = venv_dir / "Scripts" / "activate.bat"
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        activate_script = venv_dir / "bin" / "activate"
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"
    
    # Upgrade pip in virtual environment
    run_command([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip")
    
    # Install requirements
    requirements_file = project_dir / "requirements.txt"
    if requirements_file.exists():
        run_command([str(pip_exe), "install", "-r", str(requirements_file)], "Installing Python dependencies")
    else:
        print("⚠️  requirements.txt not found, skipping dependency installation")
    
    # Install Playwright browsers
    playwright_exe = venv_dir / ("Scripts" if os.name == 'nt' else "bin") / "playwright"
    run_command([str(playwright_exe), "install"], "Installing Playwright browsers")
    
    # Success message
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    
    if os.name == 'nt':  # Windows
        print("   1. Activate virtual environment:")
        print(f"      .\\venv\\Scripts\\activate")
        print("   2. Run the quick start demo:")
        print("      python quick_start.py")
        print("   3. When done, deactivate:")
        print("      deactivate")
    else:  # Unix/Linux/macOS
        print("   1. Activate virtual environment:")
        print(f"      source venv/bin/activate")
        print("   2. Run the quick start demo:")
        print("      python quick_start.py")
        print("   3. When done, deactivate:")
        print("      deactivate")
    
    print(f"\n💡 Tip: The virtual environment is located at: {venv_dir.absolute()}")
    print("💡 You can also run tests directly without activating:")
    if os.name == 'nt':
        print(f"   .\\venv\\Scripts\\python.exe quick_start.py")
    else:
        print(f"   ./venv/bin/python quick_start.py")


def main():
    """Main setup function."""
    try:
        setup_virtual_environment()
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("   - Ensure you have Python 3.9+ installed")
        print("   - Check your internet connection")
        print("   - Try running as administrator (Windows) or with sudo (Linux/macOS)")
        print("   - Ensure you have sufficient disk space")
        sys.exit(1)


if __name__ == "__main__":
    main()
