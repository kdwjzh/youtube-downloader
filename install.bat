@echo off
echo ========================================
echo     YouTube Downloader - Auto Installer
echo ========================================
echo.

:: Check if Python is installed
echo [1/4] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher first
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python is installed

:: Create virtual environment
echo.
echo [2/4] Creating virtual environment...
if exist venv (
    echo [OK] Virtual environment already exists
) else (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created successfully
)

:: Activate virtual environment and install dependencies
echo.
echo [3/4] Installing dependencies...
echo Installing required Python packages, please wait...
call venv\Scripts\activate.bat

echo Upgrading pip...
pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing...
)

echo Installing basic dependencies...
pip install --upgrade setuptools wheel
if errorlevel 1 (
    echo WARNING: Failed to install setuptools/wheel, continuing...
)

echo Installing packages from requirements.txt...
pip install -r requirements.txt --verbose
if errorlevel 1 (
    echo ERROR: Failed to install some dependencies
    echo Trying to install critical packages individually...
    
    echo Installing customtkinter...
    pip install customtkinter>=5.2.0
    
    echo Installing yt-dlp...
    pip install yt-dlp>=2023.7.6
    
    echo Installing Pillow...
    pip install Pillow>=10.0.0
    
    echo Installing requests...
    pip install requests>=2.31.0
    
    echo Installing mutagen...
    pip install mutagen>=1.47.0
    
    echo Installing moviepy (this may take a while)...
    pip install moviepy>=1.0.3
    
    if errorlevel 1 (
        echo ERROR: Critical packages installation failed
        echo Please check your internet connection
        pause
        exit /b 1
    )
)

echo.
echo Verifying installation...
echo Testing critical imports...
python -c "import customtkinter; print('customtkinter: OK')"
python -c "import yt_dlp; print('yt-dlp: OK')"
python -c "import PIL; print('Pillow: OK')"
python -c "import requests; print('requests: OK')"
python -c "import mutagen; print('mutagen: OK')"
python -c "import moviepy.editor; print('moviepy: OK')"

if errorlevel 1 (
    echo WARNING: Some modules failed to import
    echo The application may not work correctly
    echo Please check the error messages above
    pause
) else (
    echo [OK] All dependencies verified successfully
)

:: Check FFmpeg
echo.
echo [4/4] Checking FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg not found
    echo FFmpeg is used for audio/video processing
    echo Download: https://ffmpeg.org/download.html
    echo.
    echo You can continue without it, but some features may be limited
) else (
    echo [OK] FFmpeg is installed
)

:: Installation complete
echo.
echo ========================================
echo         Installation Complete!
echo ========================================
echo.
echo How to use:
echo   1. Double-click run_app.bat to start the program
echo   2. Or run in command line: run_app.bat
echo.
echo If you have issues, please check:
echo   - Python version is 3.8 or higher
echo   - Internet connection is working
echo   - requirements.txt file exists
echo.
pause
