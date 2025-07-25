"""
影片信息獲取模塊 - 處理 YouTube 影片信息的獲取
"""
import os
import re
import tempfile
import threading
import time
import yt_dlp
import requests
from PIL import Image
import io

from .utils import validate_youtube_url, format_time


class VideoInfoExtractor:
    """YouTube 影片信息提取器"""
    
    def __init__(self, callback=None):
        """
        初始化影片信息提取器
        
        Args:
            callback (function): 回調函數，用於更新 UI
        """
        self.callback = callback
        self.cache = {}  # 緩存已獲取的影片信息
        self._extraction_thread = None
    
    def extract_video_info(self, url, async_extract=True):
        """
        獲取影片基本信息
        
        Args:
            url (str): YouTube URL
            async_extract (bool): 是否異步提取
            
        Returns:
            dict: 影片信息字典 (如果同步) 或 None (如果異步)
        """
        # 檢查 URL 是否有效
        if not validate_youtube_url(url):
            if self.callback:
                self.callback({
                    'status': 'error',
                    'error': '無效的 YouTube URL'
                })
            return None
        
        # 檢查是否有緩存
        if url in self.cache:
            if self.callback:
                self.callback({
                    'status': 'complete',
                    'info': self.cache[url]
                })
            return self.cache[url]
        
        # 通知開始提取
        if self.callback:
            self.callback({
                'status': 'extracting',
                'message': '正在獲取影片信息...'
            })
        
        if async_extract:
            # 啟動異步提取線程
            self._extraction_thread = threading.Thread(
                target=self._extract_thread,
                args=(url,)
            )
            self._extraction_thread.daemon = True
            self._extraction_thread.start()
            return None
        else:
            # 同步提取
            return self._extract_info(url)
    
    def _extract_thread(self, url):
        """
        異步提取線程執行函數
        
        Args:
            url (str): YouTube URL
        """
        try:
            info = self._extract_info(url)
            
            if self.callback:
                self.callback({
                    'status': 'complete',
                    'info': info
                })
        except Exception as e:
            if self.callback:
                self.callback({
                    'status': 'error',
                    'error': str(e)
                })
    
    def _extract_info(self, url):
        """
        提取影片信息的核心方法
        
        Args:
            url (str): YouTube URL
            
        Returns:
            dict: 影片信息字典
        """
        ydl_opts = {
            'format': 'best',
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                
                # 提取所需信息
                video_info = self._process_info_dict(info_dict)
                
                # 緩存結果
                self.cache[url] = video_info
                
                return video_info
                
        except Exception as e:
            if self.callback:
                self.callback({
                    'status': 'error',
                    'error': f'無法獲取影片信息: {str(e)}'
                })
            raise
    
    def _process_info_dict(self, info_dict):
        """
        處理 yt-dlp 提供的信息字典
        
        Args:
            info_dict (dict): yt-dlp 提供的原始信息字典
            
        Returns:
            dict: 處理後的影片信息字典
        """
        if not info_dict:
            return None
            
        # 提取基本信息
        video_info = {
            'id': info_dict.get('id', ''),
            'title': info_dict.get('title', '未知標題'),
            'description': info_dict.get('description', ''),
            'thumbnail': info_dict.get('thumbnail', ''),
            'duration': info_dict.get('duration', 0),
            'duration_string': format_time(info_dict.get('duration', 0)),
            'view_count': info_dict.get('view_count', 0),
            'webpage_url': info_dict.get('webpage_url', ''),
            'uploader': info_dict.get('uploader', '未知上傳者'),
            'upload_date': info_dict.get('upload_date', ''),
        }
        
        # 處理格式信息
        formats = []
        
        # 提取 MP4 視頻格式
        mp4_formats = {
            '360p': None,
            '480p': None,
            '720p': None,
            '1080p': None,
            '2K': None,
            '4K': None,
        }
        
        # 提取 MP3 音頻格式
        mp3_formats = {
            '128kbps': None,
            '192kbps': None,
            '256kbps': None,
            '320kbps': None,
        }
        
        # 遍歷所有格式以找出最佳匹配
        for fmt in info_dict.get('formats', []):
            if fmt.get('ext') == 'mp4' and fmt.get('height'):
                height = fmt.get('height')
                
                if height <= 360 and (mp4_formats['360p'] is None or fmt.get('tbr', 0) > mp4_formats['360p'].get('tbr', 0)):
                    mp4_formats['360p'] = fmt
                elif height <= 480 and (mp4_formats['480p'] is None or fmt.get('tbr', 0) > mp4_formats['480p'].get('tbr', 0)):
                    mp4_formats['480p'] = fmt
                elif height <= 720 and (mp4_formats['720p'] is None or fmt.get('tbr', 0) > mp4_formats['720p'].get('tbr', 0)):
                    mp4_formats['720p'] = fmt
                elif height <= 1080 and (mp4_formats['1080p'] is None or fmt.get('tbr', 0) > mp4_formats['1080p'].get('tbr', 0)):
                    mp4_formats['1080p'] = fmt
                elif height <= 1440 and (mp4_formats['2K'] is None or fmt.get('tbr', 0) > mp4_formats['2K'].get('tbr', 0)):
                    mp4_formats['2K'] = fmt
                elif height <= 2160 and (mp4_formats['4K'] is None or fmt.get('tbr', 0) > mp4_formats['4K'].get('tbr', 0)):
                    mp4_formats['4K'] = fmt
            
            # 記錄音頻格式
            if fmt.get('acodec') != 'none' and fmt.get('abr'):
                abr = fmt.get('abr')
                
                if abr <= 128 and (mp3_formats['128kbps'] is None or fmt.get('abr', 0) > mp3_formats['128kbps'].get('abr', 0)):
                    mp3_formats['128kbps'] = fmt
                elif abr <= 192 and (mp3_formats['192kbps'] is None or fmt.get('abr', 0) > mp3_formats['192kbps'].get('abr', 0)):
                    mp3_formats['192kbps'] = fmt
                elif abr <= 256 and (mp3_formats['256kbps'] is None or fmt.get('abr', 0) > mp3_formats['256kbps'].get('abr', 0)):
                    mp3_formats['256kbps'] = fmt
                elif abr <= 320 and (mp3_formats['320kbps'] is None or fmt.get('abr', 0) > mp3_formats['320kbps'].get('abr', 0)):
                    mp3_formats['320kbps'] = fmt
        
        # 添加可用的 MP4 格式
        mp4_available = {}
        for quality, fmt in mp4_formats.items():
            if fmt:
                mp4_available[quality] = {
                    'format_id': fmt.get('format_id'),
                    'ext': 'mp4',
                    'height': fmt.get('height'),
                    'width': fmt.get('width'),
                    'resolution': f"{fmt.get('width', 0)}x{fmt.get('height', 0)}",
                    'filesize': fmt.get('filesize'),
                    'vcodec': fmt.get('vcodec'),
                    'acodec': fmt.get('acodec'),
                }
        
        # 添加可用的 MP3 格式
        mp3_available = {}
        for quality, fmt in mp3_formats.items():
            if fmt:
                mp3_available[quality] = {
                    'format_id': fmt.get('format_id'),
                    'ext': 'mp3',
                    'abr': fmt.get('abr'),
                    'acodec': fmt.get('acodec'),
                }
        
        video_info['formats'] = {
            'mp4': mp4_available,
            'mp3': mp3_available
        }
        
        return video_info
    
    def download_thumbnail(self, url, max_width=480, max_height=270):
        """
        下載影片縮圖
        
        Args:
            url (str): 縮圖 URL
            max_width (int): 最大寬度
            max_height (int): 最大高度
            
        Returns:
            PIL.Image 或 None: 下載的縮圖
        """
        if not url:
            return None
            
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return None
                
            # 從響應內容創建圖片
            img = Image.open(io.BytesIO(response.content))
            
            # 調整圖片大小以適合最大尺寸
            width, height = img.size
            
            if width > max_width or height > max_height:
                # 計算縮放比例
                scale = min(max_width / width, max_height / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                # 調整大小
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            return img
            
        except Exception as e:
            if self.callback:
                self.callback({
                    'status': 'error',
                    'error': f'無法下載縮圖: {str(e)}'
                })
            return None
    
    def get_available_formats(self, url):
        """
        獲取可用格式列表
        
        Args:
            url (str): YouTube URL
            
        Returns:
            dict: 可用格式字典
        """
        # 檢查是否有緩存
        if url in self.cache:
            return self.cache[url].get('formats', {})
            
        # 否則提取信息
        info = self.extract_video_info(url, async_extract=False)
        if info:
            return info.get('formats', {})
        
        return {}
