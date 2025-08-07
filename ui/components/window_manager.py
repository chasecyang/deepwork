"""
窗口管理器
负责桌面宠物窗口的基本属性和行为管理
"""
import sys
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPoint


class WindowManager:
    """窗口管理器，负责窗口的基本设置和位置管理"""
    
    def __init__(self, widget: QWidget, config_manager):
        self.widget = widget
        self.config = config_manager
        
    def init_window_properties(self):
        """初始化窗口属性"""
        # 设置窗口标志：无边框、置顶
        window_flags = (
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Window
        )
        
        # Windows平台需要额外的标志来确保透明效果
        if sys.platform == "win32":
            window_flags |= Qt.WindowType.Tool
        
        self.widget.setWindowFlags(window_flags)
        
        # 设置窗口属性 - 关键：透明背景属性
        self.widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.widget.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        
        # 平台特定属性
        if sys.platform == "darwin":  # macOS
            self.widget.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        elif sys.platform == "win32":  # Windows
            # Windows特定的透明优化
            self.widget.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        
        # 设置窗口标题
        self.widget.setWindowTitle("Deepwork")
        
        # 设置样式表
        self.widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        
    def load_window_geometry(self):
        """加载窗口位置和大小"""
        width = self.config.get("window_width", 100)
        height = self.config.get("window_height", 100)
        x = self.config.get("window_x", 100)
        y = self.config.get("window_y", 100)
        
        self.widget.setGeometry(x, y, width, height)
        
    def update_transparency(self):
        """更新窗口透明度"""
        transparency = self.config.get("transparency", 0.9)
        self.widget.setWindowOpacity(transparency)
        
    def save_position(self):
        """保存当前窗口位置"""
        self.config.set("window_x", self.widget.x())
        self.config.set("window_y", self.widget.y())
        
    def update_topmost(self, topmost: bool):
        """更新窗口置顶状态"""
        base_flags = (
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Window
        )
        
        # Windows平台需要额外的标志
        if sys.platform == "win32":
            base_flags |= Qt.WindowType.Tool
        
        if topmost:
            self.widget.setWindowFlags(base_flags | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.widget.setWindowFlags(base_flags)
        
        # 重新设置窗口属性 - 关键：透明背景属性
        self.widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.widget.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        
        # 平台特定属性
        if sys.platform == "darwin":  # macOS
            self.widget.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        elif sys.platform == "win32":  # Windows
            # Windows特定的透明优化
            self.widget.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
