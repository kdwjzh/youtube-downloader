"""
主入口文件 - 應用程序的起點
"""
import os
import sys
import customtkinter as ctk

from youtube_downloader.gui.main_window import MainWindow
from youtube_downloader.config import APP_NAME, APP_VERSION


def main():
    """主函數"""
    print(f"{APP_NAME} v{APP_VERSION} 啟動中...")
    
    # 設置主題
    ctk.set_appearance_mode("light")  # 設置為淺色主題
    ctk.set_default_color_theme("blue")
    
    # 創建主窗口
    app = MainWindow()
    
    # 運行應用程序
    app.mainloop()


if __name__ == "__main__":
    main()
