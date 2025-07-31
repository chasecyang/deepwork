"""
配置管理模块
负责桌宠的配置读取、保存和管理
"""
import json
import os
from typing import Dict, Any


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
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置，确保所有必要的键都存在
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except (json.JSONDecodeError, FileNotFoundError):
                return self.default_config.copy()
        else:
            return self.default_config.copy()
    
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get(self, key: str, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self.config[key] = value
        self.save_config()
    
    def update(self, **kwargs) -> None:
        """批量更新配置"""
        self.config.update(kwargs)
        self.save_config()