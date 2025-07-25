"""
URL 輸入組件 - 處理 YouTube URL 的輸入和驗證
"""
import customtkinter as ctk
import re

from youtube_downloader.core.utils import validate_youtube_url


class URLInput(ctk.CTkFrame):
    """URL 輸入組件"""
    
    def __init__(self, master, on_url_change=None, on_url_submit=None, **kwargs):
        """
        初始化 URL 輸入組件
        
        Args:
            master: 父組件
            on_url_change (function): URL 變更回調函數
            on_url_submit (function): URL 提交回調函數
            **kwargs: 其他參數
        """
        super().__init__(master, **kwargs)
        
        self.on_url_change = on_url_change
        self.on_url_submit = on_url_submit
        
        # 配置網格
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        
        # 創建 URL 輸入框
        self.url_entry = ctk.CTkEntry(
            self, 
            placeholder_text="貼上 YouTube 網址 (Paste youtube link here...)",
            height=36,
            font=("Arial", 12)
        )
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # 創建清除按鈕
        self.paste_button = ctk.CTkButton(
            self, 
            text="Paste",
            font=("Arial", 12, "bold"),
            width=100,
            height=36,
            fg_color="#d33a56",
            text_color="white",
            hover_color="#b52e47",
            command=self._paste_from_clipboard
        )
        self.paste_button.grid(row=0, column=1, sticky="e")
        
        # 綁定事件
        self.url_entry.bind("<KeyRelease>", self._on_url_changed)
        self.url_entry.bind("<Return>", self._on_url_submit)
        
        # 用於追蹤上一次輸入的 URL
        self._last_url = ""
    
    def _on_url_changed(self, event):
        """
        URL 變更事件處理函數
        
        Args:
            event: 事件對象
        """
        current_url = self.url_entry.get().strip()
        
        # 檢查 URL 是否有實際變化
        if current_url != self._last_url:
            self._last_url = current_url
            
            # 檢查 URL 是否有效
            is_valid = validate_youtube_url(current_url) if current_url else False
            
            # 如果有回調函數，則調用
            if self.on_url_change:
                self.on_url_change(current_url, is_valid)
    
    def _on_url_submit(self, event):
        """
        URL 提交事件處理函數
        
        Args:
            event: 事件對象
        """
        current_url = self.url_entry.get().strip()
        
        # 檢查 URL 是否有效
        is_valid = validate_youtube_url(current_url) if current_url else False
        
        if is_valid and self.on_url_submit:
            self.on_url_submit(current_url)
    
    def _paste_from_clipboard(self):
        """
        從剪貼板粘貼 URL
        """
        # 獲取剪貼板內容
        try:
            clipboard_content = self.clipboard_get().strip()
            
            # 檢查是否是有效的 YouTube URL
            if validate_youtube_url(clipboard_content):
                self.url_entry.delete(0, "end")
                self.url_entry.insert(0, clipboard_content)
                
                # 觸發 URL 變更事件
                if self.on_url_change:
                    self.on_url_change(clipboard_content, True)
                    
                # 觸發 URL 提交事件
                if self.on_url_submit:
                    self.on_url_submit(clipboard_content)
                    
        except Exception:
            # 如果無法訪問剪貼板，則忽略
            pass
    
    def get_url(self):
        """
        獲取當前 URL
        
        Returns:
            str: 當前 URL
        """
        return self.url_entry.get().strip()
    
    def set_url(self, url):
        """
        設置 URL
        
        Args:
            url (str): 要設置的 URL
        """
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, url)
        self._last_url = url
        
    def clear(self):
        """
        清除 URL
        """
        self.url_entry.delete(0, "end")
        self._last_url = ""
