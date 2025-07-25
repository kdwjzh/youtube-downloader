"""
路徑選擇組件 - 用於選擇下載路徑
"""
import os
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

from youtube_downloader.core.utils import get_default_download_path, check_disk_space


class PathSelector(ctk.CTkFrame):
    """路徑選擇組件"""
    
    def __init__(self, master, on_path_change=None, **kwargs):
        """
        初始化路徑選擇組件
        
        Args:
            master: 父組件
            on_path_change (function): 路徑變更回調函數
            **kwargs: 其他參數
        """
        super().__init__(master, **kwargs)
        
        self.on_path_change = on_path_change
        
        # 獲取默認下載路徑
        self.current_path = get_default_download_path()
        
        # 配置網格
        self.grid_columnconfigure(0, weight=0)  # 標籤
        self.grid_columnconfigure(1, weight=1)  # 路徑輸入框
        self.grid_columnconfigure(2, weight=0)  # 選擇按鈕
        
        # 創建標籤
        self.path_label = ctk.CTkLabel(
            self, 
            text="保存路徑",
            font=("Arial", 12)
        )
        self.path_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # 創建路徑輸入框
        self.path_entry = ctk.CTkEntry(
            self,
            height=32,
            font=("Arial", 12)
        )
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.path_entry.insert(0, self.current_path)
        
        # 創建選擇按鈕
        self.select_button = ctk.CTkButton(
            self,
            text="select",
            font=("Arial", 12, "bold"),
            width=80,
            height=32,
            command=self._browse_directory,
            fg_color="#d33a56",
            text_color="white",
            hover_color="#b52e47",
        )
        self.select_button.grid(row=0, column=2, sticky="e")
        
        # 綁定事件
        self.path_entry.bind("<FocusOut>", self._on_path_changed)
    
    def _browse_directory(self):
        """
        瀏覽目錄
        """
        initial_dir = self.current_path if os.path.exists(self.current_path) else os.path.expanduser("~")
        
        directory = filedialog.askdirectory(
            initialdir=initial_dir,
            title="選擇下載目錄"
        )
        
        if directory:  # 如果用戶選擇了目錄
            self.set_path(directory)
    
    def _on_path_changed(self, event):
        """
        路徑變更事件處理函數
        
        Args:
            event: 事件對象
        """
        new_path = self.path_entry.get().strip()
        
        if new_path != self.current_path:
            # 檢查路徑是否有效
            if os.path.exists(new_path) and os.path.isdir(new_path):
                self.current_path = new_path
                
                # 如果有回調函數，則調用
                if self.on_path_change:
                    self.on_path_change(new_path)
            else:
                # 如果路徑無效，則恢復原值
                self.path_entry.delete(0, "end")
                self.path_entry.insert(0, self.current_path)
    
    def get_path(self):
        """
        獲取當前選擇的路徑
        
        Returns:
            str: 當前路徑
        """
        return self.current_path
    
    def set_path(self, path):
        """
        設置路徑
        
        Args:
            path (str): 要設置的路徑
        """
        if os.path.exists(path) and os.path.isdir(path):
            self.current_path = path
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)
            
            # 如果有回調函數，則調用
            if self.on_path_change:
                self.on_path_change(path)
    
    def check_space(self, required_space):
        """
        檢查路徑是否有足夠空間
        
        Args:
            required_space (int): 所需空間大小（字節）
            
        Returns:
            bool: 是否有足夠空間
        """
        return check_disk_space(self.current_path, required_space)
