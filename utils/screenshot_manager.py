"""
截图管理器
负责屏幕截图、文件管理和图像处理
"""
import os
import time
import tempfile
import logging
from typing import Optional, Tuple
from PIL import Image, ImageGrab
import platform

logger = logging.getLogger(__name__)


class ScreenshotManager:
    """截图管理器类"""
    
    def __init__(self, config: dict = None):
        """
        初始化截图管理器
        
        Args:
            config: 配置字典，包含截图相关设置
        """
        self.config = config or {}
        self.temp_dir = tempfile.mkdtemp(prefix="deepwork_screenshots_")
        self.screenshot_quality = self.config.get("screenshot_quality", 0.7)
        self.save_screenshots = self.config.get("save_screenshots", False)
        self.max_width = 1920  # 最大宽度，用于压缩
        self.max_height = 1080  # 最大高度，用于压缩
        
        logger.info(f"截图管理器初始化完成，临时目录: {self.temp_dir}")
    
    def take_screenshot(self, compress: bool = True) -> Optional[str]:
        """
        截取当前屏幕
        
        Args:
            compress: 是否压缩图像
            
        Returns:
            Optional[str]: 截图文件路径，失败返回None
        """
        try:
            # 使用PIL截图（跨平台）
            screenshot = ImageGrab.grab()
            
            if screenshot is None:
                logger.error("截图失败：无法获取屏幕内容")
                return None
            
            # 压缩处理
            if compress:
                screenshot = self._compress_image(screenshot)
            
            # 生成文件名
            timestamp = int(time.time() * 1000)
            filename = f"screenshot_{timestamp}.jpg"
            filepath = os.path.join(self.temp_dir, filename)
            
            # 保存截图 - 确保转换为RGB模式（JPEG不支持透明度）
            if screenshot.mode == 'RGBA':
                # 创建白色背景
                rgb_screenshot = Image.new('RGB', screenshot.size, (255, 255, 255))
                rgb_screenshot.paste(screenshot, mask=screenshot.split()[-1])  # 使用alpha通道作为遮罩
                screenshot = rgb_screenshot
            elif screenshot.mode != 'RGB':
                screenshot = screenshot.convert('RGB')
            
            screenshot.save(filepath, "JPEG", quality=int(self.screenshot_quality * 100))
            
            logger.debug(f"截图已保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None
    
    def _compress_image(self, image: Image.Image) -> Image.Image:
        """
        压缩图像以减少文件大小和API调用成本
        
        Args:
            image: 原始图像
            
        Returns:
            Image.Image: 压缩后的图像
        """
        # 获取原始尺寸
        width, height = image.size
        
        # 计算压缩比例
        if width > self.max_width or height > self.max_height:
            # 计算等比例缩放
            width_ratio = self.max_width / width
            height_ratio = self.max_height / height
            ratio = min(width_ratio, height_ratio)
            
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # 使用高质量重采样
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            logger.debug(f"图像已压缩: {width}x{height} -> {new_width}x{new_height}")
        
        # 确保图像模式兼容JPEG保存
        if image.mode == 'RGBA':
            # 创建白色背景
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1])  # 使用alpha通道作为遮罩
            image = rgb_image
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    def get_screenshot_info(self, filepath: str) -> Optional[dict]:
        """
        获取截图信息
        
        Args:
            filepath: 截图文件路径
            
        Returns:
            Optional[dict]: 截图信息字典
        """
        try:
            if not os.path.exists(filepath):
                return None
            
            # 获取文件信息
            stat = os.stat(filepath)
            
            # 获取图像信息
            with Image.open(filepath) as img:
                width, height = img.size
                format_name = img.format
            
            return {
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "width": width,
                "height": height,
                "format": format_name,
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime
            }
            
        except Exception as e:
            logger.error(f"获取截图信息失败: {e}")
            return None
    
    def cleanup_old_screenshots(self, keep_count: int = 10):
        """
        清理旧的截图文件
        
        Args:
            keep_count: 保留的文件数量
        """
        try:
            # 获取所有截图文件
            files = []
            for filename in os.listdir(self.temp_dir):
                if filename.startswith("screenshot_") and filename.endswith(".jpg"):
                    filepath = os.path.join(self.temp_dir, filename)
                    files.append((filepath, os.path.getctime(filepath)))
            
            # 按创建时间排序（最新的在前）
            files.sort(key=lambda x: x[1], reverse=True)
            
            # 删除多余的文件
            deleted_count = 0
            for filepath, _ in files[keep_count:]:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except OSError as e:
                    logger.warning(f"删除文件失败: {filepath}, {e}")
            
            if deleted_count > 0:
                logger.debug(f"清理了 {deleted_count} 个旧截图文件")
                
        except Exception as e:
            logger.error(f"清理截图文件失败: {e}")
    
    def delete_screenshot(self, filepath: str) -> bool:
        """
        删除指定的截图文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            bool: 是否删除成功
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.debug(f"已删除截图: {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除截图失败: {filepath}, {e}")
            return False
    
    def cleanup_all(self):
        """清理所有临时文件"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"已清理所有临时文件: {self.temp_dir}")
        except Exception as e:
            logger.error(f"清理临时目录失败: {e}")
    
    def get_display_info(self) -> dict:
        """
        获取显示器信息
        
        Returns:
            dict: 显示器信息
        """
        try:
            # 获取主屏幕尺寸
            screenshot = ImageGrab.grab()
            if screenshot:
                width, height = screenshot.size
                return {
                    "width": width,
                    "height": height,
                    "platform": platform.system(),
                    "available": True
                }
            else:
                return {"available": False}
                
        except Exception as e:
            logger.error(f"获取显示器信息失败: {e}")
            return {"available": False, "error": str(e)}
    
    def test_screenshot_capability(self) -> Tuple[bool, str]:
        """
        测试截图功能是否正常
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 尝试截图
            filepath = self.take_screenshot()
            
            if filepath and os.path.exists(filepath):
                # 验证文件大小
                size = os.path.getsize(filepath)
                if size > 0:
                    # 清理测试文件
                    self.delete_screenshot(filepath)
                    return True, "截图功能正常"
                else:
                    return False, "截图文件为空"
            else:
                return False, "截图创建失败"
                
        except Exception as e:
            return False, f"截图测试失败: {e}"
    
    def __del__(self):
        """析构函数，清理临时文件"""
        if hasattr(self, 'temp_dir') and not self.save_screenshots:
            self.cleanup_all()


# 全局截图管理器实例
_screenshot_manager = None


def get_screenshot_manager(config: dict = None) -> ScreenshotManager:
    """
    获取全局截图管理器实例
    
    Args:
        config: 配置字典
        
    Returns:
        ScreenshotManager: 截图管理器实例
    """
    global _screenshot_manager
    
    if _screenshot_manager is None:
        _screenshot_manager = ScreenshotManager(config)
    
    return _screenshot_manager