"""
待机状态类
桌面助手的待机等待状态，用于AI功能不可用时
"""
import logging
import os
import random
import asyncio
from PySide6.QtWidgets import QToolTip
from PySide6.QtCore import QTimer, QRect, QThread, Signal
from PySide6.QtGui import QCursor
from .base_state import BaseState
from utils.ai_client import ai_client

logger = logging.getLogger(__name__)


class AIEncourageWorker(QThread):
    """AI鼓励工作线程"""
    encourage_complete = Signal(str, str)  # (message, emoji)
    encourage_failed = Signal()
    
    def __init__(self, language_config, prompts):
        super().__init__()
        self.language_config = language_config
        self.prompts = prompts
    
    def run(self):
        """在工作线程中运行异步AI调用"""
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 运行异步任务
            result = loop.run_until_complete(self._call_ai())
            
            if result:
                message, emoji = result
                self.encourage_complete.emit(message, emoji)
            else:
                self.encourage_failed.emit()
                
        except Exception as e:
            logger.error(f"AI鼓励工作线程失败: {e}")
            self.encourage_failed.emit()
        finally:
            loop.close()
    
    async def _call_ai(self):
        """异步调用AI"""
        try:
            # 随机选择提示词
            prompt = random.choice(self.prompts)
            
            # 调用AI生成鼓励内容
            response = await ai_client.call_language_model(self.language_config, prompt)
            
            if response:
                # 清理响应内容
                clean_response = self._clean_ai_response(response)
                
                if clean_response:
                    # 选择合适的表情
                    emojis = ["sleeping.gif", "thinking.gif", "confused.gif", "wink.gif"]
                    emoji = random.choice(emojis)
                    return clean_response, emoji
            
            return None
            
        except Exception as e:
            logger.error(f"AI调用失败: {e}")
            return None
    
    def _clean_ai_response(self, response: str) -> str:
        """清理AI响应内容"""
        if not response:
            return ""
            
        # 移除多余的空白字符
        clean = response.strip()
        
        # 移除引号
        if clean.startswith('"') and clean.endswith('"'):
            clean = clean[1:-1]
        if clean.startswith("'") and clean.endswith("'"):
            clean = clean[1:-1]
            
        # 限制长度（最多60个字符，待机状态可以稍长一些）
        if len(clean) > 60:
            clean = clean[:57] + "..."
            
        return clean


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
        
        # AI鼓励定时器
        self.ai_encourage_timer = QTimer()
        self.ai_encourage_timer.setSingleShot(True)
        self.ai_encourage_timer.timeout.connect(self._trigger_ai_encourage)
        
        # AI工作线程
        self.ai_encourage_worker = None
        
        # 睡眠表情列表
        self.standby_emojis = [
            "sleeping.gif",
            "confused.gif", 
            "thinking.gif"
        ]
        
        # 鼓励性质的AI提示词模板
        self.ai_encourage_prompts = [
            "作为一个休眠中的桌面助手，温柔地提醒用户配置AI功能来唤醒你（不超过20个字）",
            "你是一个等待配置的AI宠物，可爱地表达期待被唤醒的心情（不超过20个字）",
            "作为待机的小助手，友善地鼓励用户完成配置享受AI功能（不超过20个字）",
            "你正在休眠等待，简短温馨地说明配置AI后可以做什么（不超过20个字）"
        ]
        
        # 预设的鼓励话语
        self.encourage_messages = [
            ("😴 配置AI后我就能陪你聊天啦~", "sleeping.gif"),
            ("💤 设置一下AI模型，让我苏醒吧", "confused.gif"),
            ("🤔 好想和你对话呢，快配置AI吧", "thinking.gif"),
            ("😊 右键设置AI，解锁更多功能哦", "smile.gif"),
            ("💡 配置完成后我会变得更智能~", "wink.gif"),
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
        hint_delay_timer = QTimer()
        hint_delay_timer.setSingleShot(True)
        hint_delay_timer.timeout.connect(self._show_config_hint)
        hint_delay_timer.start(3000)  # 3秒后显示提示
        
        # 设置定期提示（30秒后再次提示）
        self.hint_timer.start(30000)  # 30秒
        
        # 启动AI鼓励定时器
        self._schedule_next_ai_encourage()
        
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
        
        # 停止AI鼓励定时器
        if hasattr(self, 'ai_encourage_timer') and self.ai_encourage_timer.isActive():
            self.ai_encourage_timer.stop()
        
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
                switch_timer.timeout.connect(self._switch_to_ai_auto_tab)
                switch_timer.start(200)  # 延迟200ms
                
            else:
                logger.warning("桌面宠物没有open_settings方法")
                
        except Exception as e:
            logger.error(f"弹出AI配置对话框失败: {e}")
    
    def _switch_to_ai_auto_tab(self):
        """切换到AI自动检测标签页"""
        try:
            if hasattr(self.desktop_pet, 'settings_dialog') and self.desktop_pet.settings_dialog:
                # 获取主标签页组件并切换到AI配置标签页
                from PySide6.QtWidgets import QTabWidget
                main_tab_widget = self.desktop_pet.settings_dialog.findChild(QTabWidget)
                if main_tab_widget:
                    # AI配置是第二个标签页（索引1）
                    main_tab_widget.setCurrentIndex(1)
                    
                    # 获取AI配置tab并切换到自动检测子tab
                    ai_tab = self.desktop_pet.settings_dialog.ai_tab
                    if ai_tab and hasattr(ai_tab, 'switch_to_auto_detection'):
                        ai_tab.switch_to_auto_detection()
                        logger.info("已切换到AI自动检测标签页")
                    
        except Exception as e:
            logger.error(f"切换到AI自动检测标签页失败: {e}")
    
    def _schedule_next_ai_encourage(self):
        """安排下一次AI鼓励"""
        if not self.desktop_pet.config.get("enable_ai_encourage_in_standby", True):
            return
            
        # 待机状态下的鼓励间隔更长，默认10-20分钟
        min_interval = self.desktop_pet.config.get("ai_encourage_min_interval", 600)  # 10分钟
        max_interval = self.desktop_pet.config.get("ai_encourage_max_interval", 1200)  # 20分钟
        
        interval = random.randint(min_interval, max_interval) * 1000  # 转换为毫秒
        
        if hasattr(self, 'ai_encourage_timer') and self.is_active:
            self.ai_encourage_timer.start(interval)
            logger.debug(f"安排下次AI鼓励，间隔: {interval/1000:.1f}秒")
    
    def _trigger_ai_encourage(self):
        """触发AI鼓励"""
        if not self.is_active:
            return
            
        logger.info("触发AI鼓励")
        
        # 检查是否有工作线程正在运行
        if self.ai_encourage_worker and self.ai_encourage_worker.isRunning():
            logger.debug("AI鼓励工作线程正在运行，跳过本次鼓励")
            self._schedule_next_ai_encourage()
            return
        
        # 检查是否有配置的语言模型，如果有就尝试AI生成，否则使用预设
        language_config = self.desktop_pet.config.get("language_model", {})
        
        if self._is_language_model_configured(language_config):
            # 启动AI工作线程
            self.ai_encourage_worker = AIEncourageWorker(language_config, self.ai_encourage_prompts)
            self.ai_encourage_worker.encourage_complete.connect(self._on_ai_encourage_complete)
            self.ai_encourage_worker.encourage_failed.connect(self._on_ai_encourage_failed)
            self.ai_encourage_worker.start()
        else:
            # 使用预设鼓励话语
            self._show_preset_encourage()
        
        # 安排下一次鼓励
        self._schedule_next_ai_encourage()
    
    def _on_ai_encourage_complete(self, message: str, emoji: str):
        """AI鼓励完成回调"""
        if hasattr(self.desktop_pet, 'ai_state_manager'):
            self.desktop_pet.ai_state_manager.show_speech_bubble(message, emoji, 5000)
            logger.info(f"AI鼓励: {message}")
    
    def _on_ai_encourage_failed(self):
        """AI鼓励失败回调"""
        logger.debug("AI鼓励调用失败，使用预设鼓励")
        self._show_preset_encourage()
    
    def _show_preset_encourage(self):
        """显示预设鼓励话语"""
        message, emoji = random.choice(self.encourage_messages)
        if hasattr(self.desktop_pet, 'ai_state_manager'):
            self.desktop_pet.ai_state_manager.show_speech_bubble(message, emoji, 4000)
            logger.info(f"预设鼓励: {message}")
    
    def _is_language_model_configured(self, config: dict) -> bool:
        """检查语言模型是否已配置"""
        return (
            config.get("base_url") and 
            config.get("model_name") and
            config.get("base_url").strip() != "" and
            config.get("model_name").strip() != ""
        )