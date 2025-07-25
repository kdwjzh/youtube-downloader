"""
創建預設縮圖圖片
"""
from PIL import Image, ImageDraw, ImageFont
import os
import sys

def create_default_thumbnail():
    """創建一個預設的縮圖圖片，顯示 YouTube 標誌和提示文字"""
    # 圖片尺寸
    width, height = 320, 180
    
    # 創建一個灰色背景的圖片
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # 繪製文字
    text = "顯示該URL影片縮圖"
    
    # 嘗試加載字體（如果失敗則使用默認字體）
    try:
        # 注意：這裡我們使用相對路徑，實際使用時可能需要調整
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    
    # 獲取文字尺寸
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    
    # 居中繪製文字
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, fill=(100, 100, 100), font=font)
    
    # 保存圖片
    img_path = os.path.join(os.path.dirname(__file__), "default_thumbnail.png")
    img.save(img_path)
    print(f"預設縮圖已創建：{img_path}")
    
    return img_path

if __name__ == "__main__":
    create_default_thumbnail()
