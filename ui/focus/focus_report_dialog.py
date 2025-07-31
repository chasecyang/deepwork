"""
专注报告对话框
显示专注会话的统计结果
"""
import logging
from typing import Dict
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame, QGridLayout, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from ..theme import ModernTheme

logger = logging.getLogger(__name__)


class FocusReportDialog(QDialog):
    """专注报告对话框"""
    
    def __init__(self, session_summary: Dict, parent=None):
        super().__init__(parent)
        self.session_summary = session_summary
        
        self.setWindowTitle("📊 专注报告")
        self.setModal(True)
        self.resize(450, 600)
        
        # 设置窗口标志
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        self.setup_ui()
        self.apply_theme()
        
        logger.info("专注报告对话框已创建")
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题区域
        self.create_title(layout)
        
        # 主要统计
        self.create_main_stats(layout)
        
        # 详细统计
        self.create_detailed_stats(layout)
        

        
        # 按钮
        self.create_buttons(layout)
    
    def create_title(self, layout):
        """创建标题区域"""
        title_label = QLabel("🎉 专注完成！")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 设置标题字体
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        title_label.setFont(font)
        
        layout.addWidget(title_label)
        
        # 目标显示
        goal_label = QLabel(f"目标: {self.session_summary.get('goal', '未知')}")
        goal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        goal_label.setWordWrap(True)
        
        goal_font = QFont()
        goal_font.setPointSize(14)
        goal_label.setFont(goal_font)
        
        layout.addWidget(goal_label)
    
    def create_main_stats(self, layout):
        """创建主要统计信息"""
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.Box)
        stats_layout = QGridLayout(stats_frame)
        
        # 实际专注时长
        actual_time = self.session_summary.get('actual_duration', 0)
        time_label = QLabel("实际时长")
        time_value = QLabel(f"{actual_time:.1f} 分钟")
        time_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 完成率
        completion_rate = self.session_summary.get('completion_rate', 0)
        completion_label = QLabel("完成率")
        completion_value = QLabel(f"{completion_rate:.1f}%")
        completion_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        

        
        # 设置数值标签样式
        value_font = QFont()
        value_font.setPointSize(16)
        value_font.setBold(True)
        
        for value_label in [time_value, completion_value]:
            value_label.setFont(value_font)
        
        # 添加到布局
        stats_layout.addWidget(time_label, 0, 0)
        stats_layout.addWidget(time_value, 1, 0)
        
        stats_layout.addWidget(completion_label, 0, 1)
        stats_layout.addWidget(completion_value, 1, 1)
        
        layout.addWidget(stats_frame)
    
    def create_detailed_stats(self, layout):
        """创建详细统计信息"""
        detail_frame = QFrame()
        detail_layout = QVBoxLayout(detail_frame)
        
        detail_title = QLabel("详细统计")
        detail_title.setFont(QFont("", 12, QFont.Weight.Bold))
        detail_layout.addWidget(detail_title)
        
        # 统计信息列表
        stats = [
            ("计划时长", f"{self.session_summary.get('planned_duration', 0)} 分钟"),
            ("专注时间", f"{self.session_summary.get('focused_time', 0):.1f} 分钟"),
            ("分心时间", f"{self.session_summary.get('distracted_time', 0):.1f} 分钟"),
            ("分析次数", f"{self.session_summary.get('analysis_count', 0)} 次"),
            ("开始时间", self.session_summary.get('started_at', '未知')),
            ("结束时间", self.session_summary.get('ended_at', '未知'))
        ]
        
        for label_text, value_text in stats:
            row_layout = QHBoxLayout()
            
            label = QLabel(label_text + ":")
            value = QLabel(str(value_text))
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            row_layout.addWidget(label)
            row_layout.addStretch()
            row_layout.addWidget(value)
            
            detail_layout.addLayout(row_layout)
        
        layout.addWidget(detail_frame)
    

    
    def create_buttons(self, layout):
        """创建按钮区域"""
        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        button_layout = QHBoxLayout()
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        
        # 再来一次按钮
        again_btn = QPushButton("🎯 再来一次")
        again_btn.clicked.connect(self.start_another_focus)
        
        button_layout.addStretch()
        button_layout.addWidget(again_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def start_another_focus(self):
        """开始另一次专注"""
        # 这里可以触发新的专注会话
        self.accept()
        
        # 通知父窗口开始新的专注
        if hasattr(self.parent(), 'ai_state_manager'):
            # 切换到正常状态，然后用户可以再次选择专注
            self.parent().ai_state_manager.switch_to_normal()
    
    def apply_theme(self):
        """应用主题样式"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #f8f9fa;
                border-radius: 12px;
            }}
            
            QFrame {{
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
                margin: 5px 0;
            }}
            
            QLabel {{
                color: #495057;
                font-size: 13px;
            }}
            
            QPushButton {{
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                min-width: 80px;
                background-color: #6c757d;
                color: white;
            }}
            
            QPushButton:hover {{
                background-color: #5a6268;
            }}
            
            QPushButton:pressed {{
                background-color: #4e555b;
            }}
        """)
    
    def keyPressEvent(self, event):
        """处理按键事件"""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(event)