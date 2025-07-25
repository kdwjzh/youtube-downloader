"""
歷史記錄窗口 - 顯示下載歷史
"""
import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import webbrowser
import subprocess

from youtube_downloader.core.history import DownloadHistory


class HistoryWindow(ctk.CTkToplevel):
    """歷史記錄窗口類"""
    
    def __init__(self, master=None, on_redownload=None):
        """
        初始化歷史記錄窗口
        
        Args:
            master: 父窗口
            on_redownload (function): 重新下載回調函數
        """
        super().__init__(master)
        
        # 設置窗口標題和大小
        self.title("下載歷史")
        self.geometry("800x600")
        self.minsize(800, 600)
        
        # 回調函數
        self.on_redownload = on_redownload
        
        # 初始化歷史記錄管理器
        self.history = DownloadHistory()
        
        # 創建界面組件
        self._create_widgets()
        
        # 加載歷史記錄
        self._load_history_records()
        
        # 設置窗口為模態
        self.transient(master)
        self.grab_set()
        
        # 設置窗口關閉事件
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_widgets(self):
        """創建界面組件"""
        # 創建標題標籤
        self.title_label = ctk.CTkLabel(
            self, 
            text="下載歷史記錄",
            font=("Arial", 18, "bold")
        )
        self.title_label.pack(pady=(20, 10))
        
        # 創建滾動框架
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            width=650,
            height=400
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 創建底部按鈕框架
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # 創建清除歷史按鈕
        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="清除所有歷史",
            command=self._clear_history,
            fg_color="#d33a56",
            text_color="white",
            hover_color="#b52e47",
            font=("Arial", 12, "bold")
        )
        self.clear_button.pack(side="left", padx=5)
        
        # 創建關閉按鈕
        self.close_button = ctk.CTkButton(
            self.button_frame,
            text="關閉",
            command=self._on_close,
            font=("Arial", 12, "bold")
        )
        self.close_button.pack(side="right", padx=5)
        
        # 保存歷史記錄項目的引用
        self.history_items = []
    
    def _load_history_records(self):
        """加載歷史記錄"""
        # 清除現有項目
        for widget in self.history_items:
            widget.destroy()
        self.history_items = []
        
        # 獲取歷史記錄
        records = self.history.get_records(limit=50)
        
        if not records:
            # 創建無記錄提示
            no_record_label = ctk.CTkLabel(
                self.scroll_frame,
                text="尚無下載記錄",
                font=("Arial", 14, "bold"),
                anchor="center"
            )
            no_record_label.pack(pady=50)
            self.history_items.append(no_record_label)
            return
            
        # 創建歷史記錄項目
        for record in records:
            item_frame = self._create_history_item(record)
            item_frame.pack(fill="x", padx=5, pady=5)
            self.history_items.append(item_frame)
    
    def _create_history_item(self, record):
        """
        創建歷史記錄項目
        
        Args:
            record (dict): 歷史記錄數據
            
        Returns:
            CTkFrame: 歷史記錄項目框架
        """
        # 創建項目框架
        item_frame = ctk.CTkFrame(self.scroll_frame)
        item_frame.columnconfigure(1, weight=1)
        
        # 標題
        title = record.get("title", "未知標題")
        title_label = ctk.CTkLabel(
            item_frame,
            text=title,
            font=("Arial", 12, "bold"),
            anchor="w",
            wraplength=400
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
        
        # 下載信息
        format_type = record.get("format", "").upper()
        quality = record.get("quality", "")
        time_str = record.get("download_time", "")
        
        info_text = f"格式: {format_type} | 品質: {quality} | 下載時間: {time_str}"
        info_label = ctk.CTkLabel(
            item_frame,
            text=info_text,
            font=("Arial", 10),
            anchor="w"
        )
        info_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 5))
        
        # 文件路徑
        path = record.get("file_path", "")
        if path and os.path.exists(path):
            path_state = "存在"
        else:
            path_state = "文件不存在"
            
        path_label = ctk.CTkLabel(
            item_frame,
            text=f"路徑: {path} ({path_state})",
            font=("Arial", 10),
            anchor="w",
            text_color="gray"
        )
        path_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 5))
        
        # 按鈕框架
        button_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, columnspan=2, sticky="e", padx=10, pady=(0, 10))
        
        # 重新下載按鈕
        redownload_button = ctk.CTkButton(
            button_frame,
            text="重新下載",
            width=100,
            height=25,
            command=lambda r=record: self._redownload_item(r),
            font=("Arial", 12, "bold")
        )
        redownload_button.pack(side="right", padx=5)
        
        # 打開文件位置按鈕
        if path and os.path.exists(path):
            open_folder_button = ctk.CTkButton(
                button_frame,
                text="打開文件位置",
                width=120,
                height=25,
                command=lambda p=path: self._open_file_location(p),
                font=("Arial", 12, "bold")
            )
            open_folder_button.pack(side="right", padx=5)
        
        # 在網頁中打開按鈕
        if record.get("url"):
            open_url_button = ctk.CTkButton(
                button_frame,
                text="在網頁中打開",
                width=120,
                height=25,
                command=lambda u=record.get("url"): self._open_in_browser(u),
                font=("Arial", 12, "bold")
            )
            open_url_button.pack(side="right", padx=5)
            
        return item_frame
    
    def _redownload_item(self, record):
        """
        重新下載項目
        
        Args:
            record (dict): 歷史記錄數據
        """
        if self.on_redownload:
            self.on_redownload(record.get("url"))
            self._on_close()
    
    def _open_file_location(self, file_path):
        """
        打開文件位置
        
        Args:
            file_path (str): 文件路徑
        """
        if os.path.exists(file_path):
            # 獲取文件所在的目錄
            directory = os.path.dirname(file_path)
            
            # 根據操作系統打開目錄
            if os.name == 'nt':  # Windows
                os.startfile(directory)
            elif os.name == 'posix':  # macOS/Linux
                try:
                    subprocess.Popen(["open", directory])
                except:
                    subprocess.Popen(["xdg-open", directory])
    
    def _open_in_browser(self, url):
        """
        在瀏覽器中打開 URL
        
        Args:
            url (str): 要打開的 URL
        """
        if url:
            webbrowser.open(url)
    
    def _clear_history(self):
        """清除所有歷史記錄"""
        # 創建確認對話框
        confirm_dialog = ctk.CTkToplevel(self)
        confirm_dialog.title("確認清除")
        confirm_dialog.geometry("400x180")
        confirm_dialog.resizable(False, False)
        confirm_dialog.transient(self)
        confirm_dialog.grab_set()
        
        # 將對話框置中
        confirm_dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - confirm_dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - confirm_dialog.winfo_height()) // 2
        confirm_dialog.geometry(f"+{x}+{y}")
        
        # 添加警告圖標
        warning_label = ctk.CTkLabel(
            confirm_dialog,
            text="警告",
            font=("Arial", 16, "bold"),
            text_color="#d33a56"
        )
        warning_label.pack(pady=(20, 5))
        
        # 添加說明文字
        message_label = ctk.CTkLabel(
            confirm_dialog,
            text="確定要清除所有下載歷史嗎？\n此操作不可撤銷。",
            font=("Arial", 12)
        )
        message_label.pack(pady=5)
        
        # 按鈕框架
        button_frame = ctk.CTkFrame(confirm_dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # 確認按鈕
        def on_confirm():
            self.history.clear_history()
            self._load_history_records()
            confirm_dialog.destroy()
        
        confirm_button = ctk.CTkButton(
            button_frame,
            text="確認清除",
            command=on_confirm,
            fg_color="#d33a56",
            hover_color="#b52e47",
            font=("Arial", 12, "bold")
        )
        confirm_button.pack(side="left", padx=10)
        
        # 取消按鈕
        cancel_button = ctk.CTkButton(
            button_frame,
            text="取消",
            command=confirm_dialog.destroy,
            font=("Arial", 12, "bold")
        )
        cancel_button.pack(side="right", padx=10)
    
    def _on_close(self):
        """窗口關閉事件處理函數"""
        self.grab_release()
        self.destroy()
