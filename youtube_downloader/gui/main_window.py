"""
主界面類 - 應用程序的主窗口
"""
import os
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import winsound  # 添加 winsound 庫用於播放音效
from PIL import Image

from youtube_downloader.gui.components.url_input import URLInput
from youtube_downloader.gui.components.thumbnail import ThumbnailViewer
from youtube_downloader.gui.components.format_selector import FormatSelector
from youtube_downloader.gui.components.quality_selector import QualitySelector
from youtube_downloader.gui.components.path_selector import PathSelector
from youtube_downloader.gui.components.progress_bar import ProgressBar
from youtube_downloader.gui.history_window import HistoryWindow
from youtube_downloader.gui.playlist_window import PlaylistWindow
from youtube_downloader.gui.converter_window import ConverterWindow
from youtube_downloader.core.video_info import VideoInfoExtractor
from youtube_downloader.core.downloader import YouTubeDownloader
from youtube_downloader.core.utils import get_default_download_path
from youtube_downloader.core.history import DownloadHistory
from youtube_downloader.core.updater import UpdateChecker
from youtube_downloader.config import APP_NAME, APP_VERSION


class MainWindow(ctk.CTk):
    """主界面類"""
    
    def __init__(self):
        """初始化主界面"""
        super().__init__()
        
        # 設置窗口標題和大小
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("800x650")
        self.minsize(700, 600)
        
        # 設置窗口在啟動時自動最大化
        self.after(100, lambda: self.state('zoomed'))  # 使用 after 避免在初始化階段最大化導致的問題
        
        # 設置主題
        ctk.set_appearance_mode("light")  # 設置為淺色主題
        ctk.set_default_color_theme("blue")
        
        # 設置窗口圖標
        try:
            # 直接使用現有的 ICO 文件
            ico_path = os.path.join(os.path.dirname(__file__), "../assets/icons/app_logo.ico")
            if os.path.exists(ico_path):
                # 使用 iconbitmap 設置圖標
                self.iconbitmap(ico_path)
                # print(f"成功設置圖標：{ico_path}")
                print("\033[0;35m"+"歡迎使用 YouTube 下載器 ~"+"\033[0m")
            else:
                print(f"圖標文件不存在：{ico_path}")
        except Exception as e:
            print(f"設置圖標失敗：{e}")
        
        # 創建核心組件
        self.video_info = VideoInfoExtractor(callback=self._on_video_info_update)
        self.downloader = YouTubeDownloader(callback=self._on_download_update)
        self.history = DownloadHistory()
        self.updater = UpdateChecker(parent=self, callback=self._on_update_checked)
        
        # 創建界面組件
        self._create_widgets()
        
        # 布局界面組件
        self._setup_layout()
        
        # 綁定事件處理函數
        self._bind_events()
        
        # 用於保存當前視頻信息
        self.current_video_info = None
        self.embed_thumbnail = False
        
        # 檢查更新
        self.updater.check_update()

        # 初始化其他窗口實例變數
        self.history_window = None
        self.playlist_window = None
        self.converter_window = None
    
    def _create_widgets(self):
        """創建界面組件"""
        # 創建菜單欄
        self._create_menu()
        
        # 創建主標題
        self.title_label = ctk.CTkLabel(
            self, 
            text="Download high quality YouTube videos in MP3 and MP4",
            font=("Arial", 20, "bold")
        )
        
        # 創建 URL 輸入組件
        self.url_input = URLInput(
            self,
            on_url_change=self._on_url_changed,
            on_url_submit=self._on_url_submitted,
            fg_color="transparent"
        )
        
        # 創建影片信息框架
        self.video_info_frame = ctk.CTkFrame(self)
        self.video_info_frame.grid_columnconfigure(0, weight=0)  # 縮圖
        self.video_info_frame.grid_columnconfigure(1, weight=1)  # 影片信息
        
        # 創建縮圖顯示組件
        self.thumbnail_viewer = ThumbnailViewer(
            self.video_info_frame,
            width=320,
            height=180,
            fg_color="#f0f0f0",
            corner_radius=5
        )
        
        # 創建影片信息標籤
        self.video_title_label = ctk.CTkLabel(
            self.video_info_frame,
            text="",
            font=("Arial", 14, "bold"),
            anchor="w",
            wraplength=400
        )
        
        self.video_duration_label = ctk.CTkLabel(
            self.video_info_frame,
            text="",
            font=("Arial", 12),
            anchor="w"
        )
        
        self.video_views_label = ctk.CTkLabel(
            self.video_info_frame,
            text="",
            font=("Arial", 12),
            anchor="w"
        )
        
        # 創建下載選項框架
        self.download_options_frame = ctk.CTkFrame(self)
        self.download_options_frame.grid_columnconfigure(0, weight=1)  # 格式選擇器
        self.download_options_frame.grid_columnconfigure(1, weight=1)  # 品質選擇器
        
        # 創建格式選擇組件
        self.format_selector = FormatSelector(
            self.download_options_frame,
            on_format_change=self._on_format_changed,
            fg_color="transparent"
        )
        
        # 創建品質選擇組件
        self.quality_selector = QualitySelector(
            self.download_options_frame,
            on_quality_change=self._on_quality_changed,
            fg_color="transparent"
        )
        
        # 創建路徑選擇組件
        self.path_selector = PathSelector(
            self,
            on_path_change=self._on_path_changed,
            fg_color="transparent"
        )
        
        # 創建嵌入縮圖開關
        self.embed_thumbnail_var = ctk.BooleanVar(value=False)
        self.embed_thumbnail_switch = ctk.CTkSwitch(
            self,
            text="添加縮圖至文件",
            variable=self.embed_thumbnail_var,
            command=self._on_embed_thumbnail_changed,
            font=("Arial", 12)
        )
        
        # 創建進度條組件
        self.progress_bar = ProgressBar(
            self,
            fg_color="transparent"
        )
        
        # 創建下載按鈕 - 直接放在主窗口中
        self.download_button = ctk.CTkButton(
            self,
            text="開始下載",
            font=("Arial", 16, "bold"),
            height=40,
            width=300,
            fg_color="#d33a56",
            text_color="white",
            hover_color="#b52e47",
            command=self._on_download_clicked
        )
    
    def _setup_layout(self):
        """設置界面布局"""
        padding = 20
        
        # 布局主標題
        self.title_label.pack(pady=(padding, padding), padx=padding)
        
        # 布局 URL 輸入組件
        self.url_input.pack(fill="x", padx=padding, pady=(0, padding))
        
        # 布局影片信息框架
        self.video_info_frame.pack(fill="x", padx=padding, pady=(0, padding))
        
        # 縮圖顯示組件
        self.thumbnail_viewer.grid(row=0, column=0, padx=(0, padding), pady=padding, rowspan=3)
        
        # 影片信息標籤
        self.video_title_label.grid(row=0, column=1, sticky="w", padx=(0, padding), pady=(padding, 5))
        self.video_duration_label.grid(row=1, column=1, sticky="w", padx=(0, padding), pady=(0, 5))
        self.video_views_label.grid(row=2, column=1, sticky="w", padx=(0, padding), pady=(0, padding))
        
        # 布局下載選項框架
        self.download_options_frame.pack(fill="x", padx=padding, pady=(0, padding))
        
        # 格式選擇組件
        self.format_selector.grid(row=0, column=0, padx=(0, padding), pady=padding, sticky="w")
        
        # 品質選擇組件
        self.quality_selector.grid(row=0, column=1, padx=(0, padding), pady=padding, sticky="w")
        
        # 布局路徑選擇組件
        self.path_selector.pack(fill="x", padx=padding, pady=(0, padding))
        
        # 布局嵌入縮圖開關
        self.embed_thumbnail_switch.pack(fill="x", padx=padding, pady=(0, padding))
        
        # 布局下載按鈕
        self.download_button.pack(fill="x", padx=padding*3, pady=(10, 20))
        
        # 布局進度條組件
        self.progress_bar.pack(fill="x", padx=padding, pady=(padding, 0))
        
        # 預設顯示一個初始狀態
        self.progress_bar.update_progress({"status": "starting"})
    
    def _bind_events(self):
        """綁定事件處理函數"""
        # 窗口關閉事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _create_menu(self):
        """創建菜單欄"""
        # 創建菜單欄框架
        self.menu_frame = ctk.CTkFrame(self, height=30, fg_color="#2a2d2e")
        self.menu_frame.pack(fill="x")
        
        # 文件菜單
        self.file_button = ctk.CTkButton(
            self.menu_frame,
            text="文件",
            width=60,
            height=30,
            fg_color="transparent",
            text_color="white",
            hover_color="#4a4d4e",
            command=self._show_file_menu,
            font=("Arial", 12, "bold")
        )
        self.file_button.pack(side="left")
        
        # 歷史記錄按鈕
        self.history_button = ctk.CTkButton(
            self.menu_frame,
            text="歷史下載記錄",
            width=80,
            height=30,
            fg_color="transparent",
            text_color="white",
            hover_color="#4a4d4e",
            command=self._show_history,
            font=("Arial", 12, "bold")
        )
        self.history_button.pack(side="left")
        
        # 說明按鈕
        self.help_button = ctk.CTkButton(
            self.menu_frame,
            text="說明",
            width=60,
            height=30,
            fg_color="transparent",
            text_color="white",
            hover_color="#4a4d4e",
            command=self._open_documentation,
            font=("Arial", 12, "bold")
        )
        self.help_button.pack(side="left")
        
        # 播放列表按鈕
        self.playlist_button = ctk.CTkButton(
            self.menu_frame,
            text="播放列表下載",
            width=80,
            height=30,
            fg_color="transparent",
            text_color="white",
            hover_color="#4a4d4e",
            command=self._show_playlist_window,
            font=("Arial", 12, "bold")
        )
        self.playlist_button.pack(side="left")
        
        # 關於按鈕
        self.about_button = ctk.CTkButton(
            self.menu_frame,
            text="關於",
            width=60,
            height=30,
            fg_color="transparent",
            text_color="white",
            hover_color="#4a4d4e",
            command=self._show_about,
            font=("Arial", 12, "bold")
        )
        self.about_button.pack(side="left")

        # 格式轉換按鈕
        self.converter_button = ctk.CTkButton(
            self.menu_frame,
            text="格式轉換",
            width=80,
            height=30,
            fg_color="transparent",
            text_color="white",
            hover_color="#4a4d4e",
            command=self._show_converter_window,
            font=("Arial", 12, "bold")
        )
        self.converter_button.pack(side="left")
        
        # 檢查更新按鈕
        self.update_button = ctk.CTkButton(
            self.menu_frame,
            text="檢查更新",
            width=80,
            height=30,
            fg_color="transparent",
            text_color="white",
            hover_color="#4a4d4e",
            command=self._check_for_updates,
            font=("Arial", 12, "bold")
        )
        self.update_button.pack(side="left")
    
    def _show_converter_window(self):
        """顯示格式轉換窗口"""
        if self.converter_window is None or not self.converter_window.winfo_exists():
            self.converter_window = ConverterWindow(self)
            self.converter_window.transient(self) # 設置為頂層窗口，但依附於主窗口
            self.converter_window.grab_set() # 捕獲事件，使其成為模態窗口
        else:
            self.converter_window.focus() # 如果已存在，則聚焦
        
    def _show_file_menu(self):
        """顯示文件菜單"""
        # 創建菜單
        menu = tk.Menu(self, tearoff=0, font=("Arial", 18, "bold"))
        
        # 設置菜單項標籤寬度和高度
        menu.config(activeborderwidth=20)
        
        # 利用tkinter變量設置菜單項高度和寬度
        self._set_menu_dimensions(menu)
        
        # 新增菜單項
        menu.add_command(label="貼上 URL 至輸入框內...", command=self._paste_from_clipboard)
        menu.add_command(label="YT播放列表批量下載", command=self._show_playlist_window)
        menu.add_command(label="歷史下載記錄", command=self._show_history)
        menu.add_separator()
        menu.add_command(label="退出", command=self._on_closing)
        
        # 獲取按鈕位置
        x = self.file_button.winfo_rootx()
        y = self.file_button.winfo_rooty() + self.file_button.winfo_height()
        
        # 顯示菜單
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()
            
    def _paste_from_clipboard(self):
        """從剪貼板粘貼 URL"""
        self.url_input._paste_from_clipboard()
    
    def _load_download_icon(self):
        """加載下載圖標"""
        try:
            # 創建一個簡單的下載圖標
            icon_size = 20
            icon = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
            return ctk.CTkImage(light_image=icon, dark_image=icon, size=(icon_size, icon_size))
        except Exception:
            return None
    
    def _on_url_changed(self, url, is_valid):
        """
        URL 變更事件處理函數
        
        Args:
            url (str): 變更後的 URL
            is_valid (bool): URL 是否有效
        """
        # 如果 URL 有效，則獲取視頻信息
        if is_valid:
            self.video_info.extract_video_info(url)
    
    def _on_url_submitted(self, url):
        """
        URL 提交事件處理函數
        
        Args:
            url (str): 提交的 URL
        """
        # 如果 URL 有效，則獲取視頻信息
        self.video_info.extract_video_info(url)
        
        # 加載縮圖
        self.thumbnail_viewer.load_thumbnail_for_url(url)
    
    def _on_video_info_update(self, info):
        """
        視頻信息更新事件處理函數
        
        Args:
            info (dict): 視頻信息字典
        """
        if info['status'] == 'complete':
            # 更新當前視頻信息
            self.current_video_info = info.get('info', {})
            
            # 更新界面
            self._update_video_info_ui()
    
    def _update_video_info_ui(self):
        """更新視頻信息界面"""
        if not self.current_video_info:
            return
            
        # 更新影片標題
        title = self.current_video_info.get('title', '')
        self.video_title_label.configure(text=title)
        
        # 更新影片時長
        duration = self.current_video_info.get('duration_string', '')
        self.video_duration_label.configure(text=f"時長: {duration}")
        
        # 更新觀看次數
        view_count = self.current_video_info.get('view_count', 0)
        view_count_str = f"{view_count:,}" if view_count else "未知"
        self.video_views_label.configure(text=f"觀看次數: {view_count_str}")
    
    def _on_format_changed(self, format_type):
        """
        格式變更事件處理函數
        
        Args:
            format_type (str): 變更後的格式
        """
        # 更新品質選擇組件
        self.quality_selector.update_for_format(format_type)
    
    def _on_quality_changed(self, quality):
        """
        品質變更事件處理函數
        
        Args:
            quality (str): 變更後的品質
        """
        # 可以在這裡添加額外的處理邏輯
        pass
    
    def _on_path_changed(self, path):
        """
        路徑變更事件處理函數
        
        Args:
            path (str): 變更後的路徑
        """
        # 可以在這裡添加額外的處理邏輯
        pass
    
    def _on_embed_thumbnail_changed(self):
        """嵌入縮圖開關事件處理函數"""
        self.embed_thumbnail = self.embed_thumbnail_var.get()
    
    def _on_download_clicked(self):
        """下載按鈕點擊事件處理函數"""
        # 獲取 URL
        url = self.url_input.get_url()
        if not url:
            # 顯示錯誤信息
            self.progress_bar.update_progress({
                'status': 'error',
                'error': '請輸入有效的 YouTube URL'
            })
            return
        
        # 獲取下載選項
        format_type = self.format_selector.get_format()
        quality = self.quality_selector.get_quality()
        output_path = self.path_selector.get_path()
        embed_thumbnail = self.embed_thumbnail
        
        # 開始下載
        self.downloader.download(
            url=url,
            output_path=output_path,
            format_option=format_type.lower(),
            quality_option=quality,
            embed_thumbnail=embed_thumbnail
        )
    
    def _on_download_update(self, info):
        """
        下載更新事件處理函數
        
        Args:
            info (dict): 下載信息字典
        """
        # 更新進度條
        self.progress_bar.update_progress(info)
        
        # 如果下載完成，則添加到歷史記錄並播放提示音效
        if info['status'] == 'complete':
            filename = info.get('filename', '')
            video_info = info.get('info', self.current_video_info)
            
            # 輸出調試信息
            print(f"\033[1;36m下載完成，文件名: {filename}\33[0m")
            print(f"影片信息狀態: {'有' if video_info else '無'}")
            print(f"目前影片信息狀態: {'有' if self.current_video_info else '無'}")
            
            if filename:
                # 創建下載選項記錄
                download_options = {
                    'format': self.format_selector.get_format().lower(),
                    'quality': self.quality_selector.get_quality(),
                    'embed_thumbnail': self.embed_thumbnail
                }
                
                # 使用傳過來的影片信息或当前影片信息
                if video_info or self.current_video_info:
                    # 添加到歷史記錄
                    record = self.history.add_record(
                        video_info or self.current_video_info,
                        download_options,
                        filename
                    )
                    print(f"已添加歷史記錄: {record.get('title', '')}")
                else:
                    print("無法添加歷史記錄：缺少影片信息")
                
                # 播放下載完成提示音效
                self._play_complete_sound()
    
    def _show_history(self):
        """顯示歷史記錄窗口"""
        history_window = HistoryWindow(self, on_redownload=self._on_history_redownload)
        
    def _on_history_redownload(self, url):
        """
        從歷史記錄中重新下載
        
        Args:
            url (str): 要重新下載的 URL
        """
        if url:
            self.url_input.set_url(url)
            self._on_url_submitted(url)
            
    def _show_playlist_window(self):
        """顯示播放列表下載窗口，並傳遞歷史記錄管理器實例"""
        playlist_window = PlaylistWindow(self, history=self.history)
            
    def _open_documentation(self):
        """打開文檔網頁"""
        webbrowser.open("https://github.com/kdwjzh/youtube-downloader")
        
    def _set_menu_dimensions(self, menu):
        """設置菜單項的尺寸
        
        Args:
            menu: 要設置的菜單
        """
        # 使用tkinter變量設置菜單項高度和寬度
        menu.config(
            activebackground="#4a4d4e",      # 滑鼠移到時的背景色
            activeforeground="white",       # 滑鼠移到時的前景色
            background="#333333",           # 菜單背景色
            foreground="white",            # 菜單文字顏色
            relief="solid",                # 邊框樣式
            borderwidth=2,                # 邊框寬度
            selectcolor="#4a4d4e"          # 選中項的顔色
        )
        
        # 適用每個菜單項的高度
        menu.configure(postcommand=lambda: self._update_menu_height(menu))
        
    def _update_menu_height(self, menu):
        """更新菜單項的高度
        
        Args:
            menu: 要設置的菜單
        """
        # 嘗試設置菜單項的高度和寬度
        # 注意：這些設置在不同系統上的效果可能有差異
        try:
            # 確保給每個菜單項足夠的空間
            menu.tk.call("option", "add", "*Menu.borderWidth", "2")
            menu.tk.call("option", "add", "*Menu.activeBorderWidth", "2")
            menu.tk.call("option", "add", "*Menu.font", "Arial 16 bold")
            
            # 設置菜單項的高度，這會影響菜單項之間的空間
            padding = 10  # 增加菜單項間的間距
            menu.tk.call("option", "add", "*Menu.borderWidth", str(padding))
            menu.tk.call("option", "add", "*Menu.activeBorderWidth", str(padding))
        except Exception as e:
            print(f"設置菜單項高度時出錯: {e}")
            
    def _play_complete_sound(self):
        """播放下載完成提示音效"""
        try:
            # 音效文件路徑
            sound_path = os.path.join(os.path.dirname(__file__), "../assets/sounds/download_complete_sound.wav")
            
            if os.path.exists(sound_path):
                # 在後台線程中播放音效，避免阻堵UI
                threading.Thread(
                    target=lambda: winsound.PlaySound(sound_path, winsound.SND_FILENAME),
                    daemon=True
                ).start()
                print(f"播放完成音效: {sound_path}")
            else:
                # 如果沒有找到音效文件，則使用系統預設音效
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
                print(f"音效文件不存在，使用系統預設音效: {sound_path}")
        except Exception as e:
            print(f"播放音效失敗: {e}")
        
    def _show_about(self):
        """顯示關於對話框"""
        about_window = ctk.CTkToplevel(self)
        about_window.title("關於")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        about_window.transient(self)
        about_window.grab_set()
        
        # 添加應用程序信息
        about_label = ctk.CTkLabel(
            about_window,
            text=f"{APP_NAME}\n版本 {APP_VERSION}",
            font=("Arial", 18, "bold")
        )
        about_label.pack(pady=(30, 10))
        
        # 添加描述
        desc_label = ctk.CTkLabel(
            about_window,
            text="使用 Python 和 CustomTkinter 開發的 YouTube 下載工具\n支持下載影片為 MP4 和音頻為 MP3 格式",
            font=("Arial", 12),
            wraplength=350
        )
        desc_label.pack(pady=10)
        
        # 添加版權信息
        copyright_label = ctk.CTkLabel(
            about_window,
            text="© 2025 YouTube Downloader",
            font=("Arial", 10),
            text_color="gray"
        )
        copyright_label.pack(pady=10)
        
        # 添加關閉按鈕
        close_button = ctk.CTkButton(
            about_window,
            text="關閉",
            command=about_window.destroy
        )
        close_button.pack(pady=20)
        
    def _check_for_updates(self):
        """
        手動檢查更新
        """
        # 顯示檢查更新對話框
        messagebox.showinfo(f"{APP_NAME} - 更新檢查", "正在檢查更新，請稍候...")
        
        # 調用更新檢查器，指定同步檢查，並不靜默運行
        self.updater.check_update(async_check=False, silent=False)

    def _on_update_checked(self, result):
        """
        更新檢查回調函數
        
        Args:
            result (dict): 更新檢查結果
        """
        # 靜默檢查不需要顯示無更新訊息
        if result.get('silent', True) and not result.get('has_update', False):
            return
            
        if result['status'] == 'success' and result.get('has_update', False):
            # 有更新可用，更新的對話框已在 UpdateChecker 中處理
            # 我們不需要在這裡再次創建對話框
            pass
        elif result['status'] == 'success' and not result.get('silent', True):
            # 手動檢查且無更新時顯示訊息
            messagebox.showinfo(f"{APP_NAME} - 更新檢查", "您正在使用最新版本！")
        elif result['status'] == 'error' and not result.get('silent', True):
            # 檢查更新出錯
            messagebox.showerror(
                f"{APP_NAME} - 更新檢查錯誤", 
                f"檢查更新時發生錯誤：\n{result.get('error', '未知錯誤')}"
            )
    
    def _open_download_page(self, url):
        """
        打開下載頁面
        
        Args:
            url (str): 下載頁面 URL
        """
        if url:
            webbrowser.open(url)
    
    def _on_closing(self):
        """窗口關閉事件處理函數"""
        # 取消下載
        self.downloader.cancel()
        
        # 關閉窗口
        self.destroy()
