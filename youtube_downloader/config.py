"""
配置文件 - 包含應用程序配置
"""
import os
from pathlib import Path

# 應用程序版本
APP_VERSION = "1.0.0"

# 應用程序名稱
APP_NAME = "YouTube Downloader"

# 應用程序目錄
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 資源目錄
ASSETS_DIR = os.path.join(APP_DIR, "assets")

# 默認縮圖
DEFAULT_THUMBNAIL = os.path.join(ASSETS_DIR, "default_thumbnail.png")

# 默認下載目錄
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

# 默認設置
DEFAULT_SETTINGS = {
    "format": "mp3",
    "mp3_quality": "320kbps",
    "mp4_quality": "720p",
    "download_dir": DEFAULT_DOWNLOAD_DIR,
    "embed_thumbnail": False,
    "theme": "light"
}

# 確保資源目錄存在
Path(ASSETS_DIR).mkdir(parents=True, exist_ok=True)
