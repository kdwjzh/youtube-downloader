"""
格式選擇組件 - 用於選擇下載格式（MP3/MP4）
"""
import customtkinter as ctk


class FormatSelector(ctk.CTkFrame):
    """格式選擇組件"""
    
    def __init__(self, master, on_format_change=None, **kwargs):
        """
        初始化格式選擇組件
        
        Args:
            master: 父組件
            on_format_change (function): 格式變更回調函數
            **kwargs: 其他參數
        """
        super().__init__(master, **kwargs)
        
        self.on_format_change = on_format_change
        
        # 格式選項
        self.format_options = ["MP4", "MP3"]
        self.current_format = "MP3"  # 默認選擇 MP3
        
        # 配置網格
        self.grid_columnconfigure(0, weight=0)  # 標籤
        self.grid_columnconfigure(1, weight=1)  # 下拉選單
        
        # 創建標籤
        self.format_label = ctk.CTkLabel(
            self, 
            text="下載格式",
            font=("Arial", 12)
        )
        self.format_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # 創建下拉選單
        self.format_menu = ctk.CTkOptionMenu(
            self,
            values=self.format_options,
            command=self._on_format_selected,
            width=200,
            height=32,
            font=("Arial", 12, "bold"),
            dropdown_font=("Arial", 12, "bold")
        )
        self.format_menu.grid(row=0, column=1, sticky="ew")
        
        # 設置默認值
        self.format_menu.set(self.current_format)
    
    def _on_format_selected(self, selected_format):
        """
        格式選擇事件處理函數
        
        Args:
            selected_format (str): 選擇的格式
        """
        if selected_format != self.current_format:
            self.current_format = selected_format
            
            # 如果有回調函數，則調用
            if self.on_format_change:
                self.on_format_change(selected_format)
    
    def get_format(self):
        """
        獲取當前選擇的格式
        
        Returns:
            str: 當前格式（MP3/MP4）
        """
        return self.current_format
    
    def set_format(self, format_type):
        """
        設置格式
        
        Args:
            format_type (str): 要設置的格式（MP3/MP4）
        """
        if format_type in self.format_options:
            self.format_menu.set(format_type)
            self.current_format = format_type
