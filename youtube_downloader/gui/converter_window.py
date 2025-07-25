import customtkinter as ctk
import os
import threading
import winsound
import time
from tkinter import filedialog, messagebox
import tkinter as tk
from moviepy.editor import VideoFileClip, AudioFileClip
from proglog import ProgressBarLogger

class ConverterWindow(ctk.CTkToplevel):
    """格式轉換窗口"""
    def __init__(self, master=None):
        super().__init__(master)
        self.title("格式轉換器")
        self.geometry("600x400")
        self.minsize(500, 300)

        self.input_file_path = None
        self.output_folder_path = None
        self.output_file_path = None  # 添加輸出文件路徑屬性

        self._create_widgets()
        self._setup_layout()

        self.transient(master)
        self.grab_set()

    def _create_widgets(self):
        """創建界面組件"""
        # 輸入文件選擇
        self.input_file_frame = ctk.CTkFrame(self)
        self.input_file_label = ctk.CTkLabel(self.input_file_frame, text="輸入文件:", font=("Arial", 12, "bold"))
        self.input_file_entry = ctk.CTkEntry(self.input_file_frame, width=300)
        self.input_file_button = ctk.CTkButton(self.input_file_frame, text="選擇文件", command=self._select_input_file, font=("Arial", 12, "bold"))

        # 輸出格式選擇
        self.output_format_frame = ctk.CTkFrame(self)
        self.output_format_label = ctk.CTkLabel(self.output_format_frame, text="輸出格式:", font=("Arial", 12, "bold"))
        self.output_format_var = ctk.StringVar(value="mp3") # 默認格式
        # 音頻格式
        self.audio_formats = ["mp3", "wav", "ogg", "flac"]
        # 視頻格式
        self.video_formats = ["mp4", "webm", "mov", "avi"]
        self.current_formats = self.audio_formats # 默認顯示音頻格式
        self.output_format_menu = ctk.CTkOptionMenu(self.output_format_frame, variable=self.output_format_var, values=self.current_formats, command=self._update_output_options)

        # 輸出文件夾選擇
        self.output_folder_frame = ctk.CTkFrame(self)
        self.output_folder_label = ctk.CTkLabel(self.output_folder_frame, text="輸出文件夾:", font=("Arial", 12, "bold"))
        self.output_folder_entry = ctk.CTkEntry(self.output_folder_frame, width=300)
        self.output_folder_button = ctk.CTkButton(self.output_folder_frame, text="選擇文件夾", command=self._select_output_folder, font=("Arial", 12, "bold"))

        # 轉換按鈕
        self.convert_button = ctk.CTkButton(self, text="開始轉換", command=self._start_conversion, font=("Arial", 12, "bold"))

        # 將控件先創建好但不立即放置，在_setup_layout中統一安排佈局
        # 創建進度條
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)
        
        # 創建進度百分比標籤
        self.progress_percent_label = ctk.CTkLabel(self, text="0.0%", font=("Arial", 12, "bold"))
        
        # 創建狀態標籤
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12, "bold"))

    def _setup_layout(self):
        """佈局界面組件"""
        self.input_file_frame.pack(pady=10, padx=10, fill="x")
        self.input_file_label.pack(side="left", padx=5)
        self.input_file_entry.pack(side="left", expand=True, fill="x", padx=5)
        self.input_file_button.pack(side="left", padx=5)

        self.output_format_frame.pack(pady=10, padx=10, fill="x")
        self.output_format_label.pack(side="left", padx=5)
        self.output_format_menu.pack(side="left", padx=5)

        self.output_folder_frame.pack(pady=10, padx=10, fill="x")
        self.output_folder_label.pack(side="left", padx=5)
        self.output_folder_entry.pack(side="left", expand=True, fill="x", padx=5)
        self.output_folder_button.pack(side="left", padx=5)
        
        # 添加轉換按鈕
        self.convert_button.pack(pady=20)
        
        # 添加進度條和相關標籤
        self.progress_bar.pack(padx=20, pady=(0, 5), fill="x")
        self.progress_percent_label.pack(pady=(0, 5))
        self.status_label.pack(pady=(0, 20))

    def _select_input_file(self):
        """選擇輸入文件"""
        file_path = filedialog.askopenfilename(
            title="選擇要轉換的文件",
            filetypes=(
                ("Media files", "*.mp3 *.wav *.ogg *.flac *.aac *.m4a *.mp4 *.webm *.mov *.avi *.mkv *.flv"),
                ("Audio files", "*.mp3 *.wav *.ogg *.flac *.aac *.m4a"),
                ("Video files", "*.mp4 *.webm *.mov *.avi *.mkv *.flv"),
                ("All files", "*.*"),
            )
        )
        if file_path:
            self.input_file_path = file_path
            self.input_file_entry.delete(0, tk.END)
            self.input_file_entry.insert(0, file_path)
            self._update_output_options_based_on_input(file_path)

    def _update_output_options_based_on_input(self, file_path):
        """根據輸入文件類型更新輸出格式選項"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        if ext in [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"]:
            self.current_formats = self.audio_formats
            self.output_format_var.set(self.audio_formats[0]) # 默認選中第一個音頻格式
        elif ext in [".mp4", ".webm", ".mov", ".avi", ".mkv", ".flv"]: # Video extensions
            self.current_formats = self.video_formats
            self.output_format_var.set(self.video_formats[0]) # 默認選中第一個視頻格式
        else:
            self.current_formats = self.audio_formats + self.video_formats # 未知類型則顯示所有
            self.output_format_var.set(self.current_formats[0])
        
        self.output_format_menu.configure(values=self.current_formats)

    def _update_output_options(self, choice):
        """當手動選擇輸出格式時，確保選擇有效 (主要用於未來擴展)"""
        # 目前這個函數在選擇後不做特別處理，主要由 _update_output_options_based_on_input 控制
        pass

    def _select_output_folder(self):
        """選擇輸出文件夾"""
        folder_path = filedialog.askdirectory(title="選擇輸出文件夾")
        if folder_path:
            self.output_folder_path = folder_path
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, folder_path)

    def _start_conversion(self):
        """開始格式轉換"""
        if not self.input_file_path:
            messagebox.showerror("錯誤", "請選擇輸入文件")
            return
        if not self.output_folder_path:
            messagebox.showerror("錯誤", "請選擇輸出文件夾")
            return

        output_format = self.output_format_var.get()
        input_filename = os.path.basename(self.input_file_path)
        output_filename = os.path.splitext(input_filename)[0] + "." + output_format
        output_file_path = os.path.join(self.output_folder_path, output_filename)
        
        # 將output_file_path保存為類屬性，以便在完成時使用
        self.output_file_path = output_file_path

        if os.path.exists(output_file_path):
            if not messagebox.askyesno("警告", "輸出文件已存在，是否覆蓋？"):
                return

        self.progress_bar.set(0)
        self.status_label.configure(text="準備轉換...")
        self.convert_button.configure(state="disabled")

        threading.Thread(target=self._convert_thread, args=(output_file_path, output_format), daemon=True).start()

    def _convert_thread(self, output_file_path, output_format):
        """轉換線程"""
        try:
            # 更新UI
            self.after(0, lambda: self.status_label.configure(text="正在轉換中..."))
            self.after(0, lambda: self.progress_bar.set(0.01)) # 轉換剛開始，設置一個小的初始進度值
            self.after(0, lambda: self.progress_percent_label.configure(text="0.0%"))

            # 直接實現一個更具鮹錯力的進度日誌器，捕捉所有可能的進度更新
            from proglog import ProgressBarLogger
            import time
            
            class CustomProgressBarLogger(ProgressBarLogger):
                def __init__(self, parent_window):
                    super().__init__()
                    self.parent_window = parent_window
                    self.last_update_time = time.time()
                    self.started = False
                    # 記錄用於進度計算的資訊
                    self.total_time = 0
                    self.current_time = 0
                    self.last_percent = 0
                
                # 重寫所有可能的回調方法，確保捕捉任何進度信息
                def callback(self, **kw):
                    # 用於一般回調，錯誤捕捉版
                    try:
                        if 'chunk' in kw and 'total' in kw['chunk']:
                            total = kw['chunk']['total']
                            index = kw['chunk'].get('index', 0)
                            if total > 0:
                                percent = min(index / total, 1.0)
                                self._update_progress_ui(percent)
                    except Exception:
                        pass  # 忽略錯誤
                
                def bars_callback(self, bar, attr, value, old_value=None):
                    # 進度條更新回調
                    try:
                        # 如果是視頻長度相關信息
                        if bar == 'moviepy' and attr == 'total':
                            self.total_time = value
                        elif bar == 'moviepy' and attr == 'index':
                            self.current_time = value
                            if self.total_time > 0:
                                percent = min(self.current_time / self.total_time, 1.0)
                                self._update_progress_ui(percent)
                        # 如果是區塊進度
                        elif bar == 'chunk':
                            if attr == 'total':
                                self.total_time = value
                            elif attr == 'index' and self.total_time > 0:
                                percent = min(value / self.total_time, 1.0)
                                self._update_progress_ui(percent)
                            elif attr == 't' and hasattr(self, 'tbar') and hasattr(self.tbar, 'tmax') and self.tbar.tmax > 0:
                                percent = min(value / self.tbar.tmax, 1.0)
                                self._update_progress_ui(percent)
                    except Exception as e:
                        print(f"Progress bar update error: {e}")
                
                def _update_progress_ui(self, percent):
                    """\u66f4\u65b0UI\u9032\u5ea6\u689d\u548c\u6587\u5b57"""
                    # 加入節流：每0.1秒最多更新1次，且進度差異超過1%才更新
                    now = time.time()
                    # 避免提前顯示100%，限制最大進度為95%，直到真正轉換完成
                    capped_percent = min(percent, 0.95)  # 限制最大為95%
                    
                    if (now - self.last_update_time > 0.1 and abs(capped_percent - self.last_percent) > 0.01):
                        self.last_update_time = now
                        self.last_percent = capped_percent
                        percent_text = f"{capped_percent * 100:.1f}%"
                        self.parent_window.after(0, lambda p=capped_percent: self.parent_window.progress_bar.set(p))
                        self.parent_window.after(0, lambda t=percent_text: self.parent_window.progress_percent_label.configure(text=t))
                
                # 非必要但為了實現完整接口
                def log(self, message, level="info"):
                    # 忽略一般日誌信息
                    pass
                
                def set_level(self, level):
                    # 設置日誌級別
                    pass
                
                def new_bar(self, bar_name):
                    # 創建新進度條
                    if not self.started:
                        self.started = True
                    return bar_name
                
                def get_bar(self, bar_name):
                    # 取得進度條
                    return bar_name
                
                def tbar_initialize(self, bar_name, total):
                    # 初始化時間進度條
                    if bar_name == 'chunk':
                        self.tbar = lambda: None  # 創建空對象
                        self.tbar.tmax = total
                
                def tbar_tick(self, bar_name, value=1):
                    # 時間進度條更新
                    if hasattr(self, 'tbar') and hasattr(self.tbar, 'tmax') and self.tbar.tmax > 0:
                        self._update_progress_ui(min(value / self.tbar.tmax, 1.0))
                
                def tbar_close(self, bar_name):
                    # 關閉時間進度條
                    pass
            
            # 創建日誌器實例
            progress_logger = CustomProgressBarLogger(self)
            
            # 檢查輸入文件的類型和輸出格式
            is_video_input = self.input_file_path.lower().endswith((".mp4", ".webm", ".mov", ".avi", ".mkv", ".flv"))
            is_video_output = output_format.lower() in ["mp4", "webm", "mov", "avi"]
            
            if is_video_input: # 輸入是視頻
                clip = VideoFileClip(self.input_file_path)
                
                if is_video_output: # 視頻轉視頻
                    clip.write_videofile(
                        output_file_path,
                        codec=self._get_video_codec(output_format),
                        ffmpeg_params=['-preset', 'ultrafast', '-y'],
                        logger=progress_logger, # 使用自定義日誌器
                        verbose=False # 不顯示詳細輸出
                    )
                else: # 視頻轉音頻
                    audio = clip.audio
                    audio.write_audiofile(
                        output_file_path,
                        codec=self._get_audio_codec(output_format),
                        ffmpeg_params=['-preset', 'ultrafast', '-y'],
                        logger=progress_logger,
                        verbose=False
                    )
                    audio.close()
                clip.close()
            else: # 輸入是音頻
                if is_video_output: # 音頻轉視頻 (不支持)
                    self.after(0, lambda: messagebox.showerror("錯誤", f"不支持將音頻文件轉換為 {output_format} 視頻格式。"))
                    self.after(0, self._conversion_finished, False, "格式不支持")
                    return

                # 音頻轉音頻
                clip = AudioFileClip(self.input_file_path)
                clip.write_audiofile(
                    output_file_path,
                    codec=self._get_audio_codec(output_format),
                    ffmpeg_params=['-preset', 'ultrafast', '-y'],
                    logger=progress_logger,
                    verbose=False
                )
                clip.close()
            
            self.after(0, self._conversion_finished, True, "轉換成功！")

        except Exception as e:
            error_message = f"轉換失敗: {str(e)}"
            print(error_message)
            self.after(0, self._conversion_finished, False, error_message)

    def _get_video_codec(self, file_format):
        """根據文件格式獲取推薦的視頻編解碼器"""
        if file_format == "webm":
            return "libvpx-vp9"
        elif file_format == "mov":
            return "libx264" # MOV 通常使用 H.264
        elif file_format == "avi":
            return "mpeg4"   # AVI 可以使用多種，mpeg4 比較通用
        return "libx264" # 默認 MP4 使用 H.264

    def _get_audio_codec(self, file_format):
        """根據文件格式獲取推薦的音頻編解碼器"""
        if file_format == "wav":
            return "pcm_s16le" # WAV 通常是未壓縮的 PCM
        elif file_format == "ogg":
            return "libvorbis"
        elif file_format == "flac":
            return "flac"
        return "libmp3lame" # 默認 MP3
        
    def _play_complete_sound(self):
        """播放轉換完成提示音效"""
        try:
            # 使用更清晰的音效文件
            sound_path = os.path.join(os.path.dirname(__file__), "../assets/sounds/ding-ding.wav")
            
            if os.path.exists(sound_path):
                # 使用SND_ASYNC以非阻塞方式播放，加上SND_NOSTOP確保音效完整播放
                winsound.PlaySound(
                    sound_path, 
                    winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NOSTOP
                )
                
                # 播放兩次以確保更明顯
                threading.Thread(
                    target=lambda: [
                        time.sleep(0.3), 
                        winsound.PlaySound(
                            sound_path, 
                            winsound.SND_FILENAME | winsound.SND_ASYNC
                        )
                    ],
                    daemon=True
                ).start()
                
                print(f"播放轉換完成音效: {sound_path}")
            else:
                # 如果沒有找到音效文件，使用系統提示音並重複播放
                winsound.MessageBeep(winsound.MB_OK)
                threading.Thread(
                    target=lambda: [
                        time.sleep(0.2),
                        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                    ],
                    daemon=True
                ).start()
                print(f"音效文件不存在，使用系統預設音效: {sound_path}")
        except Exception as e:
            print(f"播放音效失敗: {e}")
    
    def _conversion_finished(self, success, message=""):
        """轉換完成後調用"""
        # 確保進度條顯示正確的最終狀態
        if success:
            # 在真正完成時設置為100%
            self.progress_bar.set(1.0)  # 真正完成時顯示100%
            self.progress_percent_label.configure(text="100.0%")
            self.status_label.configure(text="轉換成功！")
            # 播放完成音效
            self._play_complete_sound()
            messagebox.showinfo("成功", "格式轉換完成\n\n輸出文件：" + os.path.join(self.output_folder_path, os.path.basename(self.output_file_path)))
        else:
            # 失敗時保持現有進度，不設置為100%
            self.status_label.configure(text=f"轉換失敗: {message}")
            messagebox.showerror("錯誤", f"轉換失敗: {message}")
        
        # 啟用開始按鈕
        self.convert_button.configure(state="normal")

if __name__ == '__main__':
    # 測試用
    app = ctk.CTk()
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    button = ctk.CTkButton(app, text="打開轉換器", command=lambda: ConverterWindow(app))
    button.pack(pady=20)
    
    app.mainloop()
