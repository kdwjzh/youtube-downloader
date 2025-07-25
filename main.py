"""
YouTube 下載器應用程序的入口點
"""
import os
import sys
import platform

# 將專案目錄添加到模塊搜索路徑中
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# 導入主模塊
from youtube_downloader.main import main

if __name__ == "__main__":
    main()
