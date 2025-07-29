@echo off
echo ========================================
echo    MoviePy Version Fix (Force 1.0.3)
echo ========================================
echo.

echo This script will fix the MoviePy version compatibility issue
echo by installing the specific version 1.0.3 that works with this app.
echo.

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Check current moviepy version
echo.
echo Checking current MoviePy version...
pip show moviepy 2>nul
if errorlevel 1 (
    echo MoviePy not installed
) else (
    echo Current version found above
)

:: Uninstall any existing moviepy
echo.
echo [1/3] Removing any existing MoviePy installation...
pip uninstall moviepy -y

:: Clean up any conflicting packages
echo.
echo [2/3] Cleaning up potential conflicts...
pip uninstall imageio imageio-ffmpeg -y
pip install imageio==2.25.1
pip install imageio-ffmpeg==0.4.9

:: Install specific moviepy version
echo.
echo [3/3] Installing MoviePy 1.0.3 (compatible version)...
pip install moviepy==1.0.3 --no-cache-dir

:: Verify installation
echo.
echo Testing MoviePy 1.0.3 installation...
python -c "import moviepy; print(f'MoviePy version: {moviepy.__version__}')"
python -c "import moviepy.editor; print('MoviePy editor import: SUCCESS')"

if errorlevel 1 (
    echo.
    echo [ERROR] MoviePy 1.0.3 installation failed
    echo.
    echo Additional troubleshooting steps:
    echo 1. Make sure you have Visual C++ Redistributable installed
    echo 2. Try running this script as administrator
    echo 3. Check if antivirus is blocking the installation
    echo.
) else (
    echo.
    echo [SUCCESS] MoviePy 1.0.3 is now working correctly!
    echo You can now run the application with run_app.bat
    echo.
)

pause
