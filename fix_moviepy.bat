@echo off
echo ========================================
echo       MoviePy Installation Fix
echo ========================================
echo.

:: Check FFmpeg first
echo Checking FFmpeg availability...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg not found in system PATH
    echo MoviePy will use imageio-ffmpeg as fallback
    echo For better performance, consider installing FFmpeg:
    echo https://ffmpeg.org/download.html
    echo.
) else (
    echo [OK] FFmpeg is available
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Uninstall and reinstall moviepy
echo.
echo [1/3] Uninstalling existing moviepy...
pip uninstall moviepy -y

echo.
echo [2/3] Installing moviepy dependencies...
pip install imageio imageio-ffmpeg
pip install numpy decorator tqdm requests proglog

echo.
echo [3/3] Installing moviepy...
pip install moviepy --no-cache-dir --force-reinstall

:: Test the installation
echo.
echo Testing moviepy installation...
python -c "import moviepy.editor; print('MoviePy installation successful!')"
if errorlevel 1 (
    echo.
    echo [ERROR] MoviePy still not working
    echo.
    echo Possible solutions:
    echo 1. Check your internet connection
    echo 2. Try installing Visual C++ Redistributable
    echo 3. Update Python to the latest version
    echo 4. Try running as administrator
    echo.
) else (
    echo.
    echo [SUCCESS] MoviePy is now working correctly!
    echo You can now run the application with run_app.bat
    echo.
)

pause
