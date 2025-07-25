"""
下載核心模塊 - 處理 YouTube 影片下載功能
"""
import os
import threading
import tempfile
import re
import subprocess
import json
import platform
from typing import Dict, Optional, Any, List, Tuple
from pathlib import Path
import yt_dlp
import mutagen
from mutagen.id3 import ID3, APIC
from PIL import Image
import io

from .utils import ensure_dir_exists, sanitize_filename


class YouTubeDownloader:
    """YouTube 下載器核心類"""
    
    def __init__(self, callback=None):
        """
        初始化下載器
        
        Args:
            callback (function): 回調函數，用於更新 UI
        """
        self.callback = callback
        self.is_downloading = False
        self.current_task = None
    
    def _progress_hook(self, d):
        """
        進度回調處理函數
        
        Args:
            d (dict): yt-dlp 回調資訊字典
        """
        if self.callback is None:
            return
            
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', '0 KiB/s').strip()
            downloaded = d.get('_downloaded_bytes_str', '0 B').strip()
            total = d.get('_total_bytes_str', 'Unknown').strip()
            eta = d.get('_eta_str', 'Unknown').strip()
            
            # 將百分比字符串轉換為浮點數
            try:
                percent_float = float(percent.replace('%', '')) / 100
            except ValueError:
                percent_float = 0
                
            status_info = {
                'status': 'downloading',
                'percent': percent_float,
                'speed': speed,
                'downloaded': downloaded,
                'total': total,
                'eta': eta,
                'filename': d.get('filename', '')
            }
            
            self.callback(status_info)
            
        elif d['status'] == 'finished':
            status_info = {
                'status': 'processing',
                'percent': 1.0,
                'filename': d.get('filename', '')
            }
            
            self.callback(status_info)
            
        elif d['status'] == 'error':
            status_info = {
                'status': 'error',
                'error': d.get('error', 'Unknown error'),
                'filename': d.get('filename', '')
            }
            
            self.callback(status_info)
    
    def download(self, url, output_path, format_option, quality_option, embed_thumbnail=False):
        """
        下載 YouTube 影片
        
        Args:
            url (str): YouTube URL
            output_path (str): 輸出路徑
            format_option (str): 格式選項 (mp4/mp3)
            quality_option (str): 品質選項
            embed_thumbnail (bool): 是否嵌入縮圖
            
        Returns:
            threading.Thread: 下載線程
        """
        if self.is_downloading:
            if self.callback:
                self.callback({
                    'status': 'error',
                    'error': '已有下載任務正在進行'
                })
            return None
            
        self.is_downloading = True
        
        if self.callback:
            self.callback({
                'status': 'starting',
                'message': '正在準備下載...'
            })
        
        # 確保輸出目錄存在
        ensure_dir_exists(output_path)
        
        # 根據選擇的格式和品質設置 yt-dlp 選項
        ydl_opts = self._get_ydl_options(output_path, format_option, quality_option, embed_thumbnail)
        
        # 創建下載線程
        download_thread = threading.Thread(
            target=self._download_thread,
            args=(url, ydl_opts, embed_thumbnail)
        )
        
        # 啟動線程
        download_thread.daemon = True
        download_thread.start()
        self.current_task = download_thread
        
        return download_thread
    
    def _download_thread(self, url, ydl_opts, embed_thumbnail=False):
        """
        下載線程執行函數
        
        Args:
            url (str): YouTube URL
            ydl_opts (dict): yt-dlp 選項
            embed_thumbnail (bool): 是否嵌入縮圖
        """
        try:
            print(f"開始下載視頻: {url}")
            # 更新狀態
            if self.callback:
                self.callback({
                    'status': 'downloading',
                    'message': '正在下載...',
                    'url': url
                })
            
            # 確保輸出目錄存在
            output_path = ydl_opts.get('paths', {}).get('home', '')
            if output_path:
                try:
                    os.makedirs(output_path, exist_ok=True)
                    print(f"確保輸出目錄存在: {output_path}")
                except Exception as e:
                    print(f"創建輸出目錄失敗: {str(e)}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 下載視頁
                print("調用yt-dlp開始下載")
                info = ydl.extract_info(url, download=True)
                if info:
                    print(f"成功獲取視頻信息: {info.get('title', '')}")
                else:
                    print("無法獲取視頻信息")
            
            # 處理嵌入縮圖
            if embed_thumbnail and 'mp3' in ydl_opts.get('format', ''):
                # MP3 格式需要手動嵌入縮圖
                thumbnail_url = info.get('thumbnail')
                if thumbnail_url and os.path.exists(ydl_opts.get('outtmpl', '')):
                    self._embed_thumbnail_to_mp3(ydl_opts.get('outtmpl', ''), thumbnail_url)
            
            # 更新狀態
            print("\33[1;36m下載完成\33[0m")
            if self.callback:
                # 獲取實際下載的文件路徑
                filename = info.get('requested_downloads', [{}])[0].get('filepath', '') \
                    if info and 'requested_downloads' in info else ''
                
                if not filename and info and 'title' in info:
                    # 如果沒有得到文件路徑，嘗試根據設置的模板構建
                    ext = 'mp3' if 'mp3' in ydl_opts.get('format', '') else 'mp4'
                    base_name = sanitize_filename(info.get('title', 'download'))
                    filename = ydl_opts.get('outtmpl', '').replace('%(title)s', base_name).replace('%(ext)s', ext)
                
                print(f"\033[1;36m已下載文件: {filename}\33[0m")
                
                self.callback({
                    'status': 'complete',
                    'message': '下載完成',
                    'url': url,
                    'filename': filename,
                    'info': info  # 傳遞完整視頁信息以便在歷史記錄中使用
                })
                
        except Exception as e:
            # 輸出完整的异常訊息
            import traceback
            print(f"下載失敗: {str(e)}")
            traceback.print_exc()
            
            # 更新狀態
            if self.callback:
                self.callback({
                    'status': 'error',
                    'error': f'下載失敗: {str(e)}',
                    'url': url
                })
        finally:
            print("重置下載器狀態: is_downloading = False")
            self.is_downloading = False
    
    def _get_ydl_options(self, output_path, format_option, quality_option, embed_thumbnail):
        """
        獲取 yt-dlp 選項
        
        Args:
            output_path (str): 輸出路徑
            format_option (str): 格式選項 (mp4/mp3)
            quality_option (str): 品質選項
            embed_thumbnail (bool): 是否嵌入縮圖
            
        Returns:
            dict: yt-dlp 選項
        """
        # 格式化輸出模板
        outtmpl = os.path.join(output_path, '%(title)s.%(ext)s')
        
        # 基本選項
        ydl_opts = {
            'outtmpl': outtmpl,
            'progress_hooks': [self._progress_hook],
            'ignoreerrors': False,
            'verbose': False,
        }
        
        # 根據格式和品質設置下載選項
        if format_option == 'mp3':
            # MP3 音頻下載選項
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality_option.replace('kbps', ''),
                }],
            })
            
            # 如果需要嵌入縮圖
            if embed_thumbnail:
                ydl_opts['writethumbnail'] = True
                ydl_opts['postprocessors'].append({
                    'key': 'EmbedThumbnail',
                })
                
        else:
            # MP4 視頻下載選項 - 智能降級邏輯
            # 使用更智能的格式選擇邏輯，當所選品質不可用時，自動降級到較低品質
            if quality_option == '360p':
                format_str = 'bestvideo[height=360][ext=mp4]+bestaudio[ext=m4a]/best[height=360][ext=mp4]/best[ext=mp4]'
            elif quality_option == '480p':
                # 首選480p，如果沒有則降級到360p
                format_str = 'bestvideo[height=480][ext=mp4]+bestaudio[ext=m4a]/best[height=480][ext=mp4]/bestvideo[height=360][ext=mp4]+bestaudio[ext=m4a]/best[height=360][ext=mp4]/best[ext=mp4]'
            elif quality_option == '720p':
                # 首選720p，如果沒有則依次降級到480p、360p
                format_str = 'bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a]/best[height=720][ext=mp4]/bestvideo[height=480][ext=mp4]+bestaudio[ext=m4a]/best[height=480][ext=mp4]/bestvideo[height=360][ext=mp4]+bestaudio[ext=m4a]/best[height=360][ext=mp4]/best[ext=mp4]'
            elif quality_option == '1080p':
                # 首選1080p，如果沒有則依次降級到720p、480p、360p
                format_str = 'bestvideo[height=1080][ext=mp4]+bestaudio[ext=m4a]/best[height=1080][ext=mp4]/bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a]/best[height=720][ext=mp4]/bestvideo[height=480][ext=mp4]+bestaudio[ext=m4a]/best[height=480][ext=mp4]/bestvideo[height=360][ext=mp4]+bestaudio[ext=m4a]/best[height=360][ext=mp4]/best[ext=mp4]'
            elif quality_option == '2K':
                # 首選2K(1440p)，如果沒有則依次降級到1080p、720p、480p、360p
                format_str = 'bestvideo[height=1440][ext=mp4]+bestaudio[ext=m4a]/best[height=1440][ext=mp4]/bestvideo[height=1080][ext=mp4]+bestaudio[ext=m4a]/best[height=1080][ext=mp4]/bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a]/best[height=720][ext=mp4]/bestvideo[height=480][ext=mp4]+bestaudio[ext=m4a]/best[height=480][ext=mp4]/bestvideo[height=360][ext=mp4]+bestaudio[ext=m4a]/best[height=360][ext=mp4]/best[ext=mp4]'
            elif quality_option == '4K':
                # 首選4K(2160p)，如果沒有則依次降級到2K、1080p、720p、480p、360p
                format_str = 'bestvideo[height=2160][ext=mp4]+bestaudio[ext=m4a]/best[height=2160][ext=mp4]/bestvideo[height=1440][ext=mp4]+bestaudio[ext=m4a]/best[height=1440][ext=mp4]/bestvideo[height=1080][ext=mp4]+bestaudio[ext=m4a]/best[height=1080][ext=mp4]/bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a]/best[height=720][ext=mp4]/bestvideo[height=480][ext=mp4]+bestaudio[ext=m4a]/best[height=480][ext=mp4]/bestvideo[height=360][ext=mp4]+bestaudio[ext=m4a]/best[height=360][ext=mp4]/best[ext=mp4]'
            else:
                format_str = 'best[ext=mp4]'
            
            # 添加其他選項
            ydl_opts['format'] = format_str
            # 強制合併視頁和音頁
            ydl_opts['merge_output_format'] = 'mp4'
            
        return ydl_opts
    
    def _embed_thumbnail_to_mp3(self, mp3_file, thumbnail_url):
        """
        將縮圖嵌入到 MP3 文件
        
        Args:
            mp3_file (str): MP3 文件路徑
            thumbnail_url (str): 縮圖 URL
        """
        try:
            # 首先確保文件存在並且是 MP3
            if not os.path.exists(mp3_file) or not mp3_file.endswith('.mp3'):
                return
                
            # 獲取縮圖
            try:
                import requests
                response = requests.get(thumbnail_url)
                if response.status_code != 200:
                    return
                    
                img_data = response.content
                img = Image.open(io.BytesIO(img_data))
                
                # 調整圖片大小
                img = img.resize((500, 500), Image.LANCZOS)
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG')
                img_data = img_bytes.getvalue()
                
            except Exception:
                return
                
            # 嵌入縮圖到 MP3
            try:
                audio = ID3(mp3_file)
            except:
                audio = ID3()
                
            audio.add(APIC(
                encoding=3,  # UTF-8
                mime='image/jpeg',
                type=3,  # 封面
                desc='Cover',
                data=img_data
            ))
            
            audio.save(mp3_file)
            
        except Exception as e:
            print(f"嵌入縮圖錯誤: {e}")
    
    def cancel(self):
        """
        取消當前下載任務
        """
        self.is_downloading = False
        if self.callback:
            self.callback({
                'status': 'cancelled',
                'message': '下載已取消'
            })
