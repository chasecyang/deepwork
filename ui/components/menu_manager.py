"""
菜单管理器
负责桌面宠物的右键菜单管理
"""
from PySide6.QtWidgets import QMenu, QApplication
from PySide6.QtGui import QAction, QCursor
from ..theme import ModernTheme


class MenuManager:
    """菜单管理器"""
    
    def __init__(self, widget, on_settings_clicked=None, on_quit_clicked=None, on_focus_history_clicked=None):
        self.widget = widget
        self.on_settings_clicked = on_settings_clicked
        self.on_quit_clicked = on_quit_clicked
        self.on_focus_history_clicked = on_focus_history_clicked
        self.context_menu = None
        self._setup_menu()
        
    def _setup_menu(self):
        """设置右键菜单"""
        self.context_menu = QMenu(self.widget)
        
        # 应用现代化菜单样式
        self.context_menu.setStyleSheet(ModernTheme.get_menu_style())
        
        # 创建菜单动作
        focus_history_action = QAction("📈 专注历史", self.widget)
        focus_history_action.triggered.connect(self._handle_focus_history)
        
        settings_action = QAction("设置", self.widget)
        settings_action.triggered.connect(self._handle_settings)
        
        quit_action = QAction("退出", self.widget)
        quit_action.triggered.connect(self._handle_quit)
        
        # 添加动作到菜单
        self.context_menu.addAction(focus_history_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(settings_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(quit_action)
        
    def _handle_focus_history(self):
        """处理专注历史菜单点击"""
        if self.on_focus_history_clicked:
            self.on_focus_history_clicked()
            
    def _handle_settings(self):
        """处理设置菜单点击"""
        if self.on_settings_clicked:
            self.on_settings_clicked()
            
    def _handle_quit(self):
        """处理退出菜单点击"""
        if self.on_quit_clicked:
            self.on_quit_clicked()
        else:
            QApplication.quit()
            
    def show_menu(self):
        """显示右键菜单"""
        self.context_menu.exec(QCursor.pos())
