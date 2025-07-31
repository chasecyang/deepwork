"""
关于标签页
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt
from ui.theme import ModernTheme


class AboutTab(QWidget):
    """关于标签页"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 应用标题
        title_label = QLabel("桌面宠物助手")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {ModernTheme.COLORS['primary']};
                margin: 10px 0;
            }}
        """)
        layout.addWidget(title_label)
        
        # 应用描述
        description_text = """一个简洁的桌面工具应用

支持动画表情
集成AI模型
简洁界面设计
个性化设置

版本: 1.0.0
作者: DeepWork Team"""
        
        description_label = QTextEdit()
        description_label.setPlainText(description_text)
        description_label.setReadOnly(True)
        description_label.setMaximumHeight(200)
        description_label.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                border: 1px solid {ModernTheme.COLORS['border_light']};
                border-radius: {ModernTheme.RADIUS['base']};
                padding: 15px;
                font-size: {ModernTheme.FONTS['size_base']};
                color: {ModernTheme.COLORS['text_primary']};
                line-height: 1.6;
            }}
        """)
        layout.addWidget(description_label)
        
        # 添加一些间距
        layout.addStretch()
    
    def load_settings(self, config):
        """加载设置 - 关于页面不需要加载设置"""
        pass
    
    def get_settings(self) -> dict:
        """获取设置 - 关于页面不返回设置"""
        return {}