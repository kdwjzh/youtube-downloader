# YouTube 下載器

這是一個基於 Python 和 CustomTkinter 開發的 YouTube 影片下載工具，提供了簡潔美觀的圖形用戶界面，讓您輕鬆下載 YouTube 影片和音頻。

## 功能特點

- 支持下載 YouTube 影片為 MP4 格式
- 支持提取 YouTube 音頻為 MP3 格式
- 支持批量下載播放列表
- 支持下載 YouTube Shorts
- 多種影片解析度選擇（360p 到 4K）-> 若沒有該解析度則下載最高解析度
- 多種音頻品質選擇（128kbps 到 320kbps）
- 顯示影片縮圖和基本信息
- 可選擇將縮圖嵌入到音頻文件
- 實時顯示下載進度和速度
- 現代化界面設計
- 支持自定義下載路徑

## 安裝與使用

### 安裝依賴

此應用程序使用虛擬環境來管理依賴。請按照以下步驟安裝：

```bash
# 創建虛擬環境
python -m venv venv

# 激活虛擬環境
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 運行應用程序

```bash
# 確保虛擬環境已激活
python main.py
```

## 使用方法

1. 複製 YouTube 視頻 URL
2. 貼上到應用程序的網址輸入框
3. 選擇下載格式（MP3 或 MP4）
4. 選擇下載品質
5. 選擇保存路徑
6. 點擊「開始下載」按鈕

## 技術架構

- **GUI 框架**：CustomTkinter (現代化的 Tkinter 替代方案)
- **下載核心**：yt-dlp Python 庫
- **圖像處理**：Pillow (PIL)
- **異步處理**：threading
- **網路請求**：requests

## 系統要求

- Python 3.7 或更高版本
