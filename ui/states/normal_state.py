"""
正常状态类
桌面助手的正常工作状态
"""
import logging
import random
from .base_state import BaseState

logger = logging.getLogger(__name__)


class NormalState(BaseState):
    """正常状态类"""
    
    def __init__(self, desktop_pet):
        """
        初始化正常状态
        
        Args:
            desktop_pet: 桌面宠物实例
        """
        super().__init__(desktop_pet, "正常模式")
        
        # 互动对话和表情列表
        self.interaction_messages = [
            ("👋 你好呀~", "wave.gif"),
            ("😊 今天过得怎么样？", "smile.gif"),
            ("🎵 我在这里陪着你哦~", "grin.gif"),
            ("💖 有什么需要帮助的吗？", "love.gif"),
            ("🎉 让我们一起开心吧！", "party.gif"),
            ("😎 我觉得今天是个好日子~", "cool.gif"),
            ("🤔 在想什么有趣的事情吗？", "thinking.gif"),
            ("👍 你真棒！", "thumbs_up.gif"),
            ("✨ 有什么新鲜事吗？", "sparkling_heart.gif"),
            ("🚀 准备好迎接新挑战了吗？", "rocket.gif")
        ]
        
    def enter(self) -> None:
        """进入正常状态"""
        super().enter()
        logger.info("进入正常模式")
        
        # 播放唤醒动画：先设置一个"醒来"的表情，然后切换到正常表情
        if hasattr(self.desktop_pet, 'pet_label'):
            # 先显示"醒来"表情
            self.desktop_pet.pet_label.set_animated_emoji("surprised.gif")
            
            # 延迟一段时间后切换到随机表情
            from PySide6.QtCore import QTimer
            self.wakeup_timer = QTimer()
            self.wakeup_timer.setSingleShot(True)
            self.wakeup_timer.timeout.connect(self._show_normal_emoji)
            self.wakeup_timer.start(1500)  # 1.5秒后切换
        
        # 更新窗口标题
        self.desktop_pet.setWindowTitle("桌面助手 - 已就绪")
        
        # 恢复正常的透明度（带动画效果）
        target_opacity = self.desktop_pet.config.get("transparency", 0.9)
        self._animate_to_opacity(target_opacity)
        
        # 可选：添加弹跳动画表示唤醒
        if hasattr(self.desktop_pet, 'bounce_animation'):
            from PySide6.QtCore import QTimer
            bounce_timer = QTimer()
            bounce_timer.setSingleShot(True)
            bounce_timer.timeout.connect(self.desktop_pet.bounce_animation)
            bounce_timer.start(500)  # 0.5秒后弹跳
        
        logger.info("正常模式激活完成")
    
    def _show_normal_emoji(self):
        """显示正常表情"""
        if hasattr(self.desktop_pet, 'pet_label'):
            self.desktop_pet.pet_label.set_random_animated_emoji()
    
    def _animate_to_opacity(self, target_opacity: float):
        """动画切换到目标透明度"""
        if not self.desktop_pet.config.get("enable_animations", True):
            self.desktop_pet.setWindowOpacity(target_opacity)
            return
        
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve
        
        self.opacity_animation = QPropertyAnimation(self.desktop_pet, b"windowOpacity")
        self.opacity_animation.setDuration(800)  # 0.8秒动画
        self.opacity_animation.setStartValue(self.desktop_pet.windowOpacity())
        self.opacity_animation.setEndValue(target_opacity)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.opacity_animation.start()
    
    def exit(self) -> None:
        """退出正常状态"""
        super().exit()
        logger.info("退出正常模式")
    
    def on_click(self) -> None:
        """处理点击事件"""
        # 正常状态下点击显示互动对话和切换表情
        if hasattr(self.desktop_pet, 'ai_state_manager'):
            message, emoji = random.choice(self.interaction_messages)
            self.desktop_pet.ai_state_manager.show_speech_bubble(message, emoji, 3000)
        logger.debug("正常模式：显示互动对话")
    
    def on_right_click(self) -> None:
        """处理右键点击事件"""
        # 显示完整的右键菜单
        super().on_right_click()
    
    def get_tooltip_text(self) -> str:
        """获取工具提示文本"""
        return "桌面助手已就绪 - 点击互动，右键打开菜单"
    
    def get_context_menu_items(self) -> list:
        """获取状态相关的右键菜单项"""
        # 正常状态下显示所有功能菜单项
        return [
            {"text": "开始专注", "enabled": True, "action": "start_focus"},
        ]
    
    def get_speech_text(self) -> str:
        """获取正常状态的对话文本"""
        return "🎉 唤醒成功！\n我现在精神饱满啦~"
    
    def get_speech_emoji(self) -> str:
        """获取正常状态的表情"""
        return "heart_eyes.gif"
    
    def should_show_speech_on_enter(self) -> bool:
        """正常状态进入时显示庆祝对话"""
        return True