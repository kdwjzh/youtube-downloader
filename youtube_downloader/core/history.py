"""
歷史記錄模塊 - 管理下載歷史
"""
import os
import json
import time
from datetime import datetime


class DownloadHistory:
    """下載歷史管理類"""
    
    def __init__(self, history_file=None):
        """
        初始化下載歷史管理器
        
        Args:
            history_file (str): 歷史記錄文件路徑
        """
        if not history_file:
            # 默認歷史記錄文件位於用戶主目錄下
            history_dir = os.path.join(os.path.expanduser("~"), ".youtube_downloader")
            os.makedirs(history_dir, exist_ok=True)
            history_file = os.path.join(history_dir, "download_history.json")
            
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self):
        """
        加載歷史記錄
        
        Returns:
            list: 歷史記錄列表
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _save_history(self):
        """保存歷史記錄"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"無法保存歷史記錄: {e}")
    
    def add_record(self, video_info, download_options, file_path):
        """
        添加下載記錄
        
        Args:
            video_info (dict): 視頻信息
            download_options (dict): 下載選項
            file_path (str): 文件路徑
        """
        # 創建記錄
        record = {
            "id": video_info.get("id", ""),
            "title": video_info.get("title", "未知標題"),
            "url": video_info.get("webpage_url", ""),
            "thumbnail": video_info.get("thumbnail", ""),
            "duration": video_info.get("duration_string", ""),
            "format": download_options.get("format", ""),
            "quality": download_options.get("quality", ""),
            "file_path": file_path,
            "download_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": int(time.time())
        }
        
        # 添加到歷史記錄
        self.history.insert(0, record)  # 新記錄插入到最前面
        
        # 限制歷史記錄數量
        if len(self.history) > 100:
            self.history = self.history[:100]
        
        # 保存歷史記錄
        self._save_history()
        
        return record
    
    def get_records(self, limit=10):
        """
        獲取歷史記錄
        
        Args:
            limit (int): 限制返回的記錄數量
            
        Returns:
            list: 歷史記錄列表
        """
        return self.history[:limit]
    
    def clear_history(self):
        """清除所有歷史記錄"""
        self.history = []
        self._save_history()
    
    def delete_record(self, record_id):
        """
        刪除指定記錄
        
        Args:
            record_id (str): 記錄 ID
            
        Returns:
            bool: 是否成功刪除
        """
        for i, record in enumerate(self.history):
            if record.get("id") == record_id:
                del self.history[i]
                self._save_history()
                return True
        return False
