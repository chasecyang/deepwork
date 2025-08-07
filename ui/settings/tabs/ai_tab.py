"""
AI配置主标签页
包含自动检测和手动配置两个子标签页
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .ai_auto_tab import AIAutoDetectionTab
from .ai_manual_tab import AIManualConfigTab


class AISettingsTab(QWidget):
    """AI配置主标签页"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距让子tab占满
        main_layout.setSpacing(0)
        
        # 创建子标签页组件
        self.sub_tab_widget = QTabWidget()
        
        # 创建自动检测和手动配置子标签页
        self.auto_tab = AIAutoDetectionTab(self)
        self.sub_tab_widget.addTab(self.auto_tab, "🔍 自动检测")
        
        self.manual_tab = AIManualConfigTab(self)
        self.sub_tab_widget.addTab(self.manual_tab, "⚙️ 手动配置")
        
        # 设置默认选中自动检测tab
        self.sub_tab_widget.setCurrentIndex(0)
        
        main_layout.addWidget(self.sub_tab_widget)
    
    def load_settings(self, config):
        """加载设置"""
        # 只需要加载手动配置tab的设置，自动检测tab不需要持久化设置
        self.manual_tab.load_settings(config)
    
    def get_settings(self) -> dict:
        """获取设置"""
        # 只从手动配置tab获取设置
        return self.manual_tab.get_settings()
    
    def apply_auto_config(self, config):
        """应用自动检测的配置"""
        # 将配置应用到手动配置tab
        self.manual_tab.apply_config(config)
        
        # 切换到手动配置tab让用户查看
        self.sub_tab_widget.setCurrentWidget(self.manual_tab)
    
    def switch_to_auto_detection(self):
        """切换到自动检测tab"""
        self.sub_tab_widget.setCurrentWidget(self.auto_tab)
    
    def switch_to_manual_config(self):
        """切换到手动配置tab"""
        self.sub_tab_widget.setCurrentWidget(self.manual_tab)
    
    def get_auto_tab(self):
        """获取自动检测tab"""
        return self.auto_tab
    
    def get_manual_tab(self):
        """获取手动配置tab"""
        return self.manual_tab