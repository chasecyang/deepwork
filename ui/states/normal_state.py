"""
正常状态类
桌面助手的正常工作状态
"""
import logging
import random
import asyncio
from PySide6.QtCore import QTimer, QThread, Signal
from .base_state import BaseState
from utils.ai_client import ai_client

logger = logging.getLogger(__name__)


class AIInteractionWorker(QThread):
    """AI互动工作线程"""
    interaction_complete = Signal(str, str)  # (message, emoji)
    interaction_failed = Signal()
    
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
                self.interaction_complete.emit(message, emoji)
            else:
                self.interaction_failed.emit()
                
        except Exception as e:
            logger.error(f"AI互动工作线程失败: {e}")
            self.interaction_failed.emit()
        finally:
            loop.close()
    
    async def _call_ai(self):
        """异步调用AI"""
        try:
            # 随机选择提示词
            prompt = random.choice(self.prompts)
            
            # 调用AI生成对话
            response = await ai_client.call_language_model(self.language_config, prompt)
            
            if response:
                # 清理响应内容
                clean_response = self._clean_ai_response(response)
                
                if clean_response:
                    # 随机选择表情
                    emojis = [
                        "smile.gif", "grin.gif", "love.gif", "heart_eyes.gif",
                        "wink.gif", "laugh.gif", "joy.gif", "cool.gif",
                        "thumbs_up.gif", "party.gif", "rocket.gif", "sparkling_heart.gif"
                    ]
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
            
        # 限制长度（最多50个字符）
        if len(clean) > 50:
            clean = clean[:47] + "..."
            
        return clean


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
        
        # AI随机对话定时器
        self.ai_random_timer = QTimer()
        self.ai_random_timer.setSingleShot(True)
        self.ai_random_timer.timeout.connect(self._trigger_ai_random_interaction)
        
        # AI工作线程
        self.ai_worker = None
        
        # AI提示词模板
        self.ai_prompts = [
            "作为桌面助手，给用户一个简短的正能量鼓励（不超过15个字）",
            "背一首古诗",
            "哼一句歌，情绪丰富，情绪饱满",
            "吐槽一下工作",
            "锐评一下最近的热点新闻",
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
        if hasattr(self.desktop_pet, 'animation_manager'):
            bounce_timer = QTimer()
            bounce_timer.setSingleShot(True)
            bounce_timer.timeout.connect(self.desktop_pet.animation_manager.bounce_animation)
            bounce_timer.start(500)  # 0.5秒后弹跳
        
        # 启动AI随机对话定时器
        self._schedule_next_ai_interaction()
        
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
        
        # 停止AI随机对话定时器
        if hasattr(self, 'ai_random_timer') and self.ai_random_timer.isActive():
            self.ai_random_timer.stop()
            
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
        # 创建动态右键菜单
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction, QCursor
        from ..theme import ModernTheme
        
        menu = QMenu(self.desktop_pet)
        menu.setStyleSheet(ModernTheme.get_menu_style())
        
        # 添加开始专注功能
        focus_action = QAction("🎯 开始专注", self.desktop_pet)
        focus_action.triggered.connect(self._start_focus)
        menu.addAction(focus_action)
        
        menu.addSeparator()
        
        # 添加专注历史
        focus_history_action = QAction("📈 专注历史", self.desktop_pet)
        focus_history_action.triggered.connect(self.desktop_pet._open_focus_history)
        menu.addAction(focus_history_action)
        
        menu.addSeparator()
        
        # 添加设置
        settings_action = QAction("设置", self.desktop_pet)
        settings_action.triggered.connect(self.desktop_pet._open_settings)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # 添加退出
        quit_action = QAction("退出", self.desktop_pet)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(quit_action)
        
        menu.exec(QCursor.pos())
    
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
    
    def _schedule_next_ai_interaction(self):
        """安排下一次AI随机互动"""
        if not self._is_ai_enabled():
            return
            
        # 获取配置的互动间隔，默认30-60秒之间随机
        min_interval = self.desktop_pet.config.get("ai_random_chat_min_interval", 30)  # 30秒
        max_interval = self.desktop_pet.config.get("ai_random_chat_max_interval", 60)  # 60秒
        
        # 检查是否启用AI随机对话
        if not self.desktop_pet.config.get("enable_ai_random_chat", True):
            return
            
        interval = random.randint(min_interval, max_interval) * 1000  # 转换为毫秒
        
        if hasattr(self, 'ai_random_timer') and self.is_active:
            self.ai_random_timer.start(interval)
            logger.debug(f"安排下次AI互动，间隔: {interval/1000:.1f}秒")
    
    def _trigger_ai_random_interaction(self):
        """触发AI随机互动"""
        if not self.is_active or not self._is_ai_enabled():
            return
            
        logger.info("触发AI随机互动")
        
        # 检查是否有工作线程正在运行
        if self.ai_worker and self.ai_worker.isRunning():
            logger.debug("AI工作线程正在运行，跳过本次互动")
            self._schedule_next_ai_interaction()
            return
        
        # 获取语言模型配置
        language_config = self.desktop_pet.config.get("language_model", {})
        
        if not self._is_language_model_configured(language_config):
            logger.debug("语言模型未配置，使用预设对话")
            self._show_preset_interaction()
            self._schedule_next_ai_interaction()
            return
        
        # 启动AI工作线程
        self.ai_worker = AIInteractionWorker(language_config, self.ai_prompts)
        self.ai_worker.interaction_complete.connect(self._on_ai_interaction_complete)
        self.ai_worker.interaction_failed.connect(self._on_ai_interaction_failed)
        self.ai_worker.start()
        
        # 安排下一次互动
        self._schedule_next_ai_interaction()
    
    def _on_ai_interaction_complete(self, message: str, emoji: str):
        """AI互动完成回调"""
        if hasattr(self.desktop_pet, 'ai_state_manager'):
            self.desktop_pet.ai_state_manager.show_speech_bubble(message, emoji, 4000)
            logger.info(f"AI随机互动: {message}")
    
    def _on_ai_interaction_failed(self):
        """AI互动失败回调"""
        logger.debug("AI调用失败，使用预设对话")
        self._show_preset_interaction()
    
    def _show_preset_interaction(self):
        """显示预设互动对话"""
        message, emoji = random.choice(self.interaction_messages)
        if hasattr(self.desktop_pet, 'ai_state_manager'):
            self.desktop_pet.ai_state_manager.show_speech_bubble(message, emoji, 3000)
            logger.info(f"预设互动: {message}")
    
    def _is_ai_enabled(self) -> bool:
        """检查AI功能是否启用"""
        return self.desktop_pet.config.get("enable_ai_random_chat", True)
    
    def _is_language_model_configured(self, config: dict) -> bool:
        """检查语言模型是否已配置"""
        return (
            config.get("base_url") and 
            config.get("model_name") and
            config.get("base_url").strip() != "" and
            config.get("model_name").strip() != ""
        )
    
    def _start_focus(self):
        """开始专注功能"""
        logger.info("用户选择开始专注")
        if hasattr(self.desktop_pet, 'ai_state_manager'):
            # 切换到专注状态
            success = self.desktop_pet.ai_state_manager.switch_to_focus()
            if success:
                logger.info("成功切换到专注状态")
            else:
                logger.error("切换到专注状态失败")
                self.desktop_pet.show_speech_bubble("切换到专注模式失败", "confused.gif", 2000)
    
    def _quit_app(self):
        """退出应用"""
        from PySide6.QtWidgets import QApplication
        QApplication.quit()