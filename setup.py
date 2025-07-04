#!/usr/bin/env python3
"""
Enhanced Setup Script for AI Playwright Testing Engine
Creates virtual environment and installs dependencies with error handling.
"""

import subprocess
import sys
import os
from pathlib import Path
import time


def run_command(command, description, check=True, timeout=300):
    """Run a command with error handling and user feedback."""
    print(f"📦 {description}...")
    try:
        if isinstance(command, str):
            result = subprocess.run(
                command, 
                shell=True, 
                check=check, 
                capture_output=True, 
                text=True,
                timeout=timeout
            )
        else:
            result = subprocess.run(
                command, 
                check=check, 
                capture_output=True, 
                text=True,
                timeout=timeout
            )
        
        if result.stdout:
            # Only show last few lines to avoid spam
            stdout_lines = result.stdout.strip().split('\n')
            if len(stdout_lines) > 3:
                print(f"   ✅ {stdout_lines[-1]}")
            else:
                print(f"   ✅ {result.stdout.strip()}")
        
        return result
        
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Command timed out after {timeout} seconds")
        if not check:
            return None
        raise
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   Details: {e.stderr.strip()}")
        if check:
            return None  # Don't exit, let caller handle
        return None


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required. Current version: {version.major}.{version.minor}")
        print("   Please upgrade Python and try again.")
        print("   Download from: https://python.org/downloads/")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True


def setup_virtual_environment():
    """Create and setup virtual environment with enhanced error handling."""
    project_dir = Path(__file__).parent
    venv_dir = project_dir / "venv"
    
    print(f"🚀 Setting up AI Playwright Testing Engine")
    print(f"📁 Project directory: {project_dir.absolute()}")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create virtual environment
    if venv_dir.exists():
        print(f"📂 Virtual environment already exists at: {venv_dir}")
        try:
            response = input("   Do you want to recreate it? (y/n): ").lower().strip()
        except KeyboardInterrupt:
            print("\n   Keeping existing virtual environment...")
            response = "n"
            
        if response in ['y', 'yes']:
            print("🗑️  Removing existing virtual environment...")
            import shutil
            try:
                shutil.rmtree(venv_dir)
            except Exception as e:
                print(f"   ⚠️  Warning: Could not remove existing venv: {e}")
        else:
            print("   Using existing virtual environment...")
    
    # Create virtual environment if it doesn't exist
    if not venv_dir.exists():
        print("🔨 Creating virtual environment...")
        result = run_command(
            [sys.executable, "-m", "venv", str(venv_dir)], 
            "Creating virtual environment",
            check=False
        )
        if result is None:
            print("❌ Failed to create virtual environment")
            print("💡 Troubleshooting tips:")
            print("   - Try: python -m pip install --upgrade pip")
            print("   - Try: python -m pip install virtualenv")
            print("   - Run as administrator (Windows) or with sudo (Linux/macOS)")
            return False
    
    # Determine paths
    if os.name == 'nt':  # Windows
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"
    
    # Verify virtual environment was created properly
    if not python_exe.exists():
        print(f"❌ Virtual environment creation failed - {python_exe} not found")
        return False
    
    # Upgrade pip in virtual environment
    print("⬆️  Upgrading pip...")
    result = run_command(
        [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], 
        "Upgrading pip",
        check=False
    )
    
    # Install core requirements
    requirements_file = project_dir / "requirements.txt"
    if requirements_file.exists():
        print("📦 Installing core Python dependencies...")
        print("   (This may take a few minutes)")
        
        # Try installing with increased timeout
        result = run_command(
            [str(pip_exe), "install", "-r", str(requirements_file)], 
            "Installing Python dependencies",
            check=False,
            timeout=600  # 10 minutes
        )
        
        if result is None:
            print("⚠️  Core dependencies installation had issues")
            print("🔧 Trying to install essential packages individually...")
            
            # Essential packages that usually work
            essential_packages = [
                "playwright==1.40.0",
                "aiohttp==3.9.1", 
                "fastapi==0.104.1",
                "pydantic==2.5.0",
                "pyyaml==6.0.1",
                "pytest==7.4.3"
            ]
            
            failed_packages = []
            for package in essential_packages:
                print(f"   Installing {package}...")
                result = run_command(
                    [str(pip_exe), "install", package],
                    f"Installing {package}",
                    check=False,
                    timeout=120
                )
                if result is None:
                    failed_packages.append(package)
            
            if failed_packages:
                print(f"⚠️  Some packages failed to install: {failed_packages}")
                print("   You can install them manually later if needed")
    else:
        print("⚠️  requirements.txt not found, skipping dependency installation")
    
    # Install Playwright browsers
    print("🌐 Installing Playwright browsers...")
    print("   (This may take several minutes)")
    
    # Try to install Playwright browsers
    if (venv_dir / ("Scripts" if os.name == 'nt' else "bin") / "playwright").exists():
        playwright_exe = venv_dir / ("Scripts" if os.name == 'nt' else "bin") / "playwright"
        result = run_command(
            [str(playwright_exe), "install"], 
            "Installing Playwright browsers",
            check=False,
            timeout=900  # 15 minutes
        )
        
        if result is None:
            print("⚠️  Playwright browser installation had issues")
            print("   You can install them manually later with:")
            print(f"   {playwright_exe} install")
    else:
        print("⚠️  Playwright not installed, skipping browser installation")
        print("   Install Playwright first: pip install playwright")
    
    # Success message
    print("\n" + "=" * 60)
    print("🎉 Setup completed!")
    print("\n📋 Next steps:")
    
    # Check what was actually installed
    try:
        result = run_command(
            [str(pip_exe), "list"], 
            "Checking installed packages",
            check=False
        )
        if result and "playwright" in result.stdout:
            print("✅ Playwright is installed")
        if result and "fastapi" in result.stdout:
            print("✅ FastAPI is installed")
    except:
        pass
    
    if os.name == 'nt':  # Windows
        print("\n🚀 To run the quick start demo:")
        print(f"   {python_exe} quick_start.py")
        print("\n🔧 To activate virtual environment:")
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("\n🚀 To run the quick start demo:")
        print(f"   {python_exe} quick_start.py")
        print("\n🔧 To activate virtual environment:")
        print("   source venv/bin/activate")
    
    print(f"\n💡 Virtual environment location: {venv_dir.absolute()}")
    
    # Offer to run quick start
    try:
        response = input("\n🎯 Would you like to run the quick start demo now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("\n🚀 Running quick start demo...")
            run_command(
                [str(python_exe), "quick_start.py"],
                "Running quick start demo",
                check=False,
                timeout=300
            )
    except KeyboardInterrupt:
        print("\n   Skipping demo run...")
    
    return True


def main():
    """Main setup function with comprehensive error handling."""
    try:
        success = setup_virtual_environment()
        if not success:
            print("\n❌ Setup encountered issues")
            print("\n🔧 Troubleshooting tips:")
            print("   1. Ensure you have Python 3.9+ installed")
            print("   2. Check your internet connection")
            print("   3. Try running as administrator (Windows) or with sudo (Linux/macOS)")
            print("   4. Update pip: python -m pip install --upgrade pip")
            print("   5. Install setuptools: python -m pip install --upgrade setuptools")
            print("\n📞 For help:")
            print("   - Check README.md for detailed instructions")
            print("   - Visit: https://github.com/dbbuilder/autoplaytest")
            sys.exit(1)
        else:
            print("\n✅ Setup completed successfully!")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {str(e)}")
        print("\n🔧 Please try running the setup again or install manually")
        sys.exit(1)


if __name__ == "__main__":
    main()
