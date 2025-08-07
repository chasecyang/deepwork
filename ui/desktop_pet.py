"""
桌宠主窗口模块（重构版）
负责桌宠的主要显示和交互功能
"""
import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer

from .settings import SettingsDialog
from .animated_emoji import AnimatedEmojiLabel
from .speech_bubble import SpeechBubble
from .states import AIStateManager
from .components.window_manager import WindowManager
from .components.drag_handler import DragHandler
from .components.animation_manager import AnimationManager
from .components.menu_manager import MenuManager

logger = logging.getLogger(__name__)


class DesktopPet(QWidget):
    """桌宠主窗口类（重构版）"""
    
    def __init__(self, config_manager, initial_ai_status=False):
        super().__init__()
        self.config = config_manager
        self.initial_ai_status = initial_ai_status
        
        # 初始化管理器
        self._init_managers()
        
        # 初始化界面和功能
        self._init_ui()
        self._init_speech_bubble()
        self._init_state_management()
        
    def _init_managers(self):
        """初始化各种管理器"""
        self.window_manager = WindowManager(self, self.config)
        self.drag_handler = DragHandler(self, self.window_manager)
        self.animation_manager = AnimationManager(self, self.config)
        self.menu_manager = MenuManager(
            self,
            on_settings_clicked=self._open_settings,
            on_quit_clicked=None,  # 使用默认退出行为
            on_focus_history_clicked=self._open_focus_history
        )
        
        # 设置对话框（延迟初始化）
        self.settings_dialog = None
        self.focus_history_dialog = None
        
    def _init_ui(self):
        """初始化用户界面"""
        # 初始化窗口属性
        self.window_manager.init_window_properties()
        self.window_manager.load_window_geometry()
        self.window_manager.update_transparency()
        
        # 创建布局和宠物标签
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.pet_label = AnimatedEmojiLabel()
        self.pet_label.set_animated_emoji("sleeping.gif")
        
        layout.addWidget(self.pet_label)
        self.setLayout(layout)
        
    def _init_speech_bubble(self):
        """初始化对话气泡"""
        self.speech_bubble = SpeechBubble(self)
        
    def _init_state_management(self):
        """初始化状态管理系统"""
        try:
            self.ai_state_manager = AIStateManager(self)
            
            # 连接状态管理器信号
            self.ai_state_manager.state_changed.connect(self._on_state_changed)
            self.ai_state_manager.state_entering.connect(self._on_state_entering)
            self.ai_state_manager.state_exited.connect(self._on_state_exited)
            
            # 启动时进入唤醒状态
            logger.info("应用启动，进入唤醒模式进行AI状态检查")
            self.ai_state_manager.switch_to_awakening()
                
        except Exception as e:
            logger.error(f"设置状态管理失败: {e}")
    
    # ============ 事件处理 ============
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        self.drag_handler.handle_mouse_press(event)
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        self.drag_handler.handle_mouse_move(event)
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        is_click = self.drag_handler.handle_mouse_release(event)
        
        if is_click:
            if self.ai_state_manager:
                self.ai_state_manager.handle_click()
            else:
                self.animation_manager.bounce_animation()
            
    def contextMenuEvent(self, event):
        """右键菜单事件"""
        if self.ai_state_manager:
            self.ai_state_manager.handle_right_click()
        else:
            self.menu_manager.show_menu()
            
    def enterEvent(self, event):
        """鼠标进入事件"""
        super().enterEvent(event)
        if self.ai_state_manager:
            self.ai_state_manager.handle_hover_enter()
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        if self.ai_state_manager:
            self.ai_state_manager.handle_hover_leave()
    
    # ============ 设置相关 ============
    
    def _open_settings(self):
        """打开设置对话框"""
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(
                self, 
                self.config, 
                self._on_settings_changed
            )
        
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
    
    def _open_focus_history(self):
        """打开专注历史对话框"""
        try:
            from .focus import FocusHistoryDialog
            
            if not self.focus_history_dialog:
                self.focus_history_dialog = FocusHistoryDialog(self)
            
            self.focus_history_dialog.show()
            self.focus_history_dialog.raise_()
            self.focus_history_dialog.activateWindow()
            
        except Exception as e:
            logger.error(f"打开专注历史对话框失败: {e}")
            self.show_speech_bubble("打开专注历史失败", "confused.gif", 2000)
        
    def _on_settings_changed(self):
        """设置更改后的回调"""
        # 更新窗口属性
        topmost = self.config.get("always_on_top", True)
        self.window_manager.update_topmost(topmost)
        self.window_manager.update_transparency()
        
        # 通知状态管理器
        if self.ai_state_manager:
            self.ai_state_manager.on_config_changed()
        
        # 重新显示窗口
        self.show()
        self.animation_manager.fade_in()
        
        # 重新检查AI配置
        self._schedule_ai_recheck()
    
    def _schedule_ai_recheck(self):
        """安排AI配置重新检查"""
        logger.info("设置已更改，重新进入唤醒状态检查AI配置")
        if self.ai_state_manager:
            self.recheck_timer = QTimer()
            self.recheck_timer.setSingleShot(True)
            self.recheck_timer.timeout.connect(self._trigger_ai_recheck)
            self.recheck_timer.start(500)
    
    def _trigger_ai_recheck(self):
        """触发AI配置重新检查"""
        logger.info("触发AI配置重新检查，切换到唤醒状态")
        if self.ai_state_manager:
            success = self.ai_state_manager.switch_to_awakening()
            if success:
                logger.info("成功切换到唤醒状态进行AI配置检查")
            else:
                logger.error("切换到唤醒状态失败")
    
    # ============ 状态管理回调 ============
    
    def _on_state_changed(self, old_state: str, new_state: str):
        """状态切换完成回调"""
        logger.info(f"状态切换完成: {old_state} -> {new_state}")
        if self.ai_state_manager:
            self.setToolTip(self.ai_state_manager.get_tooltip_text())
    
    def _on_state_entering(self, new_state: str):
        """即将进入新状态的回调"""
        logger.debug(f"即将进入状态: {new_state}")
    
    def _on_state_exited(self, old_state: str):
        """已退出状态的回调"""
        logger.debug(f"已退出状态: {old_state}")
    
    # ============ 公共接口 ============
    
    def show_context_menu(self):
        """显示右键菜单（供状态管理器调用）"""
        self.menu_manager.show_menu()
    
    def switch_to_normal_state(self):
        """切换到正常状态"""
        if self.ai_state_manager:
            return self.ai_state_manager.switch_to_normal()
        return False
    
    def switch_to_standby_state(self):
        """切换到待机状态"""
        if self.ai_state_manager:
            return self.ai_state_manager.switch_to_standby()
        return False
    
    def get_current_state(self) -> str:
        """获取当前状态名称"""
        if self.ai_state_manager:
            return self.ai_state_manager.get_current_state_name()
        return "unknown"
    
    def show_speech_bubble(self, text: str, emoji: str = None, duration: int = 3000):
        """显示对话气泡"""
        logger.info(f"显示对话气泡: text='{text}', emoji='{emoji}', duration={duration}")
        
        if not self.speech_bubble:
            logger.error("speech_bubble不存在")
            return
            
        # 切换表情
        if emoji and hasattr(self, 'pet_label'):
            self.pet_label.set_animated_emoji(emoji)
            
        # 显示气泡
        self.speech_bubble.show_bubble(text, duration, "top")
    
    def hide_speech_bubble(self):
        """隐藏对话气泡"""
        if self.speech_bubble:
            self.speech_bubble.hide_bubble()