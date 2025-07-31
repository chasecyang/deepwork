"""
基本设置标签页
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QGroupBox)
from PySide6.QtCore import Qt
from ..components.value_widgets import SliderWithValue


class BasicSettingsTab(QWidget):
    """基本设置标签页"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QVBoxLayout(basic_group)
        basic_layout.setSpacing(12)
        
        # 宠物名称设置
        name_layout = QHBoxLayout()
        name_label = QLabel("名称")
        name_label.setFixedWidth(40)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入名称...")
        self.name_edit.setMinimumHeight(28)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        basic_layout.addLayout(name_layout)
        
        layout.addWidget(basic_group)
        
        # 行为设置组
        behavior_group = QGroupBox("行为设置")
        behavior_layout = QVBoxLayout(behavior_group)
        behavior_layout.setSpacing(12)
        
        # 置顶设置
        self.topmost_checkbox = QCheckBox("总是置顶")
        behavior_layout.addWidget(self.topmost_checkbox)
        
        layout.addWidget(behavior_group)
        
        # 外观设置组
        appearance_group = QGroupBox("外观设置")
        appearance_layout = QVBoxLayout(appearance_group)
        appearance_layout.setSpacing(12)
        
        # 透明度设置 - 使用新的滑块组件
        self.transparency_slider = SliderWithValue(
            label="透明度:",
            minimum=30,
            maximum=100,
            value=90,
            unit="%",
            min_label="30%",
            max_label="100%"
        )
        
        appearance_layout.addWidget(self.transparency_slider)
        layout.addWidget(appearance_group)
        
        # 添加一些间距
        layout.addStretch()
    
    def load_settings(self, config):
        """加载设置"""
        self.name_edit.setText(config.get("pet_name", "桌面助手"))
        self.topmost_checkbox.setChecked(config.get("always_on_top", True))
        
        # 透明度值转换为百分比
        transparency = config.get("transparency", 0.9)
        self.transparency_slider.setValue(int(transparency * 100))
    
    def get_settings(self) -> dict:
        """获取设置"""
        return {
            "pet_name": self.name_edit.text(),
            "always_on_top": self.topmost_checkbox.isChecked(),
            "transparency": self.transparency_slider.value() / 100.0
        }