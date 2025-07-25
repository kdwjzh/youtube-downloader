"""
品質選擇組件 - 用於選擇下載品質
"""
import customtkinter as ctk


class QualitySelector(ctk.CTkFrame):
    """品質選擇組件"""
    
    def __init__(self, master, on_quality_change=None, **kwargs):
        """
        初始化品質選擇組件
        
        Args:
            master: 父組件
            on_quality_change (function): 品質變更回調函數
            **kwargs: 其他參數
        """
        super().__init__(master, **kwargs)
        
        self.on_quality_change = on_quality_change
        
        # 品質選項
        self.mp4_options = ["360p", "480p", "720p", "1080p", "2K", "4K"]
        self.mp3_options = ["128kbps", "192kbps", "256kbps", "320kbps"]
        
        self.current_format = "MP3"  # 默認格式
        self.current_quality = "320kbps"  # 默認品質
        
        # 配置網格
        self.grid_columnconfigure(0, weight=0)  # 標籤
        self.grid_columnconfigure(1, weight=1)  # 下拉選單
        
        # 創建標籤
        self.quality_label = ctk.CTkLabel(
            self, 
            text="下載品質",
            font=("Arial", 12)
        )
        self.quality_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # 創建下拉選單
        self.quality_menu = ctk.CTkOptionMenu(
            self,
            values=self.mp3_options,  # 默認顯示 MP3 選項
            command=self._on_quality_selected,
            width=200,
            height=32,
            font=("Arial", 12, "bold"),
            dropdown_font=("Arial", 12, "bold")
        )
        self.quality_menu.grid(row=0, column=1, sticky="ew")
        
        # 設置默認值
        self.quality_menu.set(self.current_quality)
    
    def _on_quality_selected(self, selected_quality):
        """
        品質選擇事件處理函數
        
        Args:
            selected_quality (str): 選擇的品質
        """
        if selected_quality != self.current_quality:
            self.current_quality = selected_quality
            
            # 如果有回調函數，則調用
            if self.on_quality_change:
                self.on_quality_change(selected_quality)
    
    def update_for_format(self, format_type):
        """
        根據格式更新品質選項
        
        Args:
            format_type (str): 格式類型（MP3/MP4）
        """
        self.current_format = format_type
        
        if format_type == "MP4":
            # 更新為 MP4 品質選項
            self.quality_menu.configure(values=self.mp4_options)
            
            # 如果當前選擇的不是 MP4 選項，則設置為默認
            if self.current_quality not in self.mp4_options:
                self.current_quality = "720p"
                self.quality_menu.set(self.current_quality)
                
                # 如果有回調函數，則調用
                if self.on_quality_change:
                    self.on_quality_change(self.current_quality)
        else:
            # 更新為 MP3 品質選項
            self.quality_menu.configure(values=self.mp3_options)
            
            # 如果當前選擇的不是 MP3 選項，則設置為默認
            if self.current_quality not in self.mp3_options:
                self.current_quality = "320kbps"
                self.quality_menu.set(self.current_quality)
                
                # 如果有回調函數，則調用
                if self.on_quality_change:
                    self.on_quality_change(self.current_quality)
    
    def get_quality(self):
        """
        獲取當前選擇的品質
        
        Returns:
            str: 當前品質
        """
        return self.current_quality
    
    def set_quality(self, quality):
        """
        設置品質
        
        Args:
            quality (str): 要設置的品質
        """
        if (self.current_format == "MP4" and quality in self.mp4_options) or \
           (self.current_format == "MP3" and quality in self.mp3_options):
            self.quality_menu.set(quality)
            self.current_quality = quality
