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
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection or requirements.txt file
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully

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
