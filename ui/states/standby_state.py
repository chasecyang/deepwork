"""
待机状态类
桌面助手的待机等待状态，用于AI功能不可用时
"""
import logging
import os
from PySide6.QtWidgets import QToolTip
from PySide6.QtCore import QTimer, QRect
from PySide6.QtGui import QCursor
from .base_state import BaseState

logger = logging.getLogger(__name__)


class StandbyState(BaseState):
    """待机状态类"""
    
    def __init__(self, desktop_pet):
        """
        初始化待机状态
        
        Args:
            desktop_pet: 桌面宠物实例
        """
        super().__init__(desktop_pet, "待机模式")
        
        # 用于定期显示提示的定时器
        self.hint_timer = QTimer()
        self.hint_timer.timeout.connect(self._show_periodic_hint)
        self.hint_timer.setSingleShot(True)
        
        # 睡眠表情列表
        self.standby_emojis = [
            "sleeping.gif",
            "confused.gif", 
            "thinking.gif"
        ]
        
    def enter(self) -> None:
        """进入待机状态"""
        super().enter()
        logger.info("进入待机模式")
        
        # 直接设置睡眠表情，不要中间的困倦表情动画
        if hasattr(self.desktop_pet, 'pet_label'):
            self._set_standby_emoji()
        
        # 更新窗口标题
        self.desktop_pet.setWindowTitle("桌面助手 - 等待唤醒")
        
        # 动画降低透明度，表示非活跃状态
        original_opacity = self.desktop_pet.config.get("transparency", 0.9)
        standby_opacity = max(0.3, original_opacity - 0.2)  # 降低透明度但不要太透明
        self._animate_to_opacity(standby_opacity)
        
        # 延迟显示配置提示，等动画完成
        from PySide6.QtCore import QTimer
        hint_delay_timer = QTimer()
        hint_delay_timer.setSingleShot(True)
        hint_delay_timer.timeout.connect(self._show_config_hint)
        hint_delay_timer.start(3000)  # 3秒后显示提示
        
        # 设置定期提示（30秒后再次提示）
        self.hint_timer.start(30000)  # 30秒
        
        logger.info("待机模式激活完成")
    
    def _animate_to_opacity(self, target_opacity: float):
        """动画切换到目标透明度"""
        if not self.desktop_pet.config.get("enable_animations", True):
            self.desktop_pet.setWindowOpacity(target_opacity)
            return
        
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve
        
        self.opacity_animation = QPropertyAnimation(self.desktop_pet, b"windowOpacity")
        self.opacity_animation.setDuration(1500)  # 1.5秒动画，比唤醒慢一些
        self.opacity_animation.setStartValue(self.desktop_pet.windowOpacity())
        self.opacity_animation.setEndValue(target_opacity)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.opacity_animation.start()
    
    def exit(self) -> None:
        """退出待机状态"""
        super().exit()
        logger.info("退出待机模式")
        
        # 停止提示定时器
        self.hint_timer.stop()
        
        # 隐藏可能显示的工具提示
        QToolTip.hideText()
    
    def on_click(self) -> None:
        """处理点击事件"""
        # 待机模式下点击直接弹出AI配置页面
        self._show_ai_config_dialog()
        self._set_standby_emoji()
        logger.debug("待机模式：弹出AI配置页面")
    
    def on_right_click(self) -> None:
        """处理右键点击事件"""
        # 显示右键菜单，突出设置选项
        super().on_right_click()
    
    def on_hover_enter(self) -> None:
        """鼠标悬停进入事件"""
        # 显示详细的配置提示
        tooltip_text = self.get_tooltip_text()
        if tooltip_text:
            QToolTip.showText(QCursor.pos(), tooltip_text, self.desktop_pet)
    
    def on_hover_leave(self) -> None:
        """鼠标悬停离开事件"""
        # 隐藏工具提示
        QToolTip.hideText()
    
    def get_tooltip_text(self) -> str:
        """获取工具提示文本"""
        return (
            "🛌 助手正在休眠\n"
            "请配置AI模型后唤醒助手\n\n"
            "💡 操作提示：\n"
            "• 右键 → 设置 → AI模型\n"
            "• 填写模型配置信息\n"
            "• 点击测试按钮验证\n"
            "• 测试通过后助手将自动唤醒"
        )
    
    def get_context_menu_items(self) -> list:
        """获取状态相关的右键菜单项"""
        # 待机状态下突出显示设置选项
        return [
            {"text": "⚙️ 配置AI模型", "enabled": True, "action": "settings", "highlight": True},
            {"text": "❓ 唤醒助手", "enabled": False, "action": "wakeup_help"},
        ]
    
    def get_speech_text(self) -> str:
        """获取待机状态的对话文本"""
        return "😴 未检测到可用的AI模型\n需要配置AI能力唤醒我哦~"
    
    def get_speech_emoji(self) -> str:
        """获取待机状态的表情"""
        return "sleeping.gif"
    
    def should_show_speech_on_enter(self) -> bool:
        """待机状态进入时显示对话"""
        return True
    
    def _set_standby_emoji(self) -> None:
        """设置待机表情"""
        if not hasattr(self.desktop_pet, 'pet_label'):
            return
            
        try:
            # 优先使用睡眠表情
            emoji_file = "sleeping.gif"
            emoji_path = os.path.join("assets", "animated_emojis", emoji_file)
            
            if os.path.exists(emoji_path):
                self.desktop_pet.pet_label.set_animated_emoji(emoji_file)
                logger.debug(f"设置待机表情: {emoji_file}")
            else:
                # 如果睡眠表情不存在，尝试其他表情
                for emoji_file in self.standby_emojis:
                    emoji_path = os.path.join("assets", "animated_emojis", emoji_file)
                    if os.path.exists(emoji_path):
                        self.desktop_pet.pet_label.set_animated_emoji(emoji_file)
                        logger.debug(f"设置待机表情: {emoji_file}")
                        break
                else:
                    # 如果都不存在，使用随机表情
                    self.desktop_pet.pet_label.set_random_animated_emoji()
                    logger.warning("待机表情文件不存在，使用随机表情")
                    
        except Exception as e:
            logger.error(f"设置待机表情失败: {e}")
    
    def _show_config_hint(self) -> None:
        """显示配置提示"""
        try:
            hint_text = (
                "💤 助手正在休眠\n"
                "请右键打开设置配置AI模型"
            )
            
            # 在鼠标当前位置附近显示提示
            cursor_pos = QCursor.pos()
            QToolTip.showText(cursor_pos, hint_text, self.desktop_pet, QRect(), 3000)
            
            logger.debug("显示配置提示")
            
        except Exception as e:
            logger.error(f"显示配置提示失败: {e}")
    
    def _show_periodic_hint(self) -> None:
        """定期显示提示"""
        if self.is_active:  # 只有在待机状态下才显示提示
            self._show_config_hint()
            # 重新设置定时器，1分钟后再次提示
            self.hint_timer.start(60000)  # 1分钟
    
    def _show_ai_config_dialog(self):
        """显示AI配置对话框"""
        try:
            logger.info("待机状态点击，弹出AI配置对话框")
            
            if hasattr(self.desktop_pet, 'open_settings'):
                # 调用桌面宠物的设置方法
                self.desktop_pet.open_settings()
                
                # 延迟切换到AI标签页，确保对话框完全加载
                from PySide6.QtCore import QTimer
                switch_timer = QTimer()
                switch_timer.setSingleShot(True)
                switch_timer.timeout.connect(self._switch_to_ai_tab)
                switch_timer.start(200)  # 延迟200ms
                
            else:
                logger.warning("桌面宠物没有open_settings方法")
                
        except Exception as e:
            logger.error(f"弹出AI配置对话框失败: {e}")
    
    def _switch_to_ai_tab(self):
        """切换到AI配置标签页"""
        try:
            if hasattr(self.desktop_pet, 'settings_dialog') and self.desktop_pet.settings_dialog:
                # 获取标签页组件并切换到AI标签页
                from PySide6.QtWidgets import QTabWidget
                tab_widget = self.desktop_pet.settings_dialog.findChild(QTabWidget)
                if tab_widget:
                    # AI标签页通常是第二个标签页（索引1）
                    tab_widget.setCurrentIndex(1)
                    logger.info("已切换到AI配置标签页")
                    
        except Exception as e:
            logger.error(f"切换到AI标签页失败: {e}")