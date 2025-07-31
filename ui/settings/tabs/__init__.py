"""
设置标签页模块
"""

from .basic_tab import BasicSettingsTab
from .ai_tab import AISettingsTab  
from .appearance_tab import AppearanceSettingsTab
from .about_tab import AboutTab

__all__ = [
    'BasicSettingsTab',
    'AISettingsTab', 
    'AppearanceSettingsTab',
    'AboutTab'
]