"""
幫助窗口 - 顯示使用說明和圖片指南
"""
import os
import customtkinter as ctk
from PIL import Image


class HelpWindow(ctk.CTkToplevel):
    """幫助窗口，顯示使用說明和圖片指南"""
    
    def __init__(self, master=None, title="使用說明", width=800, height=600):
        """
        初始化幫助窗口
        
        Args:
            master: 父窗口
            title: 窗口標題
            width: 窗口寬度
            height: 窗口高度
        """
        super().__init__(master)
        
        # 設置窗口標題和大小
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.minsize(width, height)
        
        # 創建界面組件
        self._create_widgets()
        
        # 布局界面組件
        self._setup_layout()
        
        # 加載圖片
        self._load_images()
        
        # 設置窗口為模態
        self.transient(master)
        self.grab_set()
        
        # 綁定關閉事件
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_widgets(self):
        """創建界面組件"""
        # 創建主滾動框架
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 創建標題標籤
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="播放列表批量下載使用說明",
            font=("Arial", 18, "bold")
        )
        self.title_label.pack(pady=(0, 20))
        
        # 創建說明文本
        self.desc_label = ctk.CTkLabel(
            self.main_frame,
            text="以下是使用播放列表批量下載功能的操作指南：",
            font=("Arial", 14),
            anchor="w",
            justify="left"
        )
        self.desc_label.pack(fill="x", pady=(0, 10))
        
        # 創建步驟1框架
        self.step1_frame = ctk.CTkFrame(self.main_frame)
        self.step1_frame.pack(fill="x", pady=(0, 20))
        
        # 創建步驟1標題
        self.step1_title = ctk.CTkLabel(
            self.step1_frame,
            text="步驟1: 點選(你or其他人的)YouTube播放列表",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        self.step1_title.pack(fill="x", padx=10, pady=(10, 5))
        
        # 創建步驟1說明
        self.step1_desc = ctk.CTkLabel(
            self.step1_frame,
            text="點選你的YouTube播放列表，要使用其他人的YouTube播放列表，必須要先獲得他的YouTube播放列表鏈接。",
            font=("Arial", 12),
            anchor="w",
            justify="left",
            wraplength=700
        )
        self.step1_desc.pack(fill="x", padx=10, pady=(0, 10))
        
        # 創建步驟1圖片標籤(預留位置)
        self.step1_image_label = ctk.CTkLabel(self.step1_frame, text="")
        self.step1_image_label.pack(pady=(0, 10))
        
        # 創建步驟2框架
        self.step2_frame = ctk.CTkFrame(self.main_frame)
        self.step2_frame.pack(fill="x", pady=(0, 20))
        
        # 創建步驟2標題
        self.step2_title = ctk.CTkLabel(
            self.step2_frame,
            text="步驟2: 複製YouTube播放列表內的影片連結",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        self.step2_title.pack(fill="x", padx=10, pady=(10, 5))
        
        # 創建步驟2說明
        self.step2_desc = ctk.CTkLabel(
            self.step2_frame,
            text="點進YouTube播放列表後，只需要複製播放列表內其中一個影片連結即可。(其他人的播放列表也是如此操作)",
            font=("Arial", 12),
            anchor="w",
            justify="left",
            wraplength=700
        )
        self.step2_desc.pack(fill="x", padx=10, pady=(0, 10))
        
        # 創建步驟2圖片標籤(預留位置)
        self.step2_image_label = ctk.CTkLabel(self.step2_frame, text="")
        self.step2_image_label.pack(pady=(0, 10))
        
        # 創建步驟3框架
        self.step3_frame = ctk.CTkFrame(self.main_frame)
        self.step3_frame.pack(fill="x", pady=(0, 20))
        
        # 創建步驟3標題
        self.step3_title = ctk.CTkLabel(
            self.step3_frame,
            text="步驟3: 貼上YouTube連結至輸入框中",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        self.step3_title.pack(fill="x", padx=10, pady=(10, 5))
        
        # 創建步驟3說明
        self.step3_desc = ctk.CTkLabel(
            self.step3_frame,
            text="將剛剛複製的YouTube連結點選貼上(Paste)按鈕，貼至輸入框中；若是使用Ctrl+V貼上的話一樣要再次點選貼上(Paste)按鈕。",
            font=("Arial", 12),
            anchor="w",
            justify="left",
            wraplength=700
        )
        self.step3_desc.pack(fill="x", padx=10, pady=(0, 10))
        
        # 創建步驟3圖片標籤(預留位置)
        self.step3_image_label = ctk.CTkLabel(self.step3_frame, text="")
        self.step3_image_label.pack(pady=(0, 10))
        
        # 創建步驟4框架
        self.step4_frame = ctk.CTkFrame(self.main_frame)
        self.step4_frame.pack(fill="x", pady=(0, 20))
        
        # 創建步驟4標題
        self.step4_title = ctk.CTkLabel(
            self.step4_frame,
            text="步驟4: 等待載入播放列表影片",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        self.step4_title.pack(fill="x", padx=10, pady=(10, 5))
        
        # 創建步驟4說明
        self.step4_desc = ctk.CTkLabel(
            self.step4_frame,
            text="貼上YouTube連結後，請等到cmd顯示：成功設置播放列表信息: <該Youtube播放列表的標題>, 影片數量: <該播放列表的影片數量> 的提示訊息，或是UI介面出現播放列表影片(如下圖所示)，即可按下開始批量下載按鈕。",
            font=("Arial", 12),
            anchor="w",
            justify="left",
            wraplength=700
        )
        self.step4_desc.pack(fill="x", padx=10, pady=(0, 10))
        
        # 創建步驟4圖片標籤(預留位置)
        self.step4_image_label = ctk.CTkLabel(self.step4_frame, text="")
        self.step4_image_label.pack(pady=(0, 10))
        
        # 創建步驟5框架
        self.step5_frame = ctk.CTkFrame(self.main_frame)
        self.step5_frame.pack(fill="x", pady=(0, 20))
        
        # 創建步驟5標題
        self.step5_title = ctk.CTkLabel(
            self.step5_frame,
            text="步驟5: 開始批量下載",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        self.step5_title.pack(fill="x", padx=10, pady=(10, 5))
        
        # 創建步驟5說明
        self.step5_desc = ctk.CTkLabel(
            self.step5_frame,
            text="按下開始批量下載按鈕後，等待完成下載音效出現，即是代表完成下載。",
            font=("Arial", 12),
            anchor="w",
            justify="left",
            wraplength=700
        )
        self.step5_desc.pack(fill="x", padx=10, pady=(0, 10))
        
        # 創建步驟5圖片標籤(預留位置)
        self.step5_image_label = ctk.CTkLabel(self.step5_frame, text="")
        self.step5_image_label.pack(pady=(0, 10))
        
        # 創建關閉按鈕
        self.close_button = ctk.CTkButton(
            self, 
            text="關閉", 
            command=self._on_close,
            width=100,
            height=30
        )
        self.close_button.pack(pady=(0, 20))
    
    def _setup_layout(self):
        """設置界面布局"""
        # 已在_create_widgets中完成布局
        pass
    
    def _load_images(self):
        """加載說明圖片"""
        try:
            # 圖片路徑
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            step1_path = os.path.join(base_dir, "youtube_downloader", "assets", "images", "help", "playlist_step1.png")
            step2_path = os.path.join(base_dir, "youtube_downloader", "assets", "images", "help", "playlist_step2.png")
            step3_path = os.path.join(base_dir, "youtube_downloader", "assets", "images", "help", "playlist_step3.png")
            step4_path = os.path.join(base_dir, "youtube_downloader", "assets", "images", "help", "playlist_step4.png")
            step5_path = os.path.join(base_dir, "youtube_downloader", "assets", "images", "help", "playlist_step5.png")
            
            # 加載步驟1圖片
            if os.path.exists(step1_path):
                # 加載並調整圖片大小
                step1_img = Image.open(step1_path)
                # 計算縮放比例，保持寬度為700，高度按比例縮放
                width, height = step1_img.size
                scale = 700 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                step1_img = step1_img.resize((new_width, new_height), Image.LANCZOS)
                
                # 創建CTkImage
                self.step1_ctk_img = ctk.CTkImage(light_image=step1_img, dark_image=step1_img, size=(new_width, new_height))
                
                # 更新圖片標籤
                self.step1_image_label.configure(image=self.step1_ctk_img, text="")
                print(f"成功加載步驟1圖片: {step1_path}")
            else:
                print(f"找不到步驟1圖片: {step1_path}")
                self.step1_image_label.configure(text="[圖片未找到]")
            
            # 加載步驟2圖片
            if os.path.exists(step2_path):
                # 加載並調整圖片大小
                step2_img = Image.open(step2_path)
                # 計算縮放比例，保持寬度為700，高度按比例縮放
                width, height = step2_img.size
                scale = 700 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                step2_img = step2_img.resize((new_width, new_height), Image.LANCZOS)
                
                # 創建CTkImage
                self.step2_ctk_img = ctk.CTkImage(light_image=step2_img, dark_image=step2_img, size=(new_width, new_height))
                
                # 更新圖片標籤
                self.step2_image_label.configure(image=self.step2_ctk_img, text="")
                print(f"成功加載步驟2圖片: {step2_path}")
            else:
                print(f"找不到步驟2圖片: {step2_path}")
                self.step2_image_label.configure(text="[圖片未找到]")
            
            # 加載步驟3圖片
            if os.path.exists(step3_path):
                # 加載並調整圖片大小
                step3_img = Image.open(step3_path)
                # 計算縮放比例，保持寬度為700，高度按比例縮放
                width, height = step3_img.size
                scale = 700 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                step3_img = step3_img.resize((new_width, new_height), Image.LANCZOS)
                
                # 創建CTkImage
                self.step3_ctk_img = ctk.CTkImage(light_image=step3_img, dark_image=step3_img, size=(new_width, new_height))
                
                # 更新圖片標籤
                self.step3_image_label.configure(image=self.step3_ctk_img, text="")
                print(f"成功加載步驟3圖片: {step3_path}")
            else:
                print(f"找不到步驟3圖片: {step3_path}")
                self.step3_image_label.configure(text="[圖片未找到]")
            
            # 加載步驟4圖片
            if os.path.exists(step4_path):
                # 加載並調整圖片大小
                step4_img = Image.open(step4_path)
                # 計算縮放比例，保持寬度為700，高度按比例縮放
                width, height = step4_img.size
                scale = 700 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                step4_img = step4_img.resize((new_width, new_height), Image.LANCZOS)
                
                # 創建CTkImage
                self.step4_ctk_img = ctk.CTkImage(light_image=step4_img, dark_image=step4_img, size=(new_width, new_height))
                
                # 更新圖片標籤
                self.step4_image_label.configure(image=self.step4_ctk_img, text="")
                print(f"成功加載步驟4圖片: {step4_path}")
            else:
                print(f"找不到步驟4圖片: {step4_path}")
                self.step4_image_label.configure(text="[圖片未找到]")
                
            # 加載步驟5圖片
            if os.path.exists(step5_path):
                # 加載並調整圖片大小
                step5_img = Image.open(step5_path)
                # 計算縮放比例，保持寬度為700，高度按比例縮放
                width, height = step5_img.size
                scale = 700 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                step5_img = step5_img.resize((new_width, new_height), Image.LANCZOS)
                
                # 創建CTkImage
                self.step5_ctk_img = ctk.CTkImage(light_image=step5_img, dark_image=step5_img, size=(new_width, new_height))
                
                # 更新圖片標籤
                self.step5_image_label.configure(image=self.step5_ctk_img, text="")
                print(f"成功加載步驟5圖片: {step5_path}")
            else:
                print(f"找不到步驟5圖片: {step5_path}")
                self.step5_image_label.configure(text="[圖片未找到]")
                
        except Exception as e:
            print(f"加載圖片時出錯: {str(e)}")
    
    def _on_close(self):
        """窗口關閉事件處理函數"""
        self.grab_release()
        self.destroy()
