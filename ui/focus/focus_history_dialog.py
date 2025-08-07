"""
专注历史查看对话框
显示历史专注数据和统计信息
"""
import logging
from typing import List, Dict, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QTabWidget, QWidget,
    QFrame, QGridLayout, QHeaderView, QAbstractItemView,
    QMessageBox, QProgressBar, QScrollArea, QGroupBox,
    QSplitter, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon
from ..theme import ModernTheme
from utils.focus_storage import get_focus_storage

logger = logging.getLogger(__name__)


class DataLoadThread(QThread):
    """数据加载线程"""
    
    data_loaded = Signal(object)  # 数据加载完成信号
    error_occurred = Signal(str)  # 错误信号
    
    def __init__(self, load_type: str, **kwargs):
        super().__init__()
        self.load_type = load_type
        self.kwargs = kwargs
    
    def run(self):
        """运行数据加载"""
        try:
            storage = get_focus_storage()
            
            if self.load_type == "history":
                data = storage.get_session_history(
                    limit=self.kwargs.get('limit', 50),
                    offset=self.kwargs.get('offset', 0)
                )
            elif self.load_type == "statistics":
                data = storage.get_statistics(
                    days=self.kwargs.get('days', 30)
                )
            elif self.load_type == "details":
                data = storage.get_session_details(
                    session_id=self.kwargs.get('session_id')
                )
            else:
                raise ValueError(f"未知的加载类型: {self.load_type}")
            
            self.data_loaded.emit(data)
            
        except Exception as e:
            logger.error(f"数据加载失败: {e}")
            self.error_occurred.emit(str(e))


class FocusHistoryDialog(QDialog):
    """专注历史对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.storage = get_focus_storage()
        self.session_data = []
        self.statistics_data = {}
        
        self.setWindowTitle("📈 专注历史")
        self.setModal(False)
        self.resize(900, 700)
        
        # 设置窗口标志
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )
        
        self.setup_ui()
        self.apply_theme()
        self.load_initial_data()
        
        logger.info("专注历史对话框已创建")
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        self.create_title(layout)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 统计信息选项卡
        self.statistics_tab = self.create_statistics_tab()
        self.tab_widget.addTab(self.statistics_tab, "📊 统计信息")
        
        # 历史记录选项卡
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "📋 历史记录")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮区域
        self.create_buttons(layout)
    
    def create_title(self, layout):
        """创建标题区域"""
        title_label = QLabel("📈 专注历史统计")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title_label.setFont(font)
        
        layout.addWidget(title_label)
    
    def create_statistics_tab(self) -> QWidget:
        """创建统计信息选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # 时间选择器
        time_frame = QFrame()
        time_layout = QHBoxLayout(time_frame)
        
        time_layout.addWidget(QLabel("统计周期:"))
        
        # 时间段按钮
        self.time_buttons = {}
        for days, text in [(7, "近7天"), (30, "近30天"), (90, "近3个月")]:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, d=days: self.load_statistics(d))
            self.time_buttons[days] = btn
            time_layout.addWidget(btn)
        
        # 默认选择30天
        self.time_buttons[30].setChecked(True)
        
        time_layout.addStretch()
        layout.addWidget(time_frame)
        
        # 统计卡片区域
        self.stats_scroll = QScrollArea()
        self.stats_scroll.setWidgetResizable(True)
        self.stats_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.stats_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.stats_widget = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_widget)
        self.stats_scroll.setWidget(self.stats_widget)
        
        layout.addWidget(self.stats_scroll)
        
        return tab
    
    def create_history_tab(self) -> QWidget:
        """创建历史记录选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：会话列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("专注会话列表"))
        
        # 会话表格
        self.session_table = QTableWidget()
        self.session_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.session_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.session_table.itemSelectionChanged.connect(self.on_session_selected)
        
        # 设置表格列
        columns = ["目标", "计划时长", "实际时长", "完成率", "开始时间"]
        self.session_table.setColumnCount(len(columns))
        self.session_table.setHorizontalHeaderLabels(columns)
        
        # 设置列宽
        header = self.session_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # 目标列自适应
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        left_layout.addWidget(self.session_table)
        
        # 右侧：会话详情
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        right_layout.addWidget(QLabel("会话详情"))
        
        self.details_area = QScrollArea()
        self.details_area.setWidgetResizable(True)
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        self.details_area.setWidget(self.details_widget)
        
        # 默认显示提示信息
        self.show_no_selection_message()
        
        right_layout.addWidget(self.details_area)
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 500])  # 设置初始大小比例
        
        layout.addWidget(splitter)
        
        return tab
    
    def create_buttons(self, layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.refresh_data)
        
        # 清理数据按钮
        cleanup_btn = QPushButton("🗑️ 清理旧数据")
        cleanup_btn.clicked.connect(self.cleanup_old_data)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(cleanup_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_initial_data(self):
        """加载初始数据"""
        self.load_statistics(30)  # 默认加载30天统计
        self.load_history()
    
    def load_statistics(self, days: int):
        """加载统计信息"""
        # 更新按钮状态
        for d, btn in self.time_buttons.items():
            btn.setChecked(d == days)
        
        # 清空现有内容
        for i in reversed(range(self.stats_layout.count())):
            self.stats_layout.itemAt(i).widget().setParent(None)
        
        # 显示加载提示
        loading_label = QLabel("正在加载统计数据...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_layout.addWidget(loading_label)
        
        # 启动数据加载线程
        self.stats_thread = DataLoadThread("statistics", days=days)
        self.stats_thread.data_loaded.connect(self.on_statistics_loaded)
        self.stats_thread.error_occurred.connect(self.on_load_error)
        self.stats_thread.start()
    
    def load_history(self):
        """加载历史记录"""
        self.session_table.setRowCount(0)
        
        # 启动数据加载线程
        self.history_thread = DataLoadThread("history", limit=100)
        self.history_thread.data_loaded.connect(self.on_history_loaded)
        self.history_thread.error_occurred.connect(self.on_load_error)
        self.history_thread.start()
    
    def on_statistics_loaded(self, stats: Dict):
        """统计信息加载完成"""
        self.statistics_data = stats
        
        # 清空现有内容
        for i in reversed(range(self.stats_layout.count())):
            self.stats_layout.itemAt(i).widget().setParent(None)
        
        # 创建统计卡片
        self.create_stats_cards(stats)
    
    def on_history_loaded(self, sessions: List[Dict]):
        """历史记录加载完成"""
        self.session_data = sessions
        self.populate_session_table()
    
    def on_load_error(self, error: str):
        """数据加载错误"""
        QMessageBox.warning(self, "加载错误", f"数据加载失败：{error}")
    
    def create_stats_cards(self, stats: Dict):
        """创建统计卡片"""
        # 主要统计信息
        main_stats_frame = QGroupBox("主要统计")
        main_stats_layout = QGridLayout(main_stats_frame)
        
        # 统计项目
        stat_items = [
            ("总会话数", f"{stats['total_sessions']} 次", "🎯"),
            ("完成会话", f"{stats['completed_sessions']} 次", "✅"),
            ("完成率", f"{stats['completion_rate']:.1f}%", "📊"),
            ("专注效率", f"{stats['focus_efficiency']:.1f}%", "🔥"),
            ("总专注时间", f"{stats['total_focused_time_minutes']:.0f} 分钟", "⏰"),
            ("平均时长", f"{stats['avg_session_duration_minutes']:.1f} 分钟", "📈")
        ]
        
        row, col = 0, 0
        for label, value, emoji in stat_items:
            card = self.create_stat_card(emoji, label, value)
            main_stats_layout.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        self.stats_layout.addWidget(main_stats_frame)
        
        # 热门目标
        if stats['top_goals']:
            goals_frame = QGroupBox("热门专注目标")
            goals_layout = QVBoxLayout(goals_frame)
            
            for goal, count in stats['top_goals']:
                goal_item = QFrame()
                goal_item.setFrameStyle(QFrame.Shape.Box)
                goal_layout = QHBoxLayout(goal_item)
                
                goal_layout.addWidget(QLabel(goal))
                goal_layout.addStretch()
                goal_layout.addWidget(QLabel(f"{count} 次"))
                
                goals_layout.addWidget(goal_item)
            
            self.stats_layout.addWidget(goals_frame)
        
        # 添加伸展项
        self.stats_layout.addStretch()
    
    def create_stat_card(self, emoji: str, label: str, value: str) -> QFrame:
        """创建统计卡片"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setFixedHeight(80)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 表情和数值
        value_layout = QHBoxLayout()
        
        emoji_label = QLabel(emoji)
        emoji_label.setFont(QFont("", 20))
        
        value_label = QLabel(value)
        value_label.setFont(QFont("", 16, QFont.Weight.Bold))
        
        value_layout.addWidget(emoji_label)
        value_layout.addWidget(value_label)
        value_layout.addStretch()
        
        # 标签
        label_widget = QLabel(label)
        label_widget.setFont(QFont("", 11))
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(value_layout)
        layout.addWidget(label_widget)
        
        return card
    
    def populate_session_table(self):
        """填充会话表格"""
        self.session_table.setRowCount(len(self.session_data))
        
        for row, session in enumerate(self.session_data):
            # 目标
            self.session_table.setItem(row, 0, QTableWidgetItem(session['goal']))
            
            # 计划时长
            self.session_table.setItem(row, 1, QTableWidgetItem(f"{session['planned_duration']} 分钟"))
            
            # 实际时长
            actual_duration = session.get('actual_duration', 0)
            self.session_table.setItem(row, 2, QTableWidgetItem(f"{actual_duration:.1f} 分钟"))
            
            # 完成率
            completion_rate = session.get('completion_rate', 0)
            self.session_table.setItem(row, 3, QTableWidgetItem(f"{completion_rate:.1f}%"))
            
            # 开始时间
            self.session_table.setItem(row, 4, QTableWidgetItem(session['started_at']))
            
            # 存储完整数据到第一列的item中
            self.session_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, session)
    
    def on_session_selected(self):
        """会话选择改变"""
        current_row = self.session_table.currentRow()
        if current_row >= 0:
            session = self.session_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            self.load_session_details(session['id'])
        else:
            self.show_no_selection_message()
    
    def load_session_details(self, session_id: int):
        """加载会话详情"""
        # 清空现有内容
        for i in reversed(range(self.details_layout.count())):
            self.details_layout.itemAt(i).widget().setParent(None)
        
        # 显示加载提示
        loading_label = QLabel("正在加载会话详情...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_layout.addWidget(loading_label)
        
        # 启动详情加载线程
        self.details_thread = DataLoadThread("details", session_id=session_id)
        self.details_thread.data_loaded.connect(self.on_session_details_loaded)
        self.details_thread.error_occurred.connect(self.on_load_error)
        self.details_thread.start()
    
    def on_session_details_loaded(self, details: Dict):
        """会话详情加载完成"""
        # 清空现有内容
        for i in reversed(range(self.details_layout.count())):
            self.details_layout.itemAt(i).widget().setParent(None)
        
        if not details:
            error_label = QLabel("会话详情加载失败")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.details_layout.addWidget(error_label)
            return
        
        # 创建详情显示
        self.create_session_details(details)
    
    def create_session_details(self, details: Dict):
        """创建会话详情显示"""
        # 基本信息
        info_frame = QGroupBox("基本信息")
        info_layout = QGridLayout(info_frame)
        
        info_items = [
            ("目标", details['goal']),
            ("计划时长", f"{details['planned_duration']} 分钟"),
            ("实际时长", f"{details['actual_duration']:.1f} 分钟"),
            ("完成率", f"{details['completion_rate']:.1f}%"),
            ("开始时间", details['started_at']),
            ("结束时间", details['ended_at'] or "未完成"),
            ("专注时间", f"{details['total_focused_time']/60:.1f} 分钟"),
            ("分心时间", f"{details['total_distracted_time']/60:.1f} 分钟")
        ]
        
        for i, (label, value) in enumerate(info_items):
            info_layout.addWidget(QLabel(f"{label}:"), i // 2, (i % 2) * 2)
            info_layout.addWidget(QLabel(str(value)), i // 2, (i % 2) * 2 + 1)
        
        self.details_layout.addWidget(info_frame)
        
        # AI分析记录
        if details.get('analysis_results'):
            analysis_frame = QGroupBox("AI分析记录")
            analysis_layout = QVBoxLayout(analysis_frame)
            
            # 创建分析记录表格
            analysis_table = QTableWidget()
            analysis_table.setMaximumHeight(200)
            analysis_results = details['analysis_results']
            
            analysis_table.setRowCount(len(analysis_results))
            analysis_table.setColumnCount(4)
            analysis_table.setHorizontalHeaderLabels(["时间", "专注状态", "反馈", "表情"])
            
            for row, result in enumerate(analysis_results):
                analysis_table.setItem(row, 0, QTableWidgetItem(result['time_str']))
                analysis_table.setItem(row, 1, QTableWidgetItem("专注" if result['is_focused'] else "分心"))
                analysis_table.setItem(row, 2, QTableWidgetItem(result['feedback_message']))
                analysis_table.setItem(row, 3, QTableWidgetItem(result['recommended_emoji']))
            
            # 设置列宽
            header = analysis_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            
            analysis_layout.addWidget(analysis_table)
            self.details_layout.addWidget(analysis_frame)
        
        # 添加伸展项
        self.details_layout.addStretch()
    
    def show_no_selection_message(self):
        """显示未选择会话的提示"""
        # 清空现有内容
        for i in reversed(range(self.details_layout.count())):
            self.details_layout.itemAt(i).widget().setParent(None)
        
        message_label = QLabel("请从左侧选择一个专注会话查看详情")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("color: #666; font-size: 14px;")
        
        self.details_layout.addWidget(message_label)
    
    def refresh_data(self):
        """刷新数据"""
        current_days = 30
        for days, btn in self.time_buttons.items():
            if btn.isChecked():
                current_days = days
                break
        
        self.load_statistics(current_days)
        self.load_history()
        
        # 清空详情区域
        self.show_no_selection_message()
    
    def cleanup_old_data(self):
        """清理旧数据"""
        reply = QMessageBox.question(
            self,
            "确认清理",
            "确定要清理90天前的旧数据吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.storage.cleanup_old_data(90)
                QMessageBox.information(self, "清理完成", "旧数据清理成功！")
                self.refresh_data()
            except Exception as e:
                QMessageBox.warning(self, "清理失败", f"数据清理失败：{str(e)}")
    
    def apply_theme(self):
        """应用主题样式"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #f8f9fa;
            }}
            
            QTabWidget::pane {{
                border: 1px solid #dee2e6;
                background-color: white;
                border-radius: 8px;
            }}
            
            QTabBar::tab {{
                background-color: #e9ecef;
                border: 1px solid #dee2e6;
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: 6px 6px 0 0;
            }}
            
            QTabBar::tab:selected {{
                background-color: white;
                border-bottom: 1px solid white;
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin: 10px 0;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: white;
            }}
            
            QFrame {{
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 10px;
                margin: 2px;
            }}
            
            QTableWidget {{
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                gridline-color: #e9ecef;
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #f1f3f4;
            }}
            
            QTableWidget::item:selected {{
                background-color: #e3f2fd;
                color: #1976d2;
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
            
            QPushButton:checked {{
                background-color: #007bff;
            }}
            
            QPushButton:checked:hover {{
                background-color: #0056b3;
            }}
        """)
    
    def keyPressEvent(self, event):
        """处理按键事件"""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
        elif event.key() == Qt.Key.Key_F5:
            self.refresh_data()
        else:
            super().keyPressEvent(event)
