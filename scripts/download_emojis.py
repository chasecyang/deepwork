#!/usr/bin/env python3
"""
下载 Noto Emoji Animation 动画表情的脚本
"""
import os
import urllib.request
import sys
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
EMOJI_DIR = PROJECT_ROOT / "assets" / "animated_emojis"

# 动画表情映射表（Unicode代码点到名称）
EMOJI_ANIMATIONS = {
    # 基础表情
    "smile": "1f642",        # 😂 微笑
    "laugh": "1f606",        # 😆 大笑
    "joy": "1f602",          # 😂 笑哭
    "heart_eyes": "1f60d",   # 😍 心形眼
    "wink": "1f609",         # 😉 眨眼
    "grin": "1f601",         # 😁 露齿笑
    "smiling_face": "1f60a", # 😊 微笑脸
    
    # 状态表情
    "thinking": "1f914",     # 🤔 思考
    "sleeping": "1f634",     # 😴 睡觉
    "cool": "1f60e",         # 😎 酷
    "party": "1f973",        # 🥳 派对
    "love": "1f970",         # 🥰 爱心脸
    "confused": "1f615",     # 😕 困惑
    "surprised": "1f62e",    # 😮 惊讶
    
    # 手势
    "thumbs_up": "1f44d",    # 👍 点赞
    "clap": "1f44f",         # 👏 鼓掌
    "wave": "1f44b",         # 👋 挥手
    "ok_hand": "1f44c",      # 👌 OK手势
    
    # 心形和爱
    "heart": "2764",         # ❤️ 红心
    "sparkling_heart": "1f496",  # 💖 闪亮心形
    
    # 其他有趣的表情
    "fire": "1f525",         # 🔥 火
    "star": "2b50",          # ⭐ 星星
    "rocket": "1f680",       # 🚀 火箭
}

def create_emoji_dir():
    """创建表情目录"""
    EMOJI_DIR.mkdir(parents=True, exist_ok=True)
    print(f"创建表情目录: {EMOJI_DIR}")

def download_emoji_gif(emoji_name, unicode_code):
    """
    下载单个动画表情GIF
    
    注意：这里的URL是示例，实际的 Noto Emoji Animation 可能需要不同的下载方式
    """
    # 尝试多个可能的URL格式
    possible_urls = [
        f"https://fonts.gstatic.com/s/e/notoemoji/latest/{unicode_code}/512.gif",
        f"https://raw.githubusercontent.com/googlefonts/noto-emoji/main/animated/{unicode_code}.gif",
        f"https://github.com/googlefonts/noto-emoji-animation/raw/main/gif/{unicode_code}.gif",
    ]
    
    save_path = EMOJI_DIR / f"{emoji_name}.gif"
    
    for url in possible_urls:
        try:
            print(f"尝试下载 {emoji_name} 从 {url}")
            urllib.request.urlretrieve(url, save_path)
            
            # 检查文件是否有效（大小大于1KB）
            if save_path.stat().st_size > 1024:
                print(f"✅ 成功下载 {emoji_name}")
                return True
            else:
                save_path.unlink()  # 删除无效文件
                
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            if save_path.exists():
                save_path.unlink()
            continue
    
    print(f"❌ 所有URL都无法下载 {emoji_name}")
    return False

def download_all_emojis():
    """下载所有动画表情"""
    create_emoji_dir()
    
    success_count = 0
    total_count = len(EMOJI_ANIMATIONS)
    
    print(f"开始下载 {total_count} 个动画表情...")
    
    for emoji_name, unicode_code in EMOJI_ANIMATIONS.items():
        if download_emoji_gif(emoji_name, unicode_code):
            success_count += 1
    
    print(f"\n下载完成: {success_count}/{total_count} 个表情成功")
    
    if success_count == 0:
        print("没有成功下载任何动画表情...")
    
    return success_count

def main():
    """主函数"""
    print("下载 Noto Emoji Animation 动画表情")
    print("=" * 50)
    download_all_emojis()
    
    print("\n使用说明:")
    print("1. 如果下载失败，可以手动下载动画表情文件")
    print("2. 将GIF文件放在 assets/animated_emojis/ 目录下")
    print("3. 文件命名格式: {表情名}.gif")

if __name__ == "__main__":
    main()
