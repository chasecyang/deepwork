"""
AI状态管理器
负责管理桌面助手的各种状态切换
"""
import logging
from typing import Optional, Dict, Type
from enum import Enum
from PySide6.QtCore import QObject, Signal

from .base_state import BaseState

logger = logging.getLogger(__name__)


class AIStateType(Enum):
    """AI状态类型枚举"""
    AWAKENING = "awakening" # 唤醒状态
    NORMAL = "normal"      # 正常状态
    STANDBY = "standby"    # 待机状态
    FOCUS = "focus"        # 专注状态
    # 未来可以添加更多状态，如：
    # BUSY = "busy"        # 忙碌状态
    # LEARNING = "learning" # 学习状态
    # ERROR = "error"      # 错误状态


class AIStateManager(QObject):
    """AI状态管理器"""
    
    # 状态切换信号
    state_changed = Signal(str, str)  # (old_state, new_state)
    state_entering = Signal(str)      # (new_state)
    state_exited = Signal(str)        # (old_state)
    
    def __init__(self, desktop_pet):
        """
        初始化状态管理器
        
        Args:
            desktop_pet: 桌面宠物实例
        """
        super().__init__()
        self.desktop_pet = desktop_pet
        self.current_state: Optional[BaseState] = None
        self.states: Dict[AIStateType, BaseState] = {}
        
        # 注册状态（延迟导入避免循环依赖）
        self._register_states()
        
        logger.info("AI状态管理器初始化完成")
    
    def _register_states(self):
        """注册所有可用状态"""
        try:
            # 延迟导入避免循环依赖
            from .awakening_state import AwakeningState
            from .normal_state import NormalState
            from .standby_state import StandbyState
            from .focus_state import FocusState
            
            # 注册状态
            self.states[AIStateType.AWAKENING] = AwakeningState(self.desktop_pet)
            self.states[AIStateType.NORMAL] = NormalState(self.desktop_pet)
            self.states[AIStateType.STANDBY] = StandbyState(self.desktop_pet)
            self.states[AIStateType.FOCUS] = FocusState(self.desktop_pet)
            
            logger.info(f"已注册状态: {list(self.states.keys())}")
            
        except ImportError as e:
            logger.error(f"注册状态失败: {e}")
            # 如果状态类还未创建，先创建空的占位状态
            self.states = {}
    
    def switch_to_state(self, state_type: AIStateType) -> bool:
        """
        切换到指定状态
        
        Args:
            state_type: 目标状态类型
            
        Returns:
            bool: 切换是否成功
        """
        if state_type not in self.states:
            logger.error(f"未知状态类型: {state_type}")
            return False
        
        target_state = self.states[state_type]
        
        # 如果已经是目标状态，不做任何操作
        if self.current_state == target_state:
            logger.debug(f"已经处于状态: {state_type.value}")
            return True
        
        old_state_name = self.current_state.state_name if self.current_state else "none"
        new_state_name = target_state.state_name
        
        try:
            # 发出即将切换信号
            self.state_entering.emit(new_state_name)
            
            # 退出当前状态
            if self.current_state:
                logger.info(f"退出状态: {old_state_name}")
                self.current_state.exit()
                self.state_exited.emit(old_state_name)
            
            # 进入新状态
            logger.info(f"🚀 进入状态: {new_state_name}")
            target_state.enter()
            self.current_state = target_state
            logger.info(f"✅ 状态切换成功，当前状态: {new_state_name}")
            
            # 检查是否需要显示对话气泡
            self._handle_speech_bubble_on_enter(target_state)
            
            # 发出状态切换完成信号
            self.state_changed.emit(old_state_name, new_state_name)
            
            logger.info(f"状态切换成功: {old_state_name} -> {new_state_name}")
            return True
            
        except Exception as e:
            logger.error(f"状态切换失败: {old_state_name} -> {new_state_name}, 错误: {e}")
            return False
    
    def switch_to_awakening(self) -> bool:
        """切换到唤醒状态"""
        return self.switch_to_state(AIStateType.AWAKENING)
    
    def switch_to_normal(self) -> bool:
        """切换到正常状态"""
        return self.switch_to_state(AIStateType.NORMAL)
    
    def switch_to_standby(self) -> bool:
        """切换到待机状态"""
        return self.switch_to_state(AIStateType.STANDBY)
    
    def switch_to_focus(self) -> bool:
        """切换到专注状态"""
        return self.switch_to_state(AIStateType.FOCUS)
    
    def get_current_state_type(self) -> Optional[AIStateType]:
        """
        获取当前状态类型
        
        Returns:
            Optional[AIStateType]: 当前状态类型，如果无状态则返回None
        """
        if not self.current_state:
            return None
        
        # 根据状态名称找到对应的枚举
        for state_type, state in self.states.items():
            if state == self.current_state:
                return state_type
        
        return None
    
    def get_current_state_name(self) -> str:
        """
        获取当前状态名称
        
        Returns:
            str: 当前状态名称
        """
        if self.current_state:
            return self.current_state.state_name
        return "none"
    
    def is_in_state(self, state_type: AIStateType) -> bool:
        """
        检查是否处于指定状态
        
        Args:
            state_type: 状态类型
            
        Returns:
            bool: 是否处于指定状态
        """
        return self.get_current_state_type() == state_type
    
    def handle_click(self) -> None:
        """处理点击事件"""
        if self.current_state:
            self.current_state.on_click()
    
    def handle_right_click(self) -> None:
        """处理右键点击事件"""
        if self.current_state:
            self.current_state.on_right_click()
    
    def handle_hover_enter(self) -> None:
        """处理鼠标悬停进入事件"""
        if self.current_state:
            self.current_state.on_hover_enter()
    
    def handle_hover_leave(self) -> None:
        """处理鼠标悬停离开事件"""
        if self.current_state:
            self.current_state.on_hover_leave()
    
    def get_tooltip_text(self) -> Optional[str]:
        """
        获取当前状态的工具提示文本
        
        Returns:
            Optional[str]: 工具提示文本
        """
        if self.current_state:
            return self.current_state.get_tooltip_text()
        return None
    

    
    def on_config_changed(self) -> None:
        """配置变化时的回调"""
        current_state = self.get_current_state_name()
        logger.info(f"配置已更改，当前状态: {current_state}")
    
    def reload_states(self) -> None:
        """重新加载状态（用于调试）"""
        current_state_type = self.get_current_state_type()
        self._register_states()
        if current_state_type and current_state_type in self.states:
            self.switch_to_state(current_state_type)
    
    def _handle_speech_bubble_on_enter(self, state):
        """处理状态进入时的对话气泡显示"""
        if not state.should_show_speech_on_enter():
            return
            
        speech_text = state.get_speech_text()
        speech_emoji = state.get_speech_emoji()
        
        if speech_text and hasattr(self.desktop_pet, 'show_speech_bubble'):
            self.desktop_pet.show_speech_bubble(speech_text, speech_emoji)
    
    def show_speech_bubble(self, text: str, emoji: str = None, duration: int = 3000):
        """显示对话气泡（供状态调用）"""
        if hasattr(self.desktop_pet, 'show_speech_bubble'):
            self.desktop_pet.show_speech_bubble(text, emoji, duration)
    
    def __repr__(self) -> str:
        """调试字符串表示"""
        current_name = self.get_current_state_name()
        state_count = len(self.states)
        return f"AIStateManager(current='{current_name}', states={state_count})"