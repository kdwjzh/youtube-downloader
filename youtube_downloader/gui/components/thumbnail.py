"""
縮圖顯示組件 - 顯示 YouTube 影片縮圖
"""
import os
import threading
import time
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
import io
import traceback
import yt_dlp

from youtube_downloader.core.video_info import VideoInfoExtractor
from youtube_downloader.core.utils import validate_youtube_url


class ThumbnailViewer(ctk.CTkFrame):
    """縮圖顯示組件 - 直接使用 yt-dlp 獲取縮圖"""
    
    def __init__(self, master, width=480, height=270, **kwargs):
        """
        初始化縮圖顯示組件
        
        Args:
            master: 父組件
            width (int): 縮圖寬度
            height (int): 縮圖高度
            **kwargs: 其他參數
        """
        super().__init__(master, width=width, height=height, **kwargs)
        
        self.width = width
        self.height = height
        
        # 創建單一一個簡單的標籤顯示縮圖
        self.image_label = ctk.CTkLabel(
            self, 
            text="👆👆👆 請貼上 YouTube URL 👆👆👆\n\n這裡會顯示該URL影片縮圖~~~",
            font=("Arial", 14, "bold"),
            width=width,
            height=height
        )
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 維護圖像引用
        self.current_image = None
        
        # 追蹤當前 URL 和狀態
        self.current_url = None
        self.loading_thread = None
        self.is_loading = False
        
        # 記錄累計要求計數以追蹤問題
        self.request_count = 0
    
    def _show_loading_text(self):
        """顯示正在加載的文字 - 重建標籤"""
        # 銷毀現有標籤並創建新標籤
        if hasattr(self, 'image_label'):
            self.image_label.destroy()
            
        self.image_label = ctk.CTkLabel(
            self, 
            text="正在加載縮圖...",
            font=("Arial", 14, "bold"),
            width=self.width,
            height=self.height
        )
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
        
    def _show_default_text(self):
        """顯示預設文字 - 重建標籤"""
        # 銷毀現有標籤並創建新標籤
        if hasattr(self, 'image_label'):
            self.image_label.destroy()
            
        self.image_label = ctk.CTkLabel(
            self, 
            text="顯示該URL影片縮圖",
            font=("Arial", 14, "bold"),
            width=self.width,
            height=self.height
        )
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def _show_error_text(self):
        """顯示錯誤文字 - 重建標籤"""
        # 銷毀現有標籤並創建新標籤
        if hasattr(self, 'image_label'):
            self.image_label.destroy()
            
        self.image_label = ctk.CTkLabel(
            self, 
            text="無法加載縮圖",
            font=("Arial", 14, "bold"),
            text_color="#FF5555",
            width=self.width,
            height=self.height
        )
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def _display_image(self, img):
        """
        顯示圖像 - 重建標籤以避免圖像問題
        
        Args:
            img (PIL.Image.Image): PIL 圖像對象
        """
        try:
            # 調整圖像大小
            if img.width != self.width or img.height != self.height:
                img = img.resize((self.width, self.height), Image.LANCZOS)
                
            # 創建新的標籤替換現有標籤
            # 這是最关鍵的解決方案 - 完全清除舊標籤並創建新的
            if hasattr(self, 'image_label'):
                self.image_label.destroy()  # 先銷毀舊標籤
                
            # 創建全新的 CTkImage
            self.current_image = ctk.CTkImage(light_image=img, dark_image=img, size=(self.width, self.height))
            
            # 創建全新的標籤
            self.image_label = ctk.CTkLabel(
                self, 
                text="",
                image=self.current_image,
                width=self.width,
                height=self.height
            )
            self.image_label.place(relx=0.5, rely=0.5, anchor="center")
            
            # 記錄成功顯示
            print(f"縮圖已成功顯示，寬度: {img.width}, 高度: {img.height}")
        except Exception as e:
            print(f"顯示圖像錯誤: {e}")
            traceback.print_exc()  # 列印詳細的堆疊跟蹤
            self._show_error_text()
    
    def _get_youtube_thumbnail(self, url):
        """
        直接使用 yt-dlp 獲取 YouTube 縮圖
        
        Args:
            url (str): YouTube URL
            
        Returns:
            PIL.Image 或 None: 縮圖圖像
        """
        try:
            print(f"獲取縮圖: {url}")
            # 檢查 URL 是否有效
            if not validate_youtube_url(url):
                print("URL 無效")
                return None
                
            # 直接使用 yt-dlp 獲取信息
            ydl_opts = {
                'quiet': True, 
                'no_warnings': True,
                'skip_download': True,
                'format': 'best',  # 添加格式選項以避免格式不可用錯誤
                'ignoreerrors': True,  # 忽略錯誤以獲取基本信息
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 提取信息
                info = ydl.extract_info(url, download=False)
                
                # 取得縮圖 URL
                if 'thumbnail' in info:
                    thumbnail_url = info['thumbnail']
                    print(f"找到縮圖 URL: {thumbnail_url}")
                    
                    # 下載縮圖
                    response = requests.get(thumbnail_url, timeout=10)
                    if response.status_code == 200:
                        img = Image.open(io.BytesIO(response.content))
                        return img
            
            return None
        except Exception as e:
            print(f"獲取縮圖失敗: {e}")
            traceback.print_exc()
            return None
    
    def show_url(self, url):
        """
        顯示 URL 縮圖
        
        Args:
            url (str): YouTube URL
        """
        # 如果 URL 為空或者未變化，則不做任何操作
        if not url or url == self.current_url:
            return
        
        # 記錄新的要求
        self.request_count += 1
        current_request = self.request_count
        print(f"縮圖要求 #{current_request}: {url}")
        
        # 更新當前 URL
        self.current_url = url
        
        # 停止之前的加載線程（如果存在）
        if self.loading_thread and self.loading_thread.is_alive():
            self.is_loading = False
            try:
                self.loading_thread.join(0.1)  # 結束之前的線程
            except:
                pass
        
        # 顯示正在加載的文字
        self._show_loading_text()
        
        # 啟動新的線程直接加載縮圖
        self.is_loading = True
        
        def thumbnail_thread():
            try:
                # 確保要求仍然是最新的
                if current_request != self.request_count:
                    print(f"要求 #{current_request} 已過期，目前要求為 #{self.request_count}")
                    return
                    
                # 直接獲取 YouTube 縮圖
                img = self._get_youtube_thumbnail(url)
                
                # 確保要求仍然是最新的
                if current_request != self.request_count:
                    print(f"要求 #{current_request} 已過期，目前要求為 #{self.request_count}")
                    return
                    
                if img and self.is_loading:
                    # 在主線程中更新圖像
                    self.after(0, lambda img=img: self._display_image(img))
                else:
                    # 如果無法加載縮圖
                    self.after(0, self._show_error_text)
            except Exception as e:
                print(f"縮圖線程錯誤: {e}")
                traceback.print_exc()
                if self.is_loading:
                    self.after(0, self._show_error_text)
            finally:
                self.is_loading = False
        
        # 啟動新線程
        self.loading_thread = threading.Thread(target=thumbnail_thread)
        self.loading_thread.daemon = True
        self.loading_thread.start()
    
    def load_thumbnail_for_url(self, url):
        """
        為指定 URL 加載縮圖 (公開方法)
        
        Args:
            url (str): YouTube URL
        """
        self.show_url(url)
    
    def clear(self):
        """
        清除縮圖 (公開方法)
        """
        self.current_url = None
        self.current_image = None
        self._show_default_text()
