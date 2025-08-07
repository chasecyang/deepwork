"""
动画管理器
负责桌面宠物的各种动画效果
"""
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint
import logging

logger = logging.getLogger(__name__)


class AnimationManager:
    """动画管理器"""
    
    def __init__(self, widget, config_manager):
        self.widget = widget
        self.config = config_manager
        self.opacity_animation = None
        self.move_animation = None
        
    def is_animations_enabled(self) -> bool:
        """检查是否启用动画"""
        return self.config.get("enable_animations", True)
        
    def get_animation_speed(self) -> int:
        """获取动画速度"""
        return self.config.get("animation_speed", 200)
        
    def fade_in(self):
        """淡入动画"""
        if not self.is_animations_enabled():
            return
            
        self.opacity_animation = QPropertyAnimation(self.widget, b"windowOpacity")
        self.opacity_animation.setDuration(self.get_animation_speed())
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(self.config.get("transparency", 0.9))
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.opacity_animation.start()
    
    def fade_out(self, callback=None):
        """淡出动画"""
        if not self.is_animations_enabled():
            if callback:
                callback()
            return
            
        self.opacity_animation = QPropertyAnimation(self.widget, b"windowOpacity")
        self.opacity_animation.setDuration(self.get_animation_speed())
        self.opacity_animation.setStartValue(self.widget.windowOpacity())
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        if callback:
            self.opacity_animation.finished.connect(callback)
        
        self.opacity_animation.start()
    
    def bounce_animation(self):
        """弹跳动画效果"""
        if not self.is_animations_enabled():
            return
            
        current_pos = self.widget.pos()
        bounce_height = 20
        
        self.move_animation = QPropertyAnimation(self.widget, b"pos")
        self.move_animation.setDuration(self.get_animation_speed())
        self.move_animation.setStartValue(current_pos)
        self.move_animation.setEndValue(QPoint(current_pos.x(), current_pos.y() - bounce_height))
        self.move_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        # 反弹回来
        def bounce_back():
            back_animation = QPropertyAnimation(self.widget, b"pos")
            back_animation.setDuration(self.get_animation_speed())
            back_animation.setStartValue(QPoint(current_pos.x(), current_pos.y() - bounce_height))
            back_animation.setEndValue(current_pos)
            back_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
            back_animation.start()
        
        self.move_animation.finished.connect(bounce_back)
        self.move_animation.start()
