@echo off
echo ========================================
echo     Installation Diagnostic Tool
echo ========================================
echo.

:: Check if virtual environment exists
echo [1/5] Checking virtual environment...
if exist venv (
    echo [OK] Virtual environment found
) else (
    echo [ERROR] Virtual environment not found
    echo Please run install.bat first
    pause
    exit /b 1
)

:: Check Python in venv
echo.
echo [2/5] Checking Python in virtual environment...
call venv\Scripts\activate.bat
python --version
if errorlevel 1 (
    echo [ERROR] Python not working in virtual environment
    pause
    exit /b 1
) else (
    echo [OK] Python is working
)

:: Check pip
echo.
echo [3/5] Checking pip...
pip --version
if errorlevel 1 (
    echo [ERROR] pip not working
    pause
    exit /b 1
) else (
    echo [OK] pip is working
)

:: List installed packages
echo.
echo [4/5] Checking installed packages...
echo Installed packages:
pip list | findstr /i "customtkinter yt-dlp pillow requests mutagen moviepy"

:: Test imports
echo.
echo [5/5] Testing module imports...
echo Testing customtkinter...
python -c "import customtkinter; print('customtkinter: OK')" 2>nul
if errorlevel 1 echo [ERROR] customtkinter import failed

echo Testing yt-dlp...
python -c "import yt_dlp; print('yt-dlp: OK')" 2>nul
if errorlevel 1 echo [ERROR] yt-dlp import failed

echo Testing Pillow...
python -c "import PIL; print('Pillow: OK')" 2>nul
if errorlevel 1 echo [ERROR] Pillow import failed

echo Testing requests...
python -c "import requests; print('requests: OK')" 2>nul
if errorlevel 1 echo [ERROR] requests import failed

echo Testing mutagen...
python -c "import mutagen; print('mutagen: OK')" 2>nul
if errorlevel 1 echo [ERROR] mutagen import failed

echo Testing moviepy...
python -c "import moviepy.editor; print('moviepy: OK')" 2>nul
if errorlevel 1 (
    echo [ERROR] moviepy import failed
    echo This is likely the cause of your problem
    echo Try running: pip install moviepy --force-reinstall
)

echo.
echo ========================================
echo         Diagnostic Complete
echo ========================================
echo.
echo If any modules show [ERROR], try:
echo 1. Run install.bat again
echo 2. Or manually install the failing package:
echo    pip install [package-name] --force-reinstall
echo.
pause
