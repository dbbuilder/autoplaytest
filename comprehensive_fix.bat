@echo off
REM File: comprehensive_fix.bat
REM Location: d:\dev2\autoplaytest\comprehensive_fix.bat

echo ========================================
echo Comprehensive Fix for AutoPlayTest
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate

echo Step 1: Updating pip and build tools...
python -m pip install --upgrade pip setuptools wheel

echo.
echo Step 2: Installing compatible NumPy version...
REM Python 3.12 requires NumPy >= 1.26.0
python -m pip install numpy==1.26.4

echo.
echo Step 3: Installing TensorFlow for Python 3.12...
REM TensorFlow 2.16+ supports Python 3.12
python -m pip install tensorflow==2.16.2

echo.
echo Step 4: Reinstalling OpenCV with proper dependencies...
python -m pip uninstall -y opencv-python-headless
python -m pip install opencv-python-headless==4.10.0.84

echo.
echo Step 5: Installing additional compatible packages...
python -m pip install scikit-learn pandas matplotlib

echo.
echo Step 6: Creating test script...
echo Creating test_installation.py...
echo Test script already exists, run it with: python test_installation.py

echo.
echo Fix completed! Test with: python test_installation.py
pause