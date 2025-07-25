"""
播放列表下載窗口 - 處理播放列表的批量下載
"""
import os
import customtkinter as ctk
from PIL import Image

from youtube_downloader.core.playlist import PlaylistProcessor
from youtube_downloader.core.downloader import YouTubeDownloader
from youtube_downloader.core.history import DownloadHistory
from youtube_downloader.gui.components.url_input import URLInput
from youtube_downloader.gui.components.format_selector import FormatSelector
from youtube_downloader.gui.components.quality_selector import QualitySelector
from youtube_downloader.gui.components.path_selector import PathSelector
from youtube_downloader.gui.components.progress_bar import ProgressBar


class PlaylistWindow(ctk.CTkToplevel):
    """播放列表下載窗口"""
    
    def __init__(self, master=None, history=None):
        """
        初始化播放列表下載窗口
        
        Args:
            master: 父窗口
            history: 歷史記錄管理器實例，從主窗口傳入
        """
        super().__init__(master)
        
        # 設置窗口標題和大小
        self.title("播放列表批量下載")
        self.geometry("1000x600")
        self.minsize(800, 600)
        
        # 創建核心組件
        self.playlist_processor = PlaylistProcessor(callback=self._on_playlist_update)
        self.downloader = YouTubeDownloader()
        # 使用傳入的歷史記錄管理器，如果沒有則創建新的
        self.history = history if history else DownloadHistory()
        
        # 創建界面組件
        self._create_widgets()
        
        # 布局界面組件
        self._setup_layout()
        
        # 綁定事件處理函數
        self._bind_events()
        
        # 初始化狀態
        self.playlist_info = None
        self.embed_thumbnail = False
        
        # 設置窗口為模態
        self.transient(master)
        self.grab_set()
    
    def _create_widgets(self):
        """創建界面組件"""
        # 創建主滾動框架
        self.main_scrollable_frame = ctk.CTkScrollableFrame(self)
        
        # 創建標題框架
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        # 創建標題標籤
        self.title_label = ctk.CTkLabel(
            self.title_frame, 
            text="YouTube 播放列表批量下載",
            font=("Arial", 18, "bold")
        )
        
        # 創建說明按鈕
        self.help_button = ctk.CTkButton(
            self.title_frame,
            text="使用說明",
            font=("Arial", 12, "bold"),
            width=100,
            height=30,
            command=self._on_help_clicked
        )
        
        # 創建說明標籤
        self.desc_label = ctk.CTkLabel(
            self,
            text="輸入 YouTube 播放列表網址，批量下載所有影片",
            font=("Arial", 12)
        )
        
        # 創建 URL 輸入組件
        self.url_input = URLInput(
            self,
            on_url_change=self._on_url_changed,
            on_url_submit=self._on_url_submitted,
            fg_color="transparent"
        )
        
        # 創建播放列表信息框架
        self.playlist_info_frame = ctk.CTkFrame(self.main_scrollable_frame)
        
        # 創建播放列表標題標籤
        self.playlist_title_label = ctk.CTkLabel(
            self.playlist_info_frame,
            text="",
            font=("Arial", 14, "bold"),
            anchor="w",
            wraplength=600
        )
        
        # 創建播放列表詳情標籤
        self.playlist_details_label = ctk.CTkLabel(
            self.playlist_info_frame,
            text="",
            font=("Arial", 12),
            anchor="w"
        )
        
        # 創建下載選項框架
        self.download_options_frame = ctk.CTkFrame(self.main_scrollable_frame)
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
            self.main_scrollable_frame,
            on_path_change=self._on_path_changed,
            fg_color="transparent"
        )
        
        # 創建嵌入縮圖開關
        self.embed_thumbnail_var = ctk.BooleanVar(value=False)
        self.embed_thumbnail_switch = ctk.CTkSwitch(
            self.main_scrollable_frame,
            text="添加縮圖至文件",
            variable=self.embed_thumbnail_var,
            command=self._on_embed_thumbnail_changed,
            font=("Arial", 12)
        )
        
        # 創建影片列表框架 - 改用滾動框架增強可視性
        self.videos_list_frame = ctk.CTkScrollableFrame(
            self.main_scrollable_frame,
            label_text="播放列表影片",
            label_font=("Arial", 12, "bold"),
            height=200
        )
        self.videos_list_frame.grid_columnconfigure(0, weight=1)  # 影片標題列
        self.videos_list_frame.grid_columnconfigure(1, weight=0)  # 影片序號列
        
        # 創建影片列表兩行表頭
        self.video_items = []
        
        # 創建進度條組件
        self.progress_bar = ProgressBar(self.main_scrollable_frame)
        
        # 創建按鈕框架
        self.button_frame = ctk.CTkFrame(self.main_scrollable_frame, fg_color="transparent")
        
        # 創建下載按鈕
        self.download_button = ctk.CTkButton(
            self.button_frame,
            text="開始批量下載",
            font=("Arial", 14, "bold"),
            height=40,
            fg_color="#d33a56",
            text_color="white",
            hover_color="#b52e47",
            command=self._on_download_clicked
        )
        
        # 創建取消按鈕
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="關閉",
            font=("Arial", 14, "bold"),
            height=40,
            command=self._on_cancel_clicked
        )
    
    def _setup_layout(self):
        """設置界面布局"""
        padding = 20
        
        # 布局標題框架
        self.title_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        # 在標題框架中布局標題和說明按鈕
        self.title_label.pack(side="left", pady=(0, 0))
        self.help_button.pack(side="right", padx=(0, 20), pady=(0, 0))
        
        # 布局說明標籤
        self.desc_label.pack(pady=(10, 20))
        
        # 布局 URL 輸入組件
        self.url_input.pack(fill="x", padx=padding, pady=(0, padding))
        
        # 布局主滾動區域 - 充滿剩餘空間並允許擴展
        self.main_scrollable_frame.pack(fill="both", expand=True, padx=padding, pady=(0, padding))
        
        # 預先在滾動框架內布局其他組件
        # 布局下載選項框架
        self.download_options_frame.pack(fill="x", padx=0, pady=(0, padding))
        
        # 格式選擇組件
        self.format_selector.grid(row=0, column=0, padx=(10, padding), pady=padding, sticky="w")
        
        # 品質選擇組件
        self.quality_selector.grid(row=0, column=1, padx=(0, 10), pady=padding, sticky="w")
        
        # 布局路徑選擇組件
        self.path_selector.pack(fill="x", padx=0, pady=(0, padding))
        
        # 布局嵌入縮圖開關
        self.embed_thumbnail_switch.pack(fill="x", padx=0, pady=(0, padding))
        
        # 布局進度條組件
        self.progress_bar.pack(fill="x", padx=0, pady=(0, padding))
        
        # 布局按鈕框架
        self.button_frame.pack(fill="x", padx=0, pady=(0, padding))
        
        # 布局下載按鈕
        self.download_button.pack(side="left", padx=10)
        
        # 布局取消按鈕
        self.cancel_button.pack(side="right", padx=10)
        
        # 注意：播放列表信息框架和影片列表框架將在播放列表加載時動態添加
    
    def _bind_events(self):
        """綁定事件處理函數"""
        # 窗口關閉事件
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _on_url_changed(self, url, is_valid):
        """
        URL 變更事件處理函數
        
        Args:
            url (str): 變更後的 URL
            is_valid (bool): URL 是否有效
        """
        # 播放列表 URL 的有效性檢查在提取信息時進行
        pass
    
    def _on_url_submitted(self, url):
        """
        URL 提交事件處理函數
        
        Args:
            url (str): 提交的 URL
        """
        # 清除現有信息
        self._clear_playlist_info()
        
        # 提取播放列表信息
        self.playlist_processor.extract_playlist_info(url)
    
    def _on_playlist_update(self, info):
        """
        播放列表信息更新事件處理函數
        
        Args:
            info (dict): 播放列表信息字典
        """
        status = info.get('status', '')
        print(f"\033[1;36m收到播放列表更新狀態: {status}, 訊息: {info.get('message', '')}, 是否下載完成: {info.get('downloaded', False)}\033[0m")
        
        if status == 'extracting':
            # 顯示提取中信息
            self.progress_bar.update_progress({
                'status': 'starting',
                'message': '正在獲取播放列表信息...'
            })
            
        # 特別處理批量下載完成的情況
        elif status == 'complete' and info.get('downloaded', False) == True:
            # 下載完成情況
            completed_videos = info.get('completed_videos', 0)
            total_videos = info.get('total_videos', 0)
            print(f"\033[1;36m批量下載已完成，共 {completed_videos}/{total_videos} 個影片\033[0m")
            
            # 更新進度條顯示完成信息
            self.progress_bar.update_progress({
                'status': 'success',
                'message': f'批量下載完成，共 {completed_videos}/{total_videos} 個影片'
            })
            
            # 播放下載完成音效
            try:
                import winsound
                import os
                import threading
                # 使用專用的音效文件，與主窗口一致的路徑計算方式
                sound_path = os.path.join(os.path.dirname(__file__), "../assets/sounds/download_complete_sound.wav")
                
                # 嘗試幾種不同的方式播放音效
                if os.path.exists(sound_path):
                    print(f"播放下載完成音效: {sound_path}")
                    # 方式一：直接播放
                    try:
                        winsound.PlaySound(sound_path, winsound.SND_FILENAME)
                        print("直接播放音效完成")
                    except Exception as e:
                        print(f"直接播放音效失敗: {str(e)}")
                        
                        # 嘗試方式二：系統聲音
                        try:
                            winsound.MessageBeep(winsound.MB_ICONASTERISK)
                            print("播放系統音效完成")
                        except Exception as e2:
                            print(f"播放系統音效失敗: {str(e2)}")
                else:
                    # print(f"找不到音效文件: {sound_path}，使用系統音效")
                    print(f"找不到音效文件: {sound_path}，如果有音效可以無視這則訊息!")
                    # # 使用系統音效
                    # winsound.MessageBeep(winsound.MB_ICONASTERISK)
                    # # 使用另一種系統音效
                    # winsound.Beep(1000, 500)  # 1000Hz的聲音持續500毫秒
            except Exception as e:
                print(f"播放音效失敗: {str(e)}")
            
        # 處理信息提取完成的情況
        elif status == 'complete' and 'playlist_info' in info:
            # 播放列表信息提取完成的情況
            playlist_info = info.get('playlist_info', {})
            
            # 確保播放列表信息有效
            if not playlist_info or not playlist_info.get('entries'):
                self.progress_bar.update_progress({
                    'status': 'error',
                    'error': '播放列表沒有影片或提取失敗'
                })
                return
                
            # 如果有效，設置播放列表信息
            self.playlist_info = playlist_info
            print(f"\033[1;36m成功設置播放列表信息: {self.playlist_info.get('title')}, 影片數量: {len(self.playlist_info.get('entries', []))}\033[0m")
            
            # 更新界面
            self._update_playlist_info_ui()
                
        elif status == 'error':
            # 顯示錯誤信息
            error_message = info.get('error', '未知錯誤')
            print(f"播放列表錯誤: {error_message}")
            
            # 檢查是否為批量下載相關錯誤
            if '已有批量下載任務正在進行' in error_message:
                # 重置處理狀態
                print("重置播放列表處理器狀態")
                self.playlist_processor.is_processing = False
                self.playlist_processor.current_task = None
                
                # 顯示安全的錯誤訊息
                self.progress_bar.update_progress({
                    'status': 'error',
                    'error': '已重置批量下載狀態，請再試一次'
                })
                
                # 不清除播放列表信息
                return
            
            # 其他錯誤情況，顯示錯誤訊息
            self.progress_bar.update_progress({
                'status': 'error',
                'error': error_message
            })
            
            # 只有在提取播放列表信息失敗時才清除播放列表信息
            if '播放列表' in error_message and ('提取失敗' in error_message or '無效' in error_message):
                print("清除播放列表信息")
                self.playlist_info = None
        
        elif status == 'downloading':
            # 顯示下載中的進度信息
            progress = info.get('progress', 0)
            message = info.get('message', '正在下載...')
            current = info.get('current_video', 0)
            total = info.get('total_videos', 0)
            
            # 查看是否需要添加到歷史記錄
            if info.get('add_to_history', False):
                filename = info.get('filename', '')
                video_info = info.get('video_info', {})
                format_option = info.get('format', 'mp4')
                quality_option = info.get('quality', 'best')
                
                # 確保有足夠的信息添加到歷史記錄
                if filename and video_info:
                    print(f"\033[1;32m將播放列表下載的視頻添加到歷史記錄: {video_info.get('title', '未知標題')}\033[0m")
                    
                    # 添加下載選項
                    download_options = {
                        'format': format_option,
                        'quality': quality_option,
                        'embed_thumbnail': self.embed_thumbnail
                    }
                    
                    # 添加到歷史記錄
                    record = self.history.add_record(video_info, download_options, filename)
                    print(f"\033[1;32m成功添加播放列表視頻到歷史記錄: {record.get('title')}\033[0m")
                else:
                    print(f"\033[1;33m無法添加到歷史記錄: 缺少文件名或視頻信息\033[0m")
            
            # 更新進度條
            self.progress_bar.update_progress({
                'status': 'downloading',
                'percent': progress,
                'message': message
            })
            
            # 如果是最後一個影片且進度為100%，換成成功狀態
            if current == total and progress >= 0.99:
                self.progress_bar.update_progress({
                    'status': 'success',
                    'message': f'批量下載完成，共 {current}/{total} 個影片'
                })
                
                # 播放下載完成音效
                try:
                    import winsound
                    import os
                    import threading
                    # 使用專用的音效文件 - 與主窗口一致的路徑計算方式
                    sound_path = os.path.join(os.path.dirname(__file__), "../assets/sounds/download_complete_sound.wav")
                    
                    if os.path.exists(sound_path):
                        print(f"播放下載完成音效: {sound_path}")
                        # 在後台線程中播放音效，避免阻栓UI
                        threading.Thread(
                            target=lambda: winsound.PlaySound(sound_path, winsound.SND_FILENAME),
                            daemon=True
                        ).start()
                    else:
                        print(f"找不到音效文件: {sound_path}，使用系統音效")
                        # 使用最標準的系統完成音效
                        winsound.MessageBeep(winsound.MB_OK)
                except Exception as e:
                    print(f"播放音效失敗: {str(e)}")
            else:
                self.progress_bar.update_progress({
                    'status': 'downloading',
                    'percent': progress,
                    'speed': info.get('speed', ''),
                    'downloaded': f"{info.get('completed_videos', current)}/{info.get('total_videos', total)} 個影片"
                })
            
        elif status == 'cancelled':
            # 顯示取消信息
            self.progress_bar.update_progress({
                'status': 'cancelled',
                'message': '批量下載已取消'
            })

    def _update_playlist_info_ui(self):
        """更新播放列表信息界面"""
        if not self.playlist_info:
            return
            
        # 顯示播放列表信息框架 - 將其直接放在滾動框架內
        self.playlist_info_frame.pack(fill="x", padx=0, pady=(0, 10))
        
        # 更新播放列表標題
        title = self.playlist_info.get('title', '未知播放列表')
        self.playlist_title_label.configure(text=title)
        
        # 更新播放列表詳情
        uploader = self.playlist_info.get('uploader', '未知上傳者')
        entries = self.playlist_info.get('entries', [])
        video_count = len(entries)
        
        details_text = f"上傳者: {uploader} | 影片數量: {video_count}"
        self.playlist_details_label.configure(text=details_text)
        
        # 顯示影片列表框架 - 不使用after參數，直接放在滾動框架內
        self.videos_list_frame.pack(fill="both", expand=True, padx=0, pady=(0, 10))
        
        # 更新影片列表
        self._update_videos_list()
    
    def _update_videos_list(self):
        """更新影片列表"""
        # 清除現有項目
        for widget in self.video_items:
            widget.destroy()
        self.video_items = []
        
        # 獲取影片列表
        entries = self.playlist_info.get('entries', [])
        
        if not entries:
            # 創建無影片提示
            no_video_label = ctk.CTkLabel(
                self.videos_list_frame,
                text="播放列表中沒有影片",
                font=("Arial", 12),
                anchor="center"
            )
            no_video_label.grid(row=0, column=0, columnspan=2, pady=20)
            self.video_items.append(no_video_label)
            return
            
        # 添加標題行
        title_label = ctk.CTkLabel(
            self.videos_list_frame,
            text="影片標題",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=5, pady=(0, 10))
        self.video_items.append(title_label)
        
        number_label = ctk.CTkLabel(
            self.videos_list_frame,
            text="序號",
            font=("Arial", 12, "bold"),
            anchor="e"
        )
        number_label.grid(row=0, column=1, sticky="e", padx=5, pady=(0, 10))
        self.video_items.append(number_label)
        
        # 添加分隔線
        separator = ctk.CTkFrame(
            self.videos_list_frame,
            height=1,
            fg_color="gray"
        )
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.video_items.append(separator)
        
        # 添加影片項目
        for i, video in enumerate(entries):
            # 影片標題
            title = video.get('title', f'未知標題 {i+1}')
            title_label = ctk.CTkLabel(
                self.videos_list_frame,
                text=title,
                font=("Arial", 12),
                anchor="w",
                wraplength=500
            )
            title_label.grid(row=i+2, column=0, sticky="w", padx=5, pady=2)
            self.video_items.append(title_label)
            
            # 影片序號
            number_label = ctk.CTkLabel(
                self.videos_list_frame,
                text=f"#{i+1}",
                font=("Arial", 12),
                anchor="e"
            )
            number_label.grid(row=i+2, column=1, sticky="e", padx=5, pady=2)
            self.video_items.append(number_label)
    
    def _clear_playlist_info(self):
        """清除播放列表信息"""
        # 隱藏播放列表信息框架和影片列表框架
        self.playlist_info_frame.pack_forget()
        self.videos_list_frame.pack_forget()
        
        # 清除播放列表信息
        self.playlist_info = None
        
        # 清除標籤文本
        self.playlist_title_label.configure(text="")
        self.playlist_details_label.configure(text="")
        
        # 清除影片列表
        for widget in self.video_items:
            widget.destroy()
        self.video_items = []
    
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
        pass
    
    def _on_path_changed(self, path):
        """
        路徑變更事件處理函數
        
        Args:
            path (str): 變更後的路徑
        """
        pass
    
    def _on_embed_thumbnail_changed(self):
        """嵌入縮圖開關事件處理函數"""
        self.embed_thumbnail = self.embed_thumbnail_var.get()
    
    def _on_download_clicked(self):
        """下載按鈕點擊事件處理函數"""
        print("點擊了開始批量下載按鈕")
        
        # 檢查是否有播放列表信息
        if not self.playlist_info:
            print("無播放列表信息")
            self.progress_bar.update_progress({
                'status': 'error',
                'error': '請先輸入有效的播放列表 URL'
            })
            return
            
        # 檢查是否有影片條目
        if not self.playlist_info.get('entries'):
            print("播放列表沒有影片條目")
            self.progress_bar.update_progress({
                'status': 'error',
                'error': '此播放列表中沒有影片可下載'
            })
            return
        
        # 獲取下載選項
        format_type = self.format_selector.get_format()
        quality = self.quality_selector.get_quality()
        output_path = self.path_selector.get_path()
        embed_thumbnail = self.embed_thumbnail
        
        # 檢查輸出路徑
        if not output_path or output_path.strip() == '':
            print("輸出路徑無效")
            self.progress_bar.update_progress({
                'status': 'error',
                'error': '請選擇有效的輸出路徑'
            })
            return
        
        print(f"開始批量下載: {len(self.playlist_info.get('entries', []))}個影片, 格式:{format_type}, 品質:{quality}")
        
        # 開始批量下載
        self.playlist_processor.batch_download(
            playlist_info=self.playlist_info,
            output_path=output_path,
            format_option=format_type.lower(),
            quality_option=quality,
            embed_thumbnail=embed_thumbnail,
            downloader=self.downloader
        )
    
    def _on_cancel_clicked(self):
        """取消按鈕點擊事件處理函數"""
        # 如果正在下載，則取消下載
        if self.playlist_processor.is_processing:
            self.playlist_processor.cancel()
        else:
            # 否則關閉窗口
            self._on_close()
    
    def _on_close(self):
        """窗口關閉事件處理函數"""
        # 如果正在下載，則取消下載
        if self.playlist_processor.is_processing:
            self.playlist_processor.cancel()
        
        # 釋放窗口
        self.grab_release()
        self.destroy()
        
    def _on_help_clicked(self):
        """說明按鈕點擊事件處理函數"""
        print("點擊了使用說明按鈕")
        
        # 從導入幫助窗口模塊
        from youtube_downloader.gui.help_window import HelpWindow
        
        # 創建幫助窗口實例
        help_window = HelpWindow(
            master=self,
            title="播放列表下載使用說明",
            width=800,
            height=600
        )
        
        # 進行初始化佈局
        help_window.update()
