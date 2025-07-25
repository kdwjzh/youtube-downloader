"""
工具函數模組 - 包含各種輔助函數
"""
import os
import re
import shutil
from pathlib import Path


def validate_youtube_url(url):
    """
    驗證 YouTube URL 是否有效
    
    Args:
        url (str): 要驗證的 URL
        
    Returns:
        bool: URL 是否有效
    """
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    match = re.match(youtube_regex, url)
    return match is not None


def get_default_download_path():
    """
    獲取默認下載路徑
    
    Returns:
        str: 默認下載路徑
    """
    return os.path.join(os.path.expanduser('~'), 'Downloads')


def format_filesize(bytes, decimals=2):
    """
    將字節大小格式化為人類可讀的格式
    
    Args:
        bytes (int): 文件大小（字節）
        decimals (int): 小數點位數
        
    Returns:
        str: 格式化後的文件大小
    """
    if bytes == 0:
        return '0 B'
    
    size_names = ('B', 'KB', 'MB', 'GB', 'TB')
    i = 0
    while bytes >= 1024 and i < len(size_names) - 1:
        bytes /= 1024
        i += 1
    
    return f"{bytes:.{decimals}f} {size_names[i]}"


def format_time(seconds):
    """
    將秒數格式化為 HH:MM:SS 格式
    
    Args:
        seconds (int): 秒數
        
    Returns:
        str: 格式化後的時間
    """
    if not seconds:
        return "00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def check_disk_space(path, required_space):
    """
    檢查磁盤是否有足夠空間
    
    Args:
        path (str): 路徑
        required_space (int): 所需空間大小（字節）
        
    Returns:
        bool: 是否有足夠空間
    """
    if not os.path.exists(path):
        path = os.path.dirname(path)
    
    free_space = shutil.disk_usage(path).free
    return free_space >= required_space


def ensure_dir_exists(directory):
    """
    確保目錄存在，如不存在則創建
    
    Args:
        directory (str): 目錄路徑
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def sanitize_filename(filename):
    """
    清理文件名，移除不允許的字符
    
    Args:
        filename (str): 原始文件名
        
    Returns:
        str: 清理後的文件名
    """
    # 替換 Windows 不允許的文件名字符
    invalid_chars = r'[\\/:*?"<>|]'
    return re.sub(invalid_chars, '_', filename)
