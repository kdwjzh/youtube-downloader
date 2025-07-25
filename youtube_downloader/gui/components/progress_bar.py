"""
進度條組件 - 顯示下載進度
"""
import customtkinter as ctk

from youtube_downloader.core.utils import format_filesize


class ProgressBar(ctk.CTkFrame):
    """進度條組件"""
    
    def __init__(self, master, **kwargs):
        """
        初始化進度條組件
        
        Args:
            master: 父組件
            **kwargs: 其他參數
        """
        super().__init__(master, **kwargs)
        
        # 配置網格
        self.grid_columnconfigure(0, weight=1)  # 進度條
        
        # 創建進度條
        self.progress = ctk.CTkProgressBar(
            self,
            orientation="horizontal",
            mode="determinate",
            height=20,
            corner_radius=2
        )
        self.progress.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # 創建狀態框架
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(row=1, column=0, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)  # 左側狀態文本
        self.status_frame.grid_columnconfigure(1, weight=0)  # 右側百分比
        
        # 創建狀態標籤
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="顯示下載進度條",
            font=("Arial", 12),
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        # 創建百分比標籤
        self.percent_label = ctk.CTkLabel(
            self.status_frame, 
            text="0%",
            font=("Arial", 12),
            anchor="e"
        )
        self.percent_label.grid(row=0, column=1, sticky="e")
        
        # 初始化進度條
        self.reset()
    
    def update_progress(self, info):
        """
        更新進度
        
        Args:
            info (dict): 進度信息字典
        """
        status = info.get('status', '')
        
        if status == 'starting':
            self.progress.set(0)
            self.status_label.configure(text="準備中...")
            self.percent_label.configure(text="0%")
            
        elif status == 'downloading':
            # 獲取進度信息
            percent = info.get('percent', 0)
            speed = info.get('speed', '0 KiB/s')
            downloaded = info.get('downloaded', '0 B')
            total = info.get('total', 'Unknown')
            eta = info.get('eta', 'Unknown')
            
            # 更新進度條
            self.progress.set(percent)
            
            # 更新狀態文本
            status_text = f"正在下載... {speed}"
            if downloaded and total:
                status_text += f" ({downloaded}/{total})"
            if eta and eta != "Unknown":
                status_text += f", 剩餘時間: {eta}"
                
            self.status_label.configure(text=status_text)
            
            # 更新百分比
            self.percent_label.configure(text=f"{int(percent * 100)}%")
            
        elif status == 'processing':
            self.progress.set(1.0)
            self.status_label.configure(text="正在處理文件...")
            self.percent_label.configure(text="100%")
            
        elif status == 'complete':
            self.progress.set(1.0)
            message = info.get('message', '下載完成')
            self.status_label.configure(text=message)
            self.percent_label.configure(text="100%")
        
        elif status == 'success':
            self.progress.set(1.0)
            message = info.get('message', '下載成功')
            self.status_label.configure(text=message)
            self.percent_label.configure(text="100%")
            
        elif status == 'error':
            error_message = info.get('error', '未知錯誤')
            # 設置錯誤信息為紅色
            self.status_label.configure(
                text=f"錯誤: {error_message}",
                text_color="#d33a56"  # 紅色
            )
            
        elif status == 'cancelled':
            self.reset()
            self.status_label.configure(text="下載已取消")
    
    def reset(self):
        """
        重置進度條
        """
        self.progress.set(0)
        self.status_label.configure(text="Loading...")
        self.percent_label.configure(text="0%")
