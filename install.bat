@echo off
echo ========================================
echo     YouTube 下載器 - 自動安裝腳本
echo ========================================
echo.

:: 檢查 Python 是否已安裝
echo [1/4] 檢查 Python 環境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 未找到 Python！
    echo 請先安裝 Python 3.8 或更高版本
    echo 下載地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python 已安裝

:: 創建虛擬環境
echo.
echo [2/4] 創建虛擬環境...
if exist venv (
    echo ✓ 虛擬環境已存在
) else (
    echo 正在創建虛擬環境...
    python -m venv venv
    if errorlevel 1 (
        echo 錯誤: 無法創建虛擬環境
        pause
        exit /b 1
    )
    echo ✓ 虛擬環境創建成功
)

:: 激活虛擬環境並安裝依賴
echo.
echo [3/4] 安裝依賴包...
echo 正在安裝所需的 Python 包，請稍候...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo 錯誤: 依賴包安裝失敗
    echo 請檢查網絡連接或 requirements.txt 文件
    pause
    exit /b 1
)
echo ✓ 依賴包安裝完成

:: 檢查 FFmpeg
echo.
echo [4/4] 檢查 FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠ 警告: 未找到 FFmpeg
    echo FFmpeg 用於音頻/視頻處理，建議安裝以獲得最佳體驗
    echo 下載地址: https://ffmpeg.org/download.html
    echo.
    echo 您也可以繼續使用，部分功能可能受限
) else (
    echo ✓ FFmpeg 已安裝
)

:: 安裝完成
echo.
echo ========================================
echo           安裝完成！
echo ========================================
echo.
echo 使用方法:
echo   1. 雙擊 run_app.bat 啟動程序
echo   2. 或者在命令行中運行: run_app.bat
echo.
echo 如有問題，請檢查:
echo   - Python 版本是否為 3.8+
echo   - 網絡連接是否正常
echo   - requirements.txt 文件是否存在
echo.
pause
