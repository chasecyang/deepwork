"""
基础设置对话框类
提供公共功能和配置
"""

from PySide6.QtWidgets import QDialog, QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from typing import Optional, Callable
from ui.theme import ModernTheme


class BaseSettingsDialog(QDialog):
    """设置对话框基类"""
    
    def __init__(self, parent: QWidget, config_manager, 
                 on_settings_changed: Optional[Callable] = None):
        super().__init__(parent)
        self.config = config_manager
        self.on_settings_changed = on_settings_changed
        
        # 设置基本属性
        self.setup_window()
        self.setup_animations()
    
    def setup_window(self):
        """设置窗口基本属性"""
        self.setWindowTitle("设置")
        self.setFixedSize(750, 650)
        
        # 设置窗口标志
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # 应用现代化样式
        self.setStyleSheet(ModernTheme.get_dialog_style())
    
    def setup_animations(self):
        """设置动画效果"""
        # 初始透明度为0，准备淡入动画
        self.setWindowOpacity(0.0)
        
        # 创建淡入动画
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def show(self):
        """显示对话框"""
        self.load_settings()
        super().show()
        # 启动淡入动画
        if hasattr(self, 'fade_animation'):
            self.fade_animation.start()
    
    def center_on_parent(self):
        """将对话框居中显示在父窗口上"""
        parent = self.parent()
        if isinstance(parent, QWidget):
            parent_geometry = parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def load_settings(self):
        """加载设置 - 子类需要实现"""
        pass
    
    def save_settings(self):
        """保存设置 - 子类需要实现"""
        pass