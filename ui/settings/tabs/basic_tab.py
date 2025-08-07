"""
基本设置标签页
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QCheckBox, QGroupBox, QSpinBox)
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
        
        # AI互动设置组
        ai_group = QGroupBox("AI互动设置")
        ai_layout = QVBoxLayout(ai_group)
        ai_layout.setSpacing(12)
        
        # 随机对话开关
        self.ai_random_chat_checkbox = QCheckBox("启用AI随机对话")
        self.ai_random_chat_checkbox.setToolTip("在正常状态下，宠物会偶尔主动说话")
        ai_layout.addWidget(self.ai_random_chat_checkbox)
        
        # 对话间隔设置
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("对话间隔:"))
        
        self.min_interval_spin = QSpinBox()
        self.min_interval_spin.setRange(10, 300)  # 10秒-5分钟
        self.min_interval_spin.setValue(30)
        self.min_interval_spin.setSuffix(" 秒")
        self.min_interval_spin.setToolTip("随机对话的最小间隔时间")
        
        interval_layout.addWidget(QLabel("最小"))
        interval_layout.addWidget(self.min_interval_spin)
        
        self.max_interval_spin = QSpinBox()
        self.max_interval_spin.setRange(10, 600)  # 10秒-10分钟
        self.max_interval_spin.setValue(60)
        self.max_interval_spin.setSuffix(" 秒")
        self.max_interval_spin.setToolTip("随机对话的最大间隔时间")
        
        interval_layout.addWidget(QLabel("最大"))
        interval_layout.addWidget(self.max_interval_spin)
        interval_layout.addStretch()
        
        ai_layout.addLayout(interval_layout)
        
        # 连接间隔验证信号
        self.min_interval_spin.valueChanged.connect(self._validate_intervals)
        self.max_interval_spin.valueChanged.connect(self._validate_intervals)
        
        # 待机状态鼓励开关
        self.ai_encourage_checkbox = QCheckBox("启用待机状态下的AI鼓励")
        self.ai_encourage_checkbox.setToolTip("在待机状态下，宠物会偶尔鼓励用户配置AI功能")
        ai_layout.addWidget(self.ai_encourage_checkbox)
        
        layout.addWidget(ai_group)
        
        # 添加一些间距
        layout.addStretch()
    
    def load_settings(self, config):
        """加载设置"""
        self.name_edit.setText(config.get("pet_name", "桌面助手"))
        self.topmost_checkbox.setChecked(config.get("always_on_top", True))
        
        # 透明度值转换为百分比
        transparency = config.get("transparency", 0.9)
        self.transparency_slider.setValue(int(transparency * 100))
        
        # AI互动设置
        self.ai_random_chat_checkbox.setChecked(config.get("enable_ai_random_chat", True))
        self.min_interval_spin.setValue(config.get("ai_random_chat_min_interval", 30))  # 直接使用秒
        self.max_interval_spin.setValue(config.get("ai_random_chat_max_interval", 60))  # 直接使用秒
        self.ai_encourage_checkbox.setChecked(config.get("enable_ai_encourage_in_standby", True))
    
    def get_settings(self) -> dict:
        """获取设置"""
        return {
            "pet_name": self.name_edit.text(),
            "always_on_top": self.topmost_checkbox.isChecked(),
            "transparency": self.transparency_slider.value() / 100.0,
            # AI互动设置
            "enable_ai_random_chat": self.ai_random_chat_checkbox.isChecked(),
            "ai_random_chat_min_interval": self.min_interval_spin.value(),  # 直接使用秒
            "ai_random_chat_max_interval": self.max_interval_spin.value(),  # 直接使用秒
            "enable_ai_encourage_in_standby": self.ai_encourage_checkbox.isChecked(),
        }
    
    def _validate_intervals(self):
        """验证间隔设置，确保最小值不大于最大值"""
        min_val = self.min_interval_spin.value()
        max_val = self.max_interval_spin.value()
        
        if min_val > max_val:
            # 如果最小值大于最大值，自动调整最大值
            self.max_interval_spin.setValue(min_val)