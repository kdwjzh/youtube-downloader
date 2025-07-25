"""
播放列表處理模組 - 處理 YouTube 播放列表的獲取和下載
"""
import threading
import yt_dlp
import re
import os


class PlaylistProcessor:
    """播放列表處理器類"""
    
    def __init__(self, callback=None):
        """
        初始化播放列表處理器
        
        Args:
            callback (function): 回調函數，用於更新 UI
        """
        self.callback = callback
        self.is_processing = False
        self.current_task = None
        
    def extract_playlist_info(self, url, async_extract=True):
        """
        提取播放列表信息
        
        Args:
            url (str): YouTube 播放列表 URL
            async_extract (bool): 是否異步提取
            
        Returns:
            dict: 播放列表信息字典 (如果同步) 或 None (如果異步)
        """
        # 檢查 URL 是否是播放列表
        if not self._is_playlist_url(url):
            if self.callback:
                self.callback({
                    'status': 'error',
                    'error': '非播放列表 URL'
                })
            return None
        
        # 通知開始提取
        if self.callback:
            self.callback({
                'status': 'extracting',
                'message': '正在獲取播放列表信息...'
            })
        
        if async_extract:
            # 啟動異步提取線程
            extract_thread = threading.Thread(
                target=self._extract_thread,
                args=(url,)
            )
            extract_thread.daemon = True
            extract_thread.start()
            return None
        else:
            # 同步提取
            return self._extract_info(url)
    
    def _extract_thread(self, url):
        """
        異步提取線程執行函數
        
        Args:
            url (str): YouTube 播放列表 URL
        """
        try:
            info = self._extract_info(url)
            
            if self.callback:
                self.callback({
                    'status': 'complete',
                    'playlist_info': info
                })
        except Exception as e:
            if self.callback:
                self.callback({
                    'status': 'error',
                    'error': str(e)
                })
    
    def _extract_info(self, url):
        """
        提取播放列表信息的核心方法
        
        Args:
            url (str): YouTube 播放列表 URL
            
        Returns:
            dict: 播放列表信息字典
        """
        # 清理 URL，確保其符合播放列表格式
        url = self._clean_playlist_url(url)
        
        # 第一步：先獲取播放列表的基本信息
        print(f"正在提取播放列表基本信息：{url}")
        basic_opts = {
            'extract_flat': 'in_playlist',  # 僅提取基本信息
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }
        
        try:
            # 先使用平面提取獲取播放列表基本信息
            with yt_dlp.YoutubeDL(basic_opts) as ydl:
                basic_info = ydl.extract_info(url, download=False)
                
                # 如果沒有播放列表信息，則返回錯誤
                if not basic_info or not basic_info.get('entries'):
                    print("無法獲取播放列表基本信息")
                    if self.callback:
                        self.callback({
                            'status': 'error',
                            'error': '播放列表中沒有視頁或此URL不是播放列表'
                        })
                    return None
                
                # 將播放列表的基本信息保存下來
                playlist_info = {
                    'id': basic_info.get('id', ''),
                    'title': basic_info.get('title', '未知播放列表'),
                    'uploader': basic_info.get('uploader', '未知上傳者'),
                    'webpage_url': basic_info.get('webpage_url', ''),
                    'entries': []
                }
                
                # 第二步：逐個提取視頻詳細信息以確保有URL
                print(f"提取播放列表中的視頻詳細信息...")
                entries = basic_info.get('entries', [])
                total_entries = len(entries)
                
                # 設置用於提取視頻詳細信息的選項
                detail_opts = {
                    'skip_download': True,
                    'quiet': True,
                    'no_warnings': True,
                }
                
                # 用於提取詳細信息的YoutubeDL實例
                with yt_dlp.YoutubeDL(detail_opts) as detail_ydl:
                    for i, entry in enumerate(entries):
                        try:
                            # 如果條目中已經有URL，則直接使用
                            video_url = entry.get('url') or entry.get('webpage_url')
                            if not video_url and 'id' in entry:
                                # 如果沒有URL但有ID，則使用ID建構完整URL
                                video_id = entry.get('id')
                                video_url = f"https://www.youtube.com/watch?v={video_id}"
                            
                            if video_url:
                                print(f"[視頻 {i+1}/{total_entries}] 提取詳細信息: {video_url}")
                                # 提取視頻詳細信息
                                video_info = detail_ydl.extract_info(video_url, download=False, process=False)
                                
                                # 確保有必要的信息
                                if video_info:
                                    # 移除較大的欄位以節省內存
                                    if 'formats' in video_info:
                                        del video_info['formats']
                                    
                                    # 添加視頻信息到播放列表項目中
                                    playlist_info['entries'].append({
                                        'id': video_info.get('id', ''),
                                        'title': video_info.get('title', f'未知標題 {i+1}'),
                                        'webpage_url': video_info.get('webpage_url', video_url),
                                        'url': video_info.get('url', video_url),
                                        'duration': video_info.get('duration', 0),
                                        'thumbnail': video_info.get('thumbnail', '')
                                    })
                                    print(f"[視頻 {i+1}/{total_entries}] 成功提取: {video_info.get('title', '')}")
                        except Exception as video_e:
                            print(f"[視頻 {i+1}/{total_entries}] 提取失敗: {str(video_e)}")
                            # 繼續處理下一個視頻，而不是中斷整個播放列表的提取
                
                # 計算播放列表總數和總時長
                playlist_info['video_count'] = len(playlist_info['entries'])
                
                print(f"\033[1;36m成功提取播放列表中的 {playlist_info['video_count']} 個視頻，可以開始下載Youtube播放列表了音樂了~\033[0m")
                return playlist_info
                
        except Exception as e:
            print(f"提取播放列表信息失敗：{str(e)}")
            import traceback
            traceback.print_exc()
            if self.callback:
                self.callback({
                    'status': 'error',
                    'error': f'無法獲取播放列表信息: {str(e)}'
                })
            raise
    
    def _process_playlist_info(self, info_dict):
        """
        處理播放列表信息字典
        
        Args:
            info_dict (dict): yt-dlp 提供的原始信息字典
            
        Returns:
            dict: 處理後的播放列表信息字典
        """
        if not info_dict:
            return None
            
        print(f"播放列表原始信息: {list(info_dict.keys())}")
        
        if 'title' in info_dict:
            print(f"播放列表標題: {info_dict.get('title')}")
        if 'id' in info_dict:
            print(f"播放列表ID: {info_dict.get('id')}")
        if 'playlist_id' in info_dict:
            print(f"播放列表ID (playlist_id): {info_dict.get('playlist_id')}")
        if '_type' in info_dict:
            print(f"資料類型: {info_dict.get('_type')}")
        if 'entries' in info_dict:
            print(f"包含條目數量: {len(info_dict.get('entries', []))}")
        if 'webpage_url' in info_dict:
            print(f"網頁URL: {info_dict.get('webpage_url')}")
        # 如果是直接視頻頁面，還需要檢查是否有playlist_title
        # 判斷是否是播放列表格式
        is_playlist = info_dict.get('_type', '') == 'playlist'
        
        # 初始化播放列表信息
        title = info_dict.get('title', '未知播放列表')
        
        # 如果有playlist_title，優先使用它作為播放列表標題
        if 'playlist_title' in info_dict:
            print(f"播放列表標題 (playlist_title): {info_dict.get('playlist_title')}")
            title = info_dict.get('playlist_title', title)
            
        # 提取基本信息
        playlist_info = {
            'id': info_dict.get('id', ''),
            'title': title,
            'uploader': info_dict.get('uploader', '未知上傳者'),
            'webpage_url': info_dict.get('webpage_url', ''),
            'entries': []
        }
        
        # 提取視頁條目
        entries = info_dict.get('entries', [])
        
        # 如果不是播放列表但有播放列表ID，可能是單個視頻中的播放列表參考
        if not is_playlist and not entries and 'playlist_id' in info_dict:
            # 重新建構播放列表URL並取得完整播放列表
            playlist_id = info_dict.get('playlist_id')
            playlist_url = f'https://www.youtube.com/playlist?list={playlist_id}'
            try:
                print(f"嘗試重新獲取完整播放列表: {playlist_url}")
                with yt_dlp.YoutubeDL({'extract_flat': 'in_playlist', 'quiet': True}) as ydl:
                    new_info = ydl.extract_info(playlist_url, download=False)
                    if new_info and new_info.get('entries'):
                        info_dict = new_info
                        entries = info_dict.get('entries', [])
                        playlist_info['title'] = info_dict.get('title', playlist_info['title'])
                        playlist_info['uploader'] = info_dict.get('uploader', playlist_info['uploader'])
            except Exception as e:
                print(f"重新獲取播放列表失敗: {str(e)}")
        
        # 紀錄該播放列表有多少視頻
        print(f"播放列表中的視頻數量: {len(entries)}")
        
        # 如果沒有條目但有playlist_id，可能是單個視頻中的播放列表參考
        for entry in entries:
            if entry:
                video_info = {
                    'id': entry.get('id', ''),
                    'title': entry.get('title', '未知標題'),
                    'url': entry.get('url', ''),
                    'webpage_url': entry.get('webpage_url', ''),
                    'duration': entry.get('duration', 0),
                    'thumbnail': entry.get('thumbnail', '')
                }
                
                playlist_info['entries'].append(video_info)
        
        # 計算播放列表總數和總時長
        playlist_info['video_count'] = len(playlist_info['entries'])
        
        return playlist_info
    
    def _is_playlist_url(self, url):
        """
        檢查 URL 是否是播放列表
        
        Args:
            url (str): 要檢查的 URL
            
        Returns:
            bool: 是否是播放列表 URL
        """
        # YouTube 播放列表 URL 通常包含 "list=" 參數
        # 並且不是單個視頻 (不包含 "watch?v=" 或包含 "&index=")
        if 'list=' not in url:
            return False
            
        # 如果URL含有 "watch?v=" 且沒有 "&index="，可能是影片附帶的推薦播放列表而非完整播放列表
        # 我們將其視為有效播放列表，讓 yt-dlp 進一步處理
        return True
        
    def _clean_playlist_url(self, url):
        """
        清理播放列表 URL，確保其格式正確
        
        Args:
            url (str): 原始 URL
            
        Returns:
            str: 清理後的 URL
        """
        # 移除URL中的多餘參數，只保留必要的部分
        if 'list=' in url:
            # 提取播放列表ID
            match = re.search(r'list=([^&]+)', url)
            if match:
                playlist_id = match.group(1)
                # 構建乾淨的播放列表URL
                if 'youtube.com/playlist' in url:
                    return f'https://www.youtube.com/playlist?list={playlist_id}'
                else:
                    # 如果是視頻中的播放列表，保留視頻ID
                    video_match = re.search(r'v=([^&]+)', url)
                    if video_match:
                        video_id = video_match.group(1)
                        return f'https://www.youtube.com/watch?v={video_id}&list={playlist_id}'
                    else:
                        return f'https://www.youtube.com/playlist?list={playlist_id}'
        return url
    
    def batch_download(self, playlist_info, output_path, format_option, quality_option, embed_thumbnail=False, downloader=None):
        """
        批量下載播放列表
        
        Args:
            playlist_info (dict): 播放列表信息字典
            output_path (str): 輸出路徑
            format_option (str): 格式選項 (mp4/mp3)
            quality_option (str): 品質選項
            embed_thumbnail (bool): 是否嵌入縮圖
            downloader (YouTubeDownloader): 下載器實例
            
        Returns:
            threading.Thread: 下載線程
        """
        # 先檢查是否有處理中的任務
        print(f"批量下載狀態檢查: is_processing={self.is_processing}, has_current_task={self.current_task is not None}")
        
        if self.is_processing:
            if self.callback:
                self.callback({
                    'status': 'error',
                    'error': '已有批量下載任務正在進行'
                })
            return None
        
        # 確保清除之前的狀態
        if self.current_task and self.current_task.is_alive():
            print("存在未結束的下載線程，嘗試結束它")
            try:
                self.cancel()  # 嘗試取消之前的任務
                self.current_task.join(timeout=1.0)  # 等待最多1秒讓它結束
            except:
                print("取消之前的任務失敗，強制繼續")
            finally:
                self.current_task = None
        
        # 設置處理狀態
        self.is_processing = True
        print("設置 is_processing = True")
        
        # 通知開始下載
        if self.callback:
            self.callback({
                'status': 'starting',
                'message': '正在準備批量下載...',
                'total_videos': len(playlist_info.get('entries', []))
            })
        
        # 創建下載線程
        try:
            print("創建下載線程")
            download_thread = threading.Thread(
                target=self._batch_download_thread,
                args=(playlist_info, output_path, format_option, quality_option, embed_thumbnail, downloader)
            )
            
            # 啟動線程
            download_thread.daemon = True
            download_thread.start()
            self.current_task = download_thread
            print("下載線程已啟動")
            
            return download_thread
        except Exception as e:
            print(f"創建下載線程失敗: {str(e)}")
            self.is_processing = False
            if self.callback:
                self.callback({
                    'status': 'error',
                    'error': f'創建下載線程失敗: {str(e)}'
                })
            return None
    
    def _batch_download_thread(self, playlist_info, output_path, format_option, quality_option, embed_thumbnail, downloader):
        """
        批量下載線程執行函數
        
        Args:
            playlist_info (dict): 播放列表信息字典
            output_path (str): 輸出路徑
            format_option (str): 格式選項 (mp4/mp3)
            quality_option (str): 品質選項
            embed_thumbnail (bool): 是否嵌入縮圖
            downloader (YouTubeDownloader): 下載器實例
        """
        try:
            print(f"批量下載線程開始: 格式={format_option}, 品質={quality_option}, 輸出路徑={output_path}")
            print(f"播放列表信息: 標題={playlist_info.get('title', '')}, ID={playlist_info.get('id', '')}")
            
            # 確保輸出目錄存在
            try:
                os.makedirs(output_path, exist_ok=True)
                print(f"確保輸出目錄存在: {output_path}")
            except Exception as e:
                print(f"創建輸出目錄失敗: {str(e)}")
                if self.callback:
                    self.callback({
                        'status': 'error',
                        'error': f'創建輸出目錄失敗: {str(e)}'
                    })
                return
            
            # 確保有視頻條目
            entries = playlist_info.get('entries', [])
            if not entries:
                print("沒有視頻條目可下載")
                if self.callback:
                    self.callback({
                        'status': 'error',
                        'error': '沒有視頻條目可下載'
                    })
                return
                
            total_videos = len(entries)
            completed_videos = 0
            print(f"播放列表共有 {total_videos} 個視頻待下載")
            
            # 檢查下載器
            if not downloader:
                print("下載器實例為空")
                if self.callback:
                    self.callback({
                        'status': 'error',
                        'error': '下載器初始化失敗'
                    })
                return
                
            # 創建下載完成的回調函數
            def download_callback(info):
                nonlocal completed_videos
                status = info.get('status', '')
                print(f"接收到下載回調: {status}")
                
                if status == 'complete':
                    completed_videos += 1
                    print(f"完成一個視頻下載: {completed_videos}/{total_videos}")
                    
                    # 添加到歷史記錄的信息
                    filename = info.get('filename', '')
                    video_info = info.get('info', {})
                    
                    # 更新進度
                    if self.callback:
                        self.callback({
                            'status': 'downloading',
                            'message': f'正在下載播放列表... ({completed_videos}/{total_videos})',
                            'progress': completed_videos / total_videos,
                            'completed_videos': completed_videos,
                            'total_videos': total_videos,
                            'filename': filename,  # 文件名
                            'video_info': video_info,  # 視頻信息
                            'format': format_option,  # 格式
                            'quality': quality_option,  # 品質
                            'add_to_history': True  # 標記為需要添加到歷史記錄
                        })
                elif status == 'error':
                    error_msg = info.get('error', '未知錯誤')
                    print(f"視頻下載錯誤: {error_msg}")
                
                # 將下載器的回調信息傳遞給我們的回調
                if self.callback:
                    self.callback(info)
            
            # 依次下載每個視頻
            for i, video in enumerate(entries):
                if not self.is_processing:
                    # 如果任務被取消，則退出
                    print("批量下載任務被取消")
                    break
                
                # 獲取視頻 URL
                video_url = video.get('webpage_url', '')
                video_title = video.get('title', f'未知標題 {i+1}')
                
                if not video_url:
                    print(f"視頻 {i+1} 沒有可用的URL，跳過")
                    continue
                
                print(f"開始下載視頻 {i+1}/{total_videos}: {video_title}")
                print(f"視頻URL: {video_url}")
                
                # 更新狀態
                if self.callback:
                    self.callback({
                        'status': 'downloading',
                        'message': f'正在下載: {video_title} ({i+1}/{total_videos})',
                        'progress': i / total_videos if total_videos > 0 else 0,
                        'current_video': i+1,
                        'total_videos': total_videos
                    })
                
                # 確保下載器就緒
                if downloader.is_downloading:
                    print("下載器已經在下載中，重置它")
                    downloader.is_downloading = False
                    if downloader.current_task and downloader.current_task.is_alive():
                        print("嘗試等待上一個下載任務結束")
                        try:
                            downloader.current_task.join(timeout=1.0)
                        except:
                            print("等待上一個下載任務失敗，繼續")
                
                # 設置臨時回調
                original_callback = downloader.callback
                downloader.callback = download_callback
                
                try:
                    # 下載視頻
                    print(f"調用下載器下載視頻: {video_url}")
                    downloader.download(
                        url=video_url,
                        output_path=output_path,
                        format_option=format_option,
                        quality_option=quality_option,
                        embed_thumbnail=embed_thumbnail
                    )
                    
                    # 等待下載完成
                    if downloader.current_task:
                        print("等待下載完成...")
                        downloader.current_task.join()
                        print("視頻下載結束")
                except Exception as e:
                    print(f"視頻下載過程中發生錯誤: {str(e)}")
                    # 如果是單個視頻下載失敗，我們可以繼續其他視頻
                    pass
                finally:
                    # 恢復原始回調
                    downloader.callback = original_callback
                    # 重置下載器狀態以確保下一個視頻可以下載
                    downloader.is_downloading = False
            
            # 通知完成
            print(f"批量下載完成，共 {completed_videos}/{total_videos} 個視頻")
            if self.callback:
                # 特意向訂閱者發送完成狀態，並加入downloaded=True表示是下載完成而非信息提取完成
                self.callback({
                    'status': 'complete', 
                    'message': f'播放列表下載完成 ({completed_videos}/{total_videos})',
                    'completed_videos': completed_videos,
                    'total_videos': total_videos,
                    'downloaded': True  # 添加標記表示下載完成與信息提取完成不同
                })
                
        except Exception as e:
            print(f"批量下載線程發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()  # 印出完整的堆疊追蹤
            if self.callback:
                self.callback({
                    'status': 'error',
                    'error': str(e)
                })
        finally:
            print("重置批量下載狀態: is_processing = False")
            self.is_processing = False
    
    def cancel(self):
        """取消當前批量下載任務"""
        self.is_processing = False
        if self.callback:
            self.callback({
                'status': 'cancelled',
                'message': '批量下載已取消'
            })
