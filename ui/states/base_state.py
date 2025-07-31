"""
基础状态接口
为所有状态提供统一的接口定义
"""
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ui.desktop_pet import DesktopPet

class BaseState(ABC):
    """基础状态抽象类"""
    
    def __init__(self, desktop_pet: "DesktopPet", state_name: str):
        """
        初始化状态
        
        Args:
            desktop_pet: 桌面宠物实例
            state_name: 状态名称
        """
        self.desktop_pet: "DesktopPet" = desktop_pet
        self.state_name = state_name
        self._is_active = False
    
    @property
    def is_active(self) -> bool:
        """状态是否处于激活状态"""
        return self._is_active
    
    @abstractmethod
    def enter(self) -> None:
        """
        进入状态时的操作
        子类必须实现此方法
        """
        self._is_active = True
    
    @abstractmethod
    def exit(self) -> None:
        """
        退出状态时的操作
        子类必须实现此方法
        """
        self._is_active = False
    
    def on_click(self) -> None:
        """
        处理点击事件
        子类可以重写此方法
        """
        pass
    
    def on_right_click(self) -> None:
        """
        处理右键点击事件
        子类可以重写此方法
        """
        # 创建动态右键菜单
        self._create_dynamic_context_menu()
    
    def _create_dynamic_context_menu(self):
        """创建动态右键菜单"""
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QCursor, QAction
        
        # 创建菜单
        menu = QMenu(self.desktop_pet)
        
        # 应用主题样式
        if hasattr(self.desktop_pet, '__class__'):
            try:
                from ..theme import ModernTheme
                menu.setStyleSheet(ModernTheme.get_menu_style())
            except ImportError:
                pass
        
        # 获取状态相关的菜单项
        state_items = self.get_context_menu_items()
        
        # 添加状态相关的菜单项
        for item in state_items:
            if item.get("separator"):
                menu.addSeparator()
                continue
            
            action = QAction(item["text"], self.desktop_pet)
            action.setEnabled(item.get("enabled", True))
            
            # 连接动作处理器
            action_name = item.get("action")
            if action_name:
                action.triggered.connect(lambda checked, a=action_name: self._handle_menu_action(a))
            
            menu.addAction(action)
        
        # 如果有状态菜单项，添加分隔线
        if state_items:
            menu.addSeparator()
        
        # 添加系统菜单项
        settings_action = QAction("设置", self.desktop_pet)
        settings_action.triggered.connect(self.desktop_pet.show_settings)
        menu.addAction(settings_action)
        
        quit_action = QAction("退出", self.desktop_pet)
        quit_action.triggered.connect(self.desktop_pet.quit_app)
        menu.addAction(quit_action)
        
        # 显示菜单
        menu.exec(QCursor.pos())
    
    def _handle_menu_action(self, action_name: str):
        """
        处理菜单动作
        子类可以重写此方法来处理自定义动作
        
        Args:
            action_name: 动作名称
        """
        if action_name == "change_emoji":
            self._handle_change_emoji()
        elif action_name == "start_focus":
            self._handle_start_focus()
        elif action_name == "ai_features":
            self._handle_ai_features()
        else:
            # 默认处理或日志记录
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"未处理的菜单动作: {action_name}")
    
    def _handle_change_emoji(self):
        """处理换表情动作"""
        if hasattr(self.desktop_pet, 'pet_label'):
            self.desktop_pet.pet_label.set_random_animated_emoji()
    
    def _handle_start_focus(self):
        """处理开始专注动作"""
        if hasattr(self.desktop_pet, 'ai_state_manager'):
            self.desktop_pet.ai_state_manager.switch_to_focus()
    
    def _handle_ai_features(self):
        """处理AI功能动作"""
        # 这里可以添加AI功能的处理逻辑
        if hasattr(self.desktop_pet, 'show_speech_bubble'):
            self.desktop_pet.show_speech_bubble("🤖 AI功能开发中...", "thinking.gif", 2000)
    
    def on_hover_enter(self) -> None:
        """
        鼠标悬停进入事件
        子类可以重写此方法
        """
        pass
    
    def on_hover_leave(self) -> None:
        """
        鼠标悬停离开事件
        子类可以重写此方法
        """
        pass
    
    def get_tooltip_text(self) -> Optional[str]:
        """
        获取工具提示文本
        子类可以重写此方法
        
        Returns:
            Optional[str]: 工具提示文本，None表示无提示
        """
        return None
    
    def get_context_menu_items(self) -> list:
        """
        获取状态相关的右键菜单项
        子类可以重写此方法
        
        Returns:
            list: 菜单项列表
        """
        return []
    
    def get_speech_text(self) -> Optional[str]:
        """
        获取状态相关的对话文本
        子类可以重写此方法来提供自定义对话内容
        
        Returns:
            Optional[str]: 对话文本，None表示无对话
        """
        return None
    
    def get_speech_emoji(self) -> Optional[str]:
        """
        获取状态相关的对话表情
        子类可以重写此方法来提供配套的表情
        
        Returns:
            Optional[str]: 表情文件名，None表示使用默认表情
        """
        return None
    
    def should_show_speech_on_enter(self) -> bool:
        """
        是否在进入状态时显示对话气泡
        子类可以重写此方法
        
        Returns:
            bool: 是否显示对话
        """
        return False
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.__class__.__name__}({self.state_name})"
    
    def __repr__(self) -> str:
        """调试字符串表示"""
        return f"{self.__class__.__name__}(name='{self.state_name}', active={self._is_active})"