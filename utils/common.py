"""
通用工具函数
将分散的工具功能集中到一个模块
"""
import os
import sys
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class PathUtils:
    """路径工具类"""
    
    @staticmethod
    def get_project_root() -> Path:
        """获取项目根目录"""
        current_file = Path(__file__).resolve()
        # 向上查找包含main.py的目录
        for parent in current_file.parents:
            if (parent / "main.py").exists():
                return parent
        return current_file.parent.parent
    
    @staticmethod
    def get_assets_dir() -> Path:
        """获取资源目录"""
        return PathUtils.get_project_root() / "assets"
    
    @staticmethod
    def get_config_dir() -> Path:
        """获取配置目录"""
        return PathUtils.get_project_root() / "config"
    
    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        """确保目录存在"""
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj


class LogUtils:
    """日志工具类"""
    
    @staticmethod
    def setup_logger(
        name: str,
        level: int = logging.INFO,
        format_string: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(format_string)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @staticmethod
    def suppress_third_party_logs():
        """抑制第三方库的调试日志"""
        third_party_loggers = [
            'openai', 'httpcore', 'httpx', 'urllib3', 
            'aiohttp', 'watchdog', 'PIL'
        ]
        for logger_name in third_party_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)


class ConfigUtils:
    """配置工具类"""
    
    @staticmethod
    def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并配置"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigUtils.merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def validate_required_keys(config: Dict[str, Any], required_keys: List[str]) -> bool:
        """验证配置是否包含必需的键"""
        for key in required_keys:
            if '.' in key:
                # 处理嵌套键（如 'ai.model'）
                current = config
                for part in key.split('.'):
                    if not isinstance(current, dict) or part not in current:
                        return False
                    current = current[part]
            else:
                if key not in config:
                    return False
        return True


class StringUtils:
    """字符串工具类"""
    
    @staticmethod
    def truncate(text: str, max_length: int = 50, suffix: str = "...") -> str:
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def safe_filename(filename: str, replacement: str = "_") -> str:
        """创建安全的文件名"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, replacement)
        return filename.strip()
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


class SystemUtils:
    """系统工具类"""
    
    @staticmethod
    def is_development_mode() -> bool:
        """检查是否是开发模式"""
        return (
            hasattr(sys, 'gettrace') and sys.gettrace() is not None
            or os.environ.get('DEVELOPMENT_MODE', '').lower() == 'true'
            or 'dev_run.py' in sys.argv[0]
        )
    
    @staticmethod
    def get_python_executable() -> str:
        """获取Python可执行文件路径"""
        return sys.executable
    
    @staticmethod
    def restart_application():
        """重启当前应用程序"""
        import subprocess
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(0)


class AsyncUtils:
    """异步工具类"""
    
    @staticmethod
    async def run_with_timeout(coro, timeout: float, default=None):
        """运行协程并设置超时"""
        import asyncio
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"操作超时 ({timeout}s)")
            return default
        except Exception as e:
            logger.error(f"异步操作失败: {e}")
            return default
