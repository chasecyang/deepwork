"""
可复用的值显示组件
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, Signal
from ui.theme import ModernTheme


class SliderWithValue(QWidget):
    """带值显示的滑块组件"""
    
    valueChanged = Signal(int)
    
    def __init__(self, label: str, minimum: int, maximum: int, 
                 value: int = 50, unit: str = "", 
                 min_label: str = "", max_label: str = ""):
        super().__init__()
        self.unit = unit
        self.init_ui(label, minimum, maximum, value, min_label, max_label)
        
    def init_ui(self, label: str, minimum: int, maximum: int, 
                value: int, min_label: str, max_label: str):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # 主标签
        if label:
            main_label = QLabel(label)
            layout.addWidget(main_label)
        
        # 滑块
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(minimum)
        self.slider.setMaximum(maximum)
        self.slider.setValue(value)
        layout.addWidget(self.slider)
        
        # 值显示布局
        value_layout = QHBoxLayout()
        value_layout.setSpacing(0)
        
        # 最小值标签
        if min_label:
            min_label_widget = QLabel(min_label)
            min_label_widget.setStyleSheet(f"color: {ModernTheme.COLORS['text_muted']};")
            value_layout.addWidget(min_label_widget)
        
        value_layout.addStretch()
        
        # 当前值标签
        self.value_label = QLabel(f"{value}{self.unit}")
        self.value_label.setFixedWidth(60)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(f"color: {ModernTheme.COLORS['primary']}; font-weight: bold;")
        value_layout.addWidget(self.value_label)
        
        value_layout.addStretch()
        
        # 最大值标签
        if max_label:
            max_label_widget = QLabel(max_label)
            max_label_widget.setStyleSheet(f"color: {ModernTheme.COLORS['text_muted']};")
            value_layout.addWidget(max_label_widget)
        
        layout.addLayout(value_layout)
        
        # 连接信号
        self.slider.valueChanged.connect(self._on_value_changed)
    
    def _on_value_changed(self, value: int):
        """值改变处理"""
        self.value_label.setText(f"{value}{self.unit}")
        self.valueChanged.emit(value)
    
    def value(self) -> int:
        """获取当前值"""
        return self.slider.value()
    
    def setValue(self, value: int):
        """设置值"""
        self.slider.setValue(value)