"""
外观设置标签页
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QGroupBox)
from PySide6.QtCore import Qt
from ..components.value_widgets import SliderWithValue


class AppearanceSettingsTab(QWidget):
    """外观设置标签页"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 主题设置组
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setSpacing(12)
        
        # 主题选择
        self.theme_light_radio = QCheckBox("浅色主题")
        self.theme_dark_radio = QCheckBox("深色主题") 
        self.theme_light_radio.setChecked(True)  # 默认浅色主题
        
        theme_layout.addWidget(self.theme_light_radio)
        theme_layout.addWidget(self.theme_dark_radio)
        
        layout.addWidget(theme_group)
        
        # 动画设置组
        animation_group = QGroupBox("动画设置")
        animation_layout = QVBoxLayout(animation_group)
        animation_layout.setSpacing(12)
        
        # 动画开关
        self.enable_animations_checkbox = QCheckBox("启用过渡动画")
        self.enable_animations_checkbox.setChecked(True)
        animation_layout.addWidget(self.enable_animations_checkbox)
        
        # 动画速度 - 使用新的滑块组件
        self.animation_speed_slider = SliderWithValue(
            label="动画速度:",
            minimum=50,
            maximum=500,
            value=200,
            unit="ms",
            min_label="慢",
            max_label="快"
        )
        
        animation_layout.addWidget(self.animation_speed_slider)
        layout.addWidget(animation_group)
        
        # 连接信号
        self.theme_light_radio.toggled.connect(self._on_theme_changed)
        self.theme_dark_radio.toggled.connect(self._on_theme_changed)
        
        # 添加一些间距
        layout.addStretch()
    
    def _on_theme_changed(self):
        """主题改变事件处理"""
        # 确保只有一个主题被选中
        if self.sender() == self.theme_light_radio and self.theme_light_radio.isChecked():
            self.theme_dark_radio.setChecked(False)
        elif self.sender() == self.theme_dark_radio and self.theme_dark_radio.isChecked():
            self.theme_light_radio.setChecked(False)
    
    def load_settings(self, config):
        """加载设置"""
        # 加载主题和外观设置
        theme = config.get("theme", "light")
        if theme == "light":
            self.theme_light_radio.setChecked(True)
            self.theme_dark_radio.setChecked(False)
        else:
            self.theme_light_radio.setChecked(False)
            self.theme_dark_radio.setChecked(True)
            
        self.enable_animations_checkbox.setChecked(config.get("enable_animations", True))
        self.animation_speed_slider.setValue(config.get("animation_speed", 200))
    
    def get_settings(self) -> dict:
        """获取设置"""
        theme = "light" if self.theme_light_radio.isChecked() else "dark"
        
        return {
            "theme": theme,
            "enable_animations": self.enable_animations_checkbox.isChecked(),
            "animation_speed": self.animation_speed_slider.value()
        }