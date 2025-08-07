"""
基础状态接口（简化版）
为所有状态提供统一而简洁的接口定义
"""
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ui.desktop_pet import DesktopPet


class BaseState(ABC):
    """基础状态抽象类（简化版）"""
    
    def __init__(self, desktop_pet: "DesktopPet", state_name: str):
        self.desktop_pet = desktop_pet
        self.state_name = state_name
        self._is_active = False
    
    @property
    def is_active(self) -> bool:
        """状态是否处于激活状态"""
        return self._is_active
    
    @abstractmethod
    def enter(self) -> None:
        """进入状态时的操作"""
        self._is_active = True
    
    @abstractmethod
    def exit(self) -> None:
        """退出状态时的操作"""
        self._is_active = False
    
    def on_click(self) -> None:
        """处理点击事件（默认实现）"""
        pass
    
    def on_right_click(self) -> None:
        """处理右键点击事件（默认实现）"""
        if hasattr(self.desktop_pet, 'show_context_menu'):
            self.desktop_pet.show_context_menu()
    
    def on_hover_enter(self) -> None:
        """鼠标悬停进入事件"""
        pass
    
    def on_hover_leave(self) -> None:
        """鼠标悬停离开事件"""
        pass
    
    def get_tooltip_text(self) -> Optional[str]:
        """获取工具提示文本"""
        return f"桌面助手 - {self.state_name}"
    
    def get_speech_text(self) -> Optional[str]:
        """获取状态相关的对话文本"""
        return None
    
    def get_speech_emoji(self) -> Optional[str]:
        """获取状态相关的对话表情"""
        return None
    
    def should_show_speech_on_enter(self) -> bool:
        """是否在进入状态时显示对话气泡"""
        return False
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.state_name})"