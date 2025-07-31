"""
桌面助手状态管理模块
提供可扩展的状态管理系统
"""

from .ai_state_manager import AIStateManager
from .base_state import BaseState
from .normal_state import NormalState
from .standby_state import StandbyState
from .awakening_state import AwakeningState

__all__ = [
    "AIStateManager",
    "BaseState", 
    "NormalState",
    "StandbyState",
    "AwakeningState"
]