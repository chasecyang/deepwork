"""
简化的专注配置对话框
让用户设置专注目标和时长
"""
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QSlider, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ..theme import ModernTheme

logger = logging.getLogger(__name__)


class FocusConfigDialog(QDialog):
    """专注配置对话框"""
    
    # 信号定义
    focus_started = Signal(str, int)  # (目标, 时长分钟)
    focus_cancelled = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎯 开始专注")
        self.setModal(True)
        self.resize(380, 280)  # 缩小尺寸
        
        # 设置窗口标志，确保始终在前台
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # 默认时长（分钟）
        self.duration_minutes = 25
        
        self.setup_ui()
        self.apply_theme()
        
        logger.info("专注配置对话框初始化完成")
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        self.create_title(layout)
        
        # 专注目标输入
        self.create_goal_input(layout)
        
        # 时长滑块
        self.create_duration_slider(layout)
        
        # 按钮
        self.create_buttons(layout)
    
    def create_title(self, layout):
        """创建标题区域"""
        title_label = QLabel("🎯 开始专注")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 设置标题字体
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title_label.setFont(font)
        
        layout.addWidget(title_label)
    
    def create_goal_input(self, layout):
        """创建专注目标输入区域"""
        goal_label = QLabel("专注目标")
        goal_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(goal_label)
        
        self.goal_input = QLineEdit()
        self.goal_input.setPlaceholderText("例如: 完成项目报告、学习Python、阅读文档...")
        layout.addWidget(self.goal_input)
    
    def create_duration_slider(self, layout):
        """创建时长滑块区域"""
        duration_label = QLabel("专注时长")
        duration_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(duration_label)
        
        # 时长显示标签
        self.duration_display = QLabel(f"{self.duration_minutes} 分钟")
        self.duration_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.duration_display.setStyleSheet("font-size: 24px; font-weight: bold; color: #007bff; margin: 10px 0;")
        layout.addWidget(self.duration_display)
        
        # 时长滑块
        self.duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.duration_slider.setMinimum(5)   # 最短5分钟
        self.duration_slider.setMaximum(180) # 最长3小时
        self.duration_slider.setValue(self.duration_minutes)
        self.duration_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.duration_slider.setTickInterval(15)  # 每15分钟一个刻度
        self.duration_slider.valueChanged.connect(self.on_duration_changed)
        layout.addWidget(self.duration_slider)
        
        # 时长范围标签
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("5分钟"))
        range_layout.addStretch()
        range_layout.addWidget(QLabel("3小时"))
        layout.addLayout(range_layout)
    
    def on_duration_changed(self, value):
        """处理时长滑块变化"""
        self.duration_minutes = value
        self.duration_display.setText(f"{value} 分钟")
    
    def create_buttons(self, layout):
        """创建按钮区域"""
        # 添加弹性空间
        layout.addStretch()
        
        button_layout = QHBoxLayout()
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.on_cancel)
        
        # 开始按钮
        self.start_btn = QPushButton("🚀 开始专注")
        self.start_btn.clicked.connect(self.on_start_focus)
        self.start_btn.setDefault(True)  # 设为默认按钮
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.start_btn)
        
        layout.addLayout(button_layout)
    
    def apply_theme(self):
        """应用主题样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border-radius: 12px;
            }
            
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
            
            QSlider::groove:horizontal {
                height: 8px;
                background: #e9ecef;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #007bff;
                border: none;
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: -6px 0;
            }
            
            QSlider::handle:horizontal:hover {
                background: #0056b3;
            }
            
            QSlider::sub-page:horizontal {
                background: #007bff;
                border-radius: 4px;
            }
            
            QPushButton {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                min-width: 100px;
                background-color: #6c757d;
                color: white;
            }
            
            QPushButton:hover {
                background-color: #5a6268;
            }
            
            QPushButton:pressed {
                background-color: #4e555b;
            }
            
            QPushButton[default="true"] {
                background-color: #007bff;
                font-weight: bold;
            }
            
            QPushButton[default="true"]:hover {
                background-color: #0056b3;
            }
            
            QLabel {
                color: #495057;
                font-size: 13px;
            }
        """)
    
    def on_start_focus(self):
        """开始专注"""
        goal = self.goal_input.text().strip()
        
        if not goal:
            self.goal_input.setFocus()
            self.goal_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #dc3545 !important;
                    background-color: #fff5f5 !important;
                }
            """)
            return
        
        # 发出开始信号
        self.focus_started.emit(goal, self.duration_minutes)
        
        # 关闭对话框
        self.accept()
        
        logger.info(f"用户开始专注: {goal}, {self.duration_minutes}分钟")
    
    def on_cancel(self):
        """取消专注"""
        self.focus_cancelled.emit()
        self.reject()
        
        logger.info("用户取消专注设置")
    
    def keyPressEvent(self, event):
        """处理按键事件"""
        # Enter键开始专注
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.goal_input.text().strip():
                self.on_start_focus()
            else:
                self.goal_input.setFocus()
        # Esc键取消
        elif event.key() == Qt.Key.Key_Escape:
            self.on_cancel()
        else:
            super().keyPressEvent(event)