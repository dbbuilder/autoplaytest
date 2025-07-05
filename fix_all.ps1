# File: fix_all.ps1
# Location: d:\dev2\autoplaytest\fix_all.ps1

Write-Host "AutoPlayTest Complete Fix Script" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Host "Warning: Not running as administrator. Some fixes may fail." -ForegroundColor Yellow
}

# Set execution policy for current process
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# Navigate to project directory
Set-Location "D:\Dev2\autoplaytest"

# Remove existing venv if it exists
if (Test-Path "venv") {
    Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Path "venv" -Recurse -Force
}

# Create new virtual environment
Write-Host "Creating new virtual environment..." -ForegroundColor Green
python -m venv venv
# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip setuptools wheel

# Install packages in order of dependency
Write-Host "Installing packages..." -ForegroundColor Green

# Core packages first
python -m pip install playwright==1.40.0
python -m pip install aiohttp==3.9.1
python -m pip install fastapi==0.104.1
python -m pip install pydantic==2.5.0
python -m pip install pyyaml==6.0.1

# Database
python -m pip install psycopg2-binary==2.9.9

# Scientific packages (Python 3.12 compatible)
python -m pip install numpy==1.26.4
python -m pip install opencv-python-headless==4.10.0.84
python -m pip install tensorflow==2.17.0  # Latest stable for Python 3.12
python -m pip install scikit-learn pandas matplotlib

# Install Playwright browsers
Write-Host "Installing Playwright browsers..." -ForegroundColor Green
playwright install chromium firefox
# Run tests
Write-Host "Running installation tests..." -ForegroundColor Green
python test_installation.py

Write-Host "`nFix completed!" -ForegroundColor Green
Write-Host "To activate the environment, run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow