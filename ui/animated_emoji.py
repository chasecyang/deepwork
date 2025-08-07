"""
动画表情管理模块
支持 Noto Emoji Animation 的动画表情
"""
import os
import random
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie, QPixmap


class AnimatedEmojiLabel(QLabel):
    """支持动画表情的标签"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._movie = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 动画表情资源路径
        from utils.common import PathUtils
        self.emoji_dir = PathUtils.get_assets_dir() / 'animated_emojis'
        
    def set_animated_emoji(self, emoji_name):
        """
        设置动画表情
        
        Args:
            emoji_name: 表情名称，可以包含或不包含.gif扩展名
        """
        # 处理文件名，确保有.gif扩展名
        if not emoji_name.endswith('.gif'):
            gif_path = self.emoji_dir / f"{emoji_name}.gif"
        else:
            gif_path = self.emoji_dir / emoji_name
        
        if gif_path.exists():
            # 停止之前的动画
            if self._movie:
                self._movie.stop()
                
            # 创建新的动画
            self._movie = QMovie(str(gif_path))
            # 使用固定的小尺寸，而不是 self.size()
            from PySide6.QtCore import QSize
            self._movie.setScaledSize(QSize(64, 64))  # 64x64 像素，比窗口稍小
            self.setMovie(self._movie)
            self._movie.start()
            
            # 清除文本
            self.setText("")
            return True
        else:
            # 如果没有动画文件，显示文本提示
            if self._movie:
                self._movie.stop()
                self._movie = None
            self.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: gray;
                    background-color: transparent;
                }
            """)
            self.setText(f"❌ {emoji_name}")
            return False
        
    def set_random_animated_emoji(self):
        """设置随机动画表情"""
        # 可用的动画表情列表（根据成功下载的文件）
        animated_emojis = [
            "smile", "laugh", "joy", "heart_eyes", "wink", "grin", "smiling_face",
            "thinking", "sleeping", "cool", "party", "love", "confused", "surprised",
            "thumbs_up", "clap", "wave", "ok_hand", "heart", "sparkling_heart", 
            "fire", "rocket"
        ]
        
        emoji_name = random.choice(animated_emojis)
        self.set_animated_emoji(emoji_name)
