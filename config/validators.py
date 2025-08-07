"""
配置验证器
提供各种配置项的验证功能
"""
from typing import Any, Dict, List, Union, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_range(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> bool:
        """验证数值是否在指定范围内"""
        try:
            return min_val <= float(value) <= max_val
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """验证URL格式"""
        if not isinstance(url, str):
            return False
        return url.startswith(('http://', 'https://')) and len(url.strip()) > 8
    
    @staticmethod
    def validate_choice(value: Any, choices: List[Any]) -> bool:
        """验证值是否在选择列表中"""
        return value in choices
    
    @staticmethod
    def validate_window_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """验证窗口配置"""
        validated = {}
        
        # 窗口位置
        validated['window_x'] = max(0, min(config.get('window_x', 100), 3000))
        validated['window_y'] = max(0, min(config.get('window_y', 100), 3000))
        
        # 窗口大小
        validated['window_width'] = max(32, min(config.get('window_width', 64), 200))
        validated['window_height'] = max(32, min(config.get('window_height', 64), 200))
        
        # 透明度
        transparency = config.get('transparency', 0.9)
        validated['transparency'] = max(0.1, min(float(transparency), 1.0))
        
        # 布尔值
        validated['always_on_top'] = bool(config.get('always_on_top', True))
        
        return validated
    
    @staticmethod
    def validate_ai_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """验证AI配置"""
        validated = {}
        
        for model_type in ['vision_model', 'language_model']:
            model_config = config.get(model_type, {})
            validated[model_type] = {
                'base_url': str(model_config.get('base_url', '')).strip(),
                'api_key': str(model_config.get('api_key', '')).strip(),
                'model_name': str(model_config.get('model_name', '')).strip()
            }
        
        return validated
    
    @staticmethod
    def validate_animation_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """验证动画配置"""
        validated = {}
        
        validated['enable_animations'] = bool(config.get('enable_animations', True))
        
        speed = config.get('animation_speed', 200)
        validated['animation_speed'] = max(50, min(int(speed), 1000))
        
        theme = config.get('theme', 'light')
        validated['theme'] = theme if theme in ['light', 'dark'] else 'light'
        
        return validated
    
    @staticmethod
    def validate_focus_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """验证专注功能配置"""
        focus_config = config.get('focus', {})
        validated = {}
        
        # 默认专注时长（分钟）
        duration = focus_config.get('default_duration', 25)
        validated['default_duration'] = max(1, min(int(duration), 240))
        
        # 分析间隔（秒）
        interval = focus_config.get('analysis_interval', 10)
        validated['analysis_interval'] = max(5, min(int(interval), 60))
        
        # 截图质量
        quality = focus_config.get('screenshot_quality', 0.7)
        validated['screenshot_quality'] = max(0.1, min(float(quality), 1.0))
        
        # 专注阈值
        threshold = focus_config.get('focus_threshold', 0.7)
        validated['focus_threshold'] = max(0.1, min(float(threshold), 1.0))
        
        # 布尔值
        validated['enable_notifications'] = bool(focus_config.get('enable_notifications', True))
        validated['save_screenshots'] = bool(focus_config.get('save_screenshots', False))
        
        # 历史记录数
        history = focus_config.get('max_session_history', 10)
        validated['max_session_history'] = max(1, min(int(history), 100))
        
        return validated
