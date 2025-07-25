"""
更新檢查模塊 - 檢查和應用應用程序更新
"""
import json
import os
import sys
import tempfile
import shutil
import zipfile
import subprocess
import threading
import requests
from packaging import version
from tkinter import messagebox

from youtube_downloader.config import APP_VERSION, APP_NAME

# GitHub 相關配置
GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/releases/latest"
GITHUB_REPO_OWNER = "kdwjzh"  # 您的 GitHub 用戶名
GITHUB_REPO_NAME = "youtube-downloader"  # 您的 GitHub 倉庫名


class UpdateChecker:
    """更新檢查器類 - 處理應用程序的更新檢查、下載和安裝"""
    
    def __init__(self, parent=None, callback=None):
        """
        初始化更新檢查器
        
        Args:
            parent: 父窗口，用於顯示消息框
            callback (function): 回調函數，用於通知更新結果
        """
        self.parent = parent
        self.callback = callback
        self.current_version = APP_VERSION
        self.update_info = None
        self.download_path = None
        
    def check_update(self, async_check=True, silent=False):
        """
        檢查更新
        
        Args:
            async_check (bool): 是否異步檢查
            silent (bool): 是否靜默檢查（不顯示無更新消息）
            
        Returns:
            dict: 更新信息字典（如果是同步檢查）
        """
        self.silent = silent
        
        if async_check:
            # 創建異步線程
            update_thread = threading.Thread(target=self._check_update_thread)
            update_thread.daemon = True
            update_thread.start()
            return None
        else:
            return self._check_update()
    
    def _check_update_thread(self):
        """異步檢查更新線程"""
        result = self._check_update()
        # 將靜默標誌添加到結果中
        if isinstance(result, dict):
            result['silent'] = self.silent
        if self.callback:
            self.callback(result)
    
    def _check_update(self):
        """
        從 GitHub 檢查更新
        
        Returns:
            dict: 更新信息字典
        """
        try:
            # 從 GitHub API 獲取最新版本信息
            api_url = GITHUB_API_URL.format(owner=GITHUB_REPO_OWNER, repo=GITHUB_REPO_NAME)
            headers = {"Accept": "application/vnd.github.v3+json"}
            
            try:
                response = requests.get(api_url, headers=headers, timeout=10)
                response.raise_for_status()
                release_info = response.json()
                
                latest_version = release_info.get("tag_name", "v0.0.0").lstrip("v")
                download_url = None
                
                # 尋找 Windows 版本的更新包（zip 文件）
                for asset in release_info.get("assets", []):
                    if asset["name"].endswith(".zip") and "windows" in asset["name"].lower():
                        download_url = asset["browser_download_url"]
                        break
                
                if not download_url and release_info.get("assets", []):
                    # 如果沒有找到 Windows 專用包，使用第一個 zip 文件
                    for asset in release_info.get("assets", []):
                        if asset["name"].endswith(".zip"):
                            download_url = asset["browser_download_url"]
                            break
                
                # 如果還是沒找到，使用 zipball_url
                if not download_url:
                    download_url = release_info.get("zipball_url")
                
                # 檢查是否有更新
                has_update = version.parse(latest_version) > version.parse(self.current_version)
                
                # 更新說明
                release_notes = release_info.get("body", "無版本說明")
                
                result = {
                    "status": "success",
                    "current_version": self.current_version,
                    "latest_version": latest_version,
                    "has_update": has_update,
                    "download_url": download_url if has_update else None,
                    "release_notes": release_notes
                }
                
                self.update_info = result
                
                # 顯示更新提示
                if has_update and self.parent and not self.silent:
                    self._show_update_dialog(result)
                elif not has_update and self.parent and not self.silent:
                    messagebox.showinfo(f"{APP_NAME} - 更新檢查", "您正在使用最新版本！")
                
                return result
                
            except requests.RequestException as e:
                # 如果無法從 GitHub API 獲取數據，提供模擬數據
                if not self.silent:
                    messagebox.showwarning(f"{APP_NAME} - 更新檢查", f"無法連接到更新伺服器：{str(e)}")
                
                return {
                    "status": "error",
                    "error": f"連接錯誤: {str(e)}",
                    "has_update": False
                }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "has_update": False
            }
    
    def _show_update_dialog(self, update_info):
        """
        顯示發現更新的對話框
        
        Args:
            update_info (dict): 更新信息字典
        """
        message = f"發現新版本：v{update_info['latest_version']}\n" + \
                 f"當前版本：v{update_info['current_version']}\n\n" + \
                 f"版本說明：\n{update_info['release_notes'][:500]}...\n\n" + \
                 "是否立即下載並安裝更新？"
        
        if messagebox.askyesno(f"{APP_NAME} - 發現更新", message):
            self.download_and_install_update(update_info['download_url'])
    
    def download_and_install_update(self, download_url):
        """
        下載並安裝更新
        
        Args:
            download_url (str): 更新包下載 URL
        """
        if not download_url:
            messagebox.showerror(f"{APP_NAME} - 更新錯誤", "無效的下載鏈接！")
            return
        
        # 創建下載線程
        download_thread = threading.Thread(
            target=self._download_and_install_thread,
            args=(download_url,)
        )
        download_thread.daemon = True
        download_thread.start()
    
    def _download_and_install_thread(self, download_url):
        """
        下載和安裝更新的線程
        
        Args:
            download_url (str): 更新包下載 URL
        """
        try:
            # 創建臨時目錄
            temp_dir = tempfile.mkdtemp(prefix=f"{APP_NAME}-update-")
            self.download_path = os.path.join(temp_dir, "update.zip")
            
            # 下載更新文件
            if self.parent:
                self.parent.after(0, lambda: messagebox.showinfo(f"{APP_NAME} - 更新", "開始下載更新，請稍候..."))
            
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(self.download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 解壓更新文件
            extract_path = os.path.join(temp_dir, "extracted")
            os.makedirs(extract_path, exist_ok=True)
            
            with zipfile.ZipFile(self.download_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # 查找解壓後的根目錄（GitHub 下載有可能包含一層父目錄）
            root_dirs = [d for d in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, d))]
            source_dir = os.path.join(extract_path, root_dirs[0]) if root_dirs else extract_path
            
            # 創建更新腳本
            self._create_updater_script(source_dir)
            
            if self.parent:
                self.parent.after(0, lambda: messagebox.showinfo(
                    f"{APP_NAME} - 更新準備就緒", 
                    "更新已下載完成。應用程序將關閉，並自動完成更新。"
                ))
                
                # 執行更新並退出
                self.parent.after(1000, self._run_updater)
                
        except Exception as e:
            if self.parent:
                self.parent.after(0, lambda: messagebox.showerror(
                    f"{APP_NAME} - 更新錯誤", 
                    f"更新過程中發生錯誤：\n{str(e)}"
                ))
    
    def _create_updater_script(self, source_dir):
        """
        創建更新腳本
        
        Args:
            source_dir (str): 解壓後的源文件目錄
        """
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        script_path = os.path.join(os.path.dirname(self.download_path), "updater.bat")
        
        with open(script_path, 'w') as f:
            f.write(f"@echo off\n")
            f.write(f"echo 正在更新 {APP_NAME}...\n")
            f.write(f"timeout /t 2 /nobreak >nul\n")  # 等待主程序退出
            f.write(f"xcopy /E /Y \"{source_dir}\\*\" \"{app_dir}\"\n")
            f.write(f"echo 更新完成！\n")
            f.write(f"start "" \"{app_dir}\\run_app.bat\"\n")
        
        self.updater_script = script_path
    
    def _run_updater(self):
        """
        運行更新腳本並退出應用程序
        """
        try:
            # 以管理員身份運行更新腳本
            subprocess.Popen(["cmd.exe", "/c", self.updater_script], 
                          creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            # 退出應用程序
            sys.exit(0)
        except Exception as e:
            messagebox.showerror(f"{APP_NAME} - 更新錯誤", f"無法啟動更新程序：{str(e)}")

