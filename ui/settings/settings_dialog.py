"""
重构后的设置对话框
组装各个标签页组件
"""

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget
from PySide6.QtCore import Qt, Signal
from typing import Callable, Optional
from .base_dialog import BaseSettingsDialog
from .tabs.basic_tab import BasicSettingsTab
from .tabs.ai_tab import AISettingsTab
from .tabs.appearance_tab import AppearanceSettingsTab
from .tabs.about_tab import AboutTab


class SettingsDialog(BaseSettingsDialog):
    """设置对话框类"""
    
    def __init__(self, parent, config_manager, on_settings_changed: Optional[Callable] = None):
        super().__init__(parent, config_manager, on_settings_changed)
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标签页组件
        tab_widget = QTabWidget()
        
        # 创建各个标签页
        self.basic_tab = BasicSettingsTab()
        tab_widget.addTab(self.basic_tab, "基本设置")
        
        self.ai_tab = AISettingsTab()
        tab_widget.addTab(self.ai_tab, "AI模型")
        
        self.appearance_tab = AppearanceSettingsTab()
        tab_widget.addTab(self.appearance_tab, "外观")
        
        self.about_tab = AboutTab()
        tab_widget.addTab(self.about_tab, "关于")
        
        main_layout.addWidget(tab_widget)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFlat(True)
        self.ok_button = QPushButton("确定")
        self.ok_button.setDefault(True)
        
        # 设置按钮间距
        button_layout.addWidget(self.cancel_button)
        button_layout.addSpacing(12)
        button_layout.addWidget(self.ok_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # 连接信号
        self.ok_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
    
    def connect_signals(self):
        """连接各种信号"""
        # 注释：移除AI配置测试成功的信号连接，现在改为关闭设置后重新检查配置
        pass
    
    def load_settings(self):
        """加载当前设置"""
        # 加载各个标签页的设置
        self.basic_tab.load_settings(self.config)
        self.ai_tab.load_settings(self.config)
        self.appearance_tab.load_settings(self.config)
        self.about_tab.load_settings(self.config)
    
    def save_settings(self):
        """保存设置"""
        # 收集各个标签页的设置
        basic_settings = self.basic_tab.get_settings()
        ai_settings = self.ai_tab.get_settings()
        appearance_settings = self.appearance_tab.get_settings()
        
        # 合并所有设置
        all_settings = {}
        all_settings.update(basic_settings)
        all_settings.update(ai_settings)
        all_settings.update(appearance_settings)
        
        # 更新配置
        self.config.update(**all_settings)
        
        # 通知主窗口设置已更改
        if self.on_settings_changed:
            self.on_settings_changed()
            
        self.accept()