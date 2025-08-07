"""
设置标签页模块
"""

from .basic_tab import BasicSettingsTab
from .ai_tab import AISettingsTab
from .ai_auto_tab import AIAutoDetectionTab
from .ai_manual_tab import AIManualConfigTab  
from .appearance_tab import AppearanceSettingsTab
from .about_tab import AboutTab

__all__ = [
    'BasicSettingsTab',
    'AISettingsTab',
    'AIAutoDetectionTab',
    'AIManualConfigTab', 
    'AppearanceSettingsTab',
    'AboutTab'
]