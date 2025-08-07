"""
配置管理模块（重构版）
负责桌宠的配置读取、保存和管理，增加了验证功能
"""
import json
import os
import logging
from typing import Dict, Any, Optional
from .validators import ConfigValidator

logger = logging.getLogger(__name__)


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "pet_name": "小助手",
            "window_x": 100,
            "window_y": 100,
            "window_width": 64,  # 更小的宽度，适合无边框桌宠
            "window_height": 64,  # 更小的高度，适合表情显示
            "always_on_top": True,
            "transparency": 0.9,
            # AI模型设置
            "vision_model": {
                "base_url": "",
                "api_key": "",
                "model_name": ""
            },
            "language_model": {
                "base_url": "",
                "api_key": "",
                "model_name": ""
            },
            # 主题和外观设置
            "theme": "light",  # light 或 dark
            "enable_animations": True,
            "animation_speed": 200,  # 毫秒
            # 专注功能设置
            "focus": {
                "default_duration": 25,  # 默认专注时长（分钟）
                "analysis_interval": 10,  # 分析间隔（秒）
                "screenshot_quality": 0.7,  # 截图质量（0-1）
                "enable_notifications": True,  # 是否启用通知
                "save_screenshots": False,  # 是否保存截图（调试用）
                "max_session_history": 10  # 最大会话历史记录数
            },
            # AI随机对话设置
            "enable_ai_random_chat": True,  # 是否启用正常状态下的AI随机对话
            "ai_random_chat_min_interval": 30,  # AI随机对话最小间隔（秒，默认30秒）
            "ai_random_chat_max_interval": 60,  # AI随机对话最大间隔（秒，默认1分钟）
            "enable_ai_encourage_in_standby": True,  # 是否在待机状态启用AI鼓励
            "ai_encourage_min_interval": 600,  # AI鼓励最小间隔（秒，默认10分钟）
            "ai_encourage_max_interval": 1200  # AI鼓励最大间隔（秒，默认20分钟）
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载并验证配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置
                merged_config = self.default_config.copy()
                merged_config.update(config)
                # 验证配置
                return self._validate_config(merged_config)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.warning(f"配置文件加载失败: {e}，使用默认配置")
                return self.default_config.copy()
        else:
            logger.info("配置文件不存在，使用默认配置")
            return self.default_config.copy()
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证配置并返回验证后的配置"""
        validated = {}
        
        try:
            # 验证窗口配置
            validated.update(ConfigValidator.validate_window_config(config))
            
            # 验证AI配置
            validated.update(ConfigValidator.validate_ai_config(config))
            
            # 验证动画配置
            validated.update(ConfigValidator.validate_animation_config(config))
            
            # 验证专注功能配置
            validated['focus'] = ConfigValidator.validate_focus_config(config)
            
            # 保留其他未验证的配置项
            for key, value in config.items():
                if key not in validated and key != 'focus':
                    validated[key] = value
                    
            return validated
            
        except Exception as e:
            logger.error(f"配置验证失败: {e}，使用默认配置")
            return self.default_config.copy()
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            # 验证配置再保存
            validated_config = self._validate_config(self.config)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(validated_config, f, ensure_ascii=False, indent=2)
            self.config = validated_config
            logger.debug("配置保存成功")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def get(self, key: str, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置值"""
        old_value = self.config.get(key)
        self.config[key] = value
        if self.save_config():
            logger.debug(f"配置更新: {key} = {value} (旧值: {old_value})")
            return True
        else:
            self.config[key] = old_value  # 回滚
            return False
    
    def update(self, **kwargs) -> bool:
        """批量更新配置"""
        old_config = self.config.copy()
        self.config.update(kwargs)
        if self.save_config():
            changes = {k: v for k, v in kwargs.items() if old_config.get(k) != v}
            logger.debug(f"批量配置更新: {changes}")
            return True
        else:
            self.config = old_config  # 回滚
            return False
    
    def get_nested(self, keys: str, default=None):
        """获取嵌套配置值，使用点分隔的键"""
        try:
            value = self.config
            for key in keys.split('.'):
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_nested(self, keys: str, value: Any) -> bool:
        """设置嵌套配置值，使用点分隔的键"""
        try:
            config_copy = self.config.copy()
            current = config_copy
            key_list = keys.split('.')
            
            # 导航到最后一个键的父级
            for key in key_list[:-1]:
                if key not in current or not isinstance(current[key], dict):
                    current[key] = {}
                current = current[key]
            
            # 设置最后一个键的值
            current[key_list[-1]] = value
            
            # 尝试保存
            old_config = self.config
            self.config = config_copy
            if self.save_config():
                logger.debug(f"嵌套配置更新: {keys} = {value}")
                return True
            else:
                self.config = old_config
                return False
                
        except Exception as e:
            logger.error(f"设置嵌套配置失败: {e}")
            return False