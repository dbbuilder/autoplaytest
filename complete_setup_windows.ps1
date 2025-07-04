# Complete System Setup for AI Playwright Testing Engine (PowerShell)
# This script installs all necessary build tools and dependencies
# Run this as Administrator: Set-ExecutionPolicy Bypass -Scope Process -Force

param(
    [switch]$SkipChocolatey,
    [switch]$SkipBuildTools,
    [switch]$Force
)

Write-Host "🚀 AI Playwright Testing Engine - Complete System Setup (PowerShell)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️  This script requires Administrator privileges" -ForegroundColor Yellow
    Write-Host "   Please run PowerShell as Administrator and try again" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   1. Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "   2. Run: Set-ExecutionPolicy Bypass -Scope Process -Force" -ForegroundColor Yellow
    Write-Host "   3. Run this script again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

Write-Host "📋 What this script will install:" -ForegroundColor Yellow
Write-Host "   1. Chocolatey package manager" -ForegroundColor White
Write-Host "   2. Python 3.11 (latest stable)" -ForegroundColor White
Write-Host "   3. Visual Studio Build Tools 2022" -ForegroundColor White
Write-Host "   4. CMake and build essentials" -ForegroundColor White
Write-Host "   5. Git version control" -ForegroundColor White
Write-Host "   6. PostgreSQL development libraries" -ForegroundColor White
Write-Host "   7. All Python dependencies including TensorFlow and OpenCV" -ForegroundColor White
Write-Host ""

if (-not $Force) {
    $continue = Read-Host "Continue with installation? (y/n)"
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        Write-Host "Installation cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Function to run commands with error handling
function Invoke-CommandWithLogging {
    param(
        [string]$Description,
        [scriptblock]$Command,
        [switch]$ContinueOnError
    )
    
    Write-Host "📦 $Description..." -ForegroundColor Yellow
    
    try {
        $result = & $Command
        Write-Host "✅ $Description completed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ $Description failed: $($_.Exception.Message)" -ForegroundColor Red
        if (-not $ContinueOnError) {
            throw
        }
        return $false
    }
}

# Function to check if a command exists
function Test-CommandExists {
    param([string]$Command)
    
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

try {
    # Step 1: Install Chocolatey
    if (-not $SkipChocolatey) {
        Write-Host ""
        Write-Host "🍫 Step 1: Installing Chocolatey package manager..." -ForegroundColor Cyan
        
        if (Test-CommandExists "choco") {
            Write-Host "✅ Chocolatey already installed" -ForegroundColor Green
        }
        else {
            Invoke-CommandWithLogging "Installing Chocolatey" {
                Set-ExecutionPolicy Bypass -Scope Process -Force
                [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
                Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
            }
            
            # Refresh environment
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        }
    }

    # Step 2: Install Python
    Write-Host ""
    Write-Host "🐍 Step 2: Installing Python..." -ForegroundColor Cyan
    
    if (Test-CommandExists "python") {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python already installed: $pythonVersion" -ForegroundColor Green
    }
    else {
        Invoke-CommandWithLogging "Installing Python 3.11" {
            choco install python311 -y
        }
        
        # Refresh environment
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
    }

    # Step 3: Install Visual Studio Build Tools
    if (-not $SkipBuildTools) {
        Write-Host ""
        Write-Host "🔨 Step 3: Installing Visual Studio Build Tools..." -ForegroundColor Cyan
        
        $vsInstalled = Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC"
        if ($vsInstalled) {
            Write-Host "✅ Visual Studio Build Tools already installed" -ForegroundColor Green
        }
        else {
            Write-Host "Installing Visual Studio Build Tools 2022..." -ForegroundColor Yellow
            Write-Host "⏰ This may take 10-15 minutes..." -ForegroundColor Yellow
            
            Invoke-CommandWithLogging "Installing Visual Studio Build Tools" {
                choco install visualstudio2022buildtools --package-parameters "--add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK.19041 --add Microsoft.VisualStudio.Component.VC.CMake.Project" -y
            } -ContinueOnError
        }
    }

    # Step 4: Install CMake
    Write-Host ""
    Write-Host "🏗️ Step 4: Installing CMake..." -ForegroundColor Cyan
    
    if (Test-CommandExists "cmake") {
        Write-Host "✅ CMake already installed" -ForegroundColor Green
    }
    else {
        Invoke-CommandWithLogging "Installing CMake" {
            choco install cmake -y
        }
    }

    # Step 5: Install Git
    Write-Host ""
    Write-Host "📁 Step 5: Installing Git..." -ForegroundColor Cyan
    
    if (Test-CommandExists "git") {
        Write-Host "✅ Git already installed" -ForegroundColor Green
    }
    else {
        Invoke-CommandWithLogging "Installing Git" {
            choco install git -y
        }
    }

    # Step 6: Install PostgreSQL
    Write-Host ""
    Write-Host "🐘 Step 6: Installing PostgreSQL..." -ForegroundColor Cyan
    
    Invoke-CommandWithLogging "Installing PostgreSQL development libraries" {
        choco install postgresql14 -y
    } -ContinueOnError

    # Refresh environment variables
    Write-Host ""
    Write-Host "🔄 Refreshing environment variables..." -ForegroundColor Cyan
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")

    # Step 7: Setup Python environment
    Write-Host ""
    Write-Host "🐍 Step 7: Setting up Python environment..." -ForegroundColor Cyan
    
    # Change to script directory
    Set-Location $PSScriptRoot

    # Upgrade pip and setuptools
    Invoke-CommandWithLogging "Upgrading pip and setuptools" {
        python -m pip install --upgrade pip setuptools wheel
    }

    # Create virtual environment
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    if (Test-Path "venv") {
        Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force "venv"
    }

    Invoke-CommandWithLogging "Creating virtual environment" {
        python -m venv venv
    }

    # Activate virtual environment
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"

    # Upgrade pip in virtual environment
    Invoke-CommandWithLogging "Upgrading pip in virtual environment" {
        python -m pip install --upgrade pip setuptools wheel
    }

    # Step 8: Install Python dependencies
    Write-Host ""
    Write-Host "📦 Step 8: Installing complete Python dependencies..." -ForegroundColor Cyan
    Write-Host "⏰ This may take 15-30 minutes depending on your internet speed..." -ForegroundColor Yellow

    # Install build dependencies
    Invoke-CommandWithLogging "Installing build dependencies" {
        pip install --upgrade cython numpy
    }

    # Install TensorFlow
    Write-Host "Installing TensorFlow..." -ForegroundColor Yellow
    $tfSuccess = Invoke-CommandWithLogging "Installing TensorFlow 2.15.0" {
        pip install tensorflow==2.15.0
    } -ContinueOnError
    
    if (-not $tfSuccess) {
        Write-Host "⚠️  TensorFlow 2.15.0 failed, trying CPU version..." -ForegroundColor Yellow
        Invoke-CommandWithLogging "Installing TensorFlow CPU" {
            pip install tensorflow-cpu==2.15.0
        } -ContinueOnError
    }

    # Install OpenCV
    Write-Host "Installing OpenCV..." -ForegroundColor Yellow
    $cvSuccess = Invoke-CommandWithLogging "Installing OpenCV" {
        pip install opencv-python==4.8.1.78
    } -ContinueOnError
    
    if (-not $cvSuccess) {
        Write-Host "⚠️  OpenCV with GUI failed, trying headless version..." -ForegroundColor Yellow
        Invoke-CommandWithLogging "Installing OpenCV headless" {
            pip install opencv-python-headless==4.8.1.78
        } -ContinueOnError
    }

    # Install PostgreSQL adapter
    Write-Host "Installing PostgreSQL adapter..." -ForegroundColor Yellow
    $pgSuccess = Invoke-CommandWithLogging "Installing psycopg2-binary" {
        pip install psycopg2-binary==2.9.9
    } -ContinueOnError
    
    if (-not $pgSuccess) {
        Write-Host "⚠️  psycopg2-binary failed, trying source version..." -ForegroundColor Yellow
        Invoke-CommandWithLogging "Installing psycopg2" {
            pip install psycopg2==2.9.9
        } -ContinueOnError
    }

    # Install remaining dependencies
    Invoke-CommandWithLogging "Installing remaining dependencies" {
        pip install -r requirements-complete.txt
    } -ContinueOnError

    # Install Playwright browsers
    Invoke-CommandWithLogging "Installing Playwright browsers" {
        playwright install
    }

    # Step 9: Test installation
    Write-Host ""
    Write-Host "🎯 Step 9: Testing installation..." -ForegroundColor Cyan

    $packages = @{
        "TensorFlow" = "import tensorflow; print('✅ TensorFlow:', tensorflow.__version__)"
        "OpenCV" = "import cv2; print('✅ OpenCV:', cv2.__version__)"
        "psycopg2" = "import psycopg2; print('✅ psycopg2:', psycopg2.__version__)"
        "Playwright" = "import playwright; print('✅ Playwright available')"
        "scikit-learn" = "import sklearn; print('✅ scikit-learn:', sklearn.__version__)"
        "pandas" = "import pandas; print('✅ pandas:', pandas.__version__)"
    }

    foreach ($package in $packages.Keys) {
        try {
            $result = python -c $packages[$package] 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host $result -ForegroundColor Green
            } else {
                Write-Host "⚠️  $package not available" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "⚠️  $package not available" -ForegroundColor Yellow
        }
    }

    # Success message
    Write-Host ""
    Write-Host "🎉 Complete system setup finished!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Summary:" -ForegroundColor Cyan
    Write-Host "   ✅ Build tools installed" -ForegroundColor Green
    Write-Host "   ✅ Python environment configured" -ForegroundColor Green
    Write-Host "   ✅ Virtual environment created" -ForegroundColor Green
    Write-Host "   ✅ All dependencies installed" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 You can now run the full AI Playwright Testing Engine:" -ForegroundColor Cyan
    Write-Host "   .\venv\Scripts\python.exe quick_start.py" -ForegroundColor White
    Write-Host "   .\venv\Scripts\python.exe src\simple_runner.py --help" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 To activate the virtual environment manually:" -ForegroundColor Cyan
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "❌ Setup encountered an error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "   1. Ensure you're running PowerShell as Administrator" -ForegroundColor White
    Write-Host "   2. Set execution policy: Set-ExecutionPolicy Bypass -Scope Process -Force" -ForegroundColor White
    Write-Host "   3. Check your internet connection" -ForegroundColor White
    Write-Host "   4. Temporarily disable antivirus software" -ForegroundColor White
    Write-Host "   5. Try running with -SkipBuildTools if Visual Studio installation fails" -ForegroundColor White
    Write-Host ""
    Write-Host "📞 For help: https://github.com/dbbuilder/autoplaytest/issues" -ForegroundColor White
    exit 1
}

Write-Host "Press Enter to continue..." -ForegroundColor Yellow
Read-Host
