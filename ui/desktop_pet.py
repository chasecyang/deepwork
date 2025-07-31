"""
桌宠主窗口模块
负责桌宠的主要显示和交互功能 - PySide6版本
"""
import os
import random
import logging
from PySide6.QtWidgets import (QWidget, QLabel, QMenu, QVBoxLayout, 
                               QApplication)
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QAction, QCursor
from .settings import SettingsDialog
from .animated_emoji import AnimatedEmojiLabel
from .speech_bubble import SpeechBubble
from .theme import ModernTheme
from .states import AIStateManager

logger = logging.getLogger(__name__)


class DesktopPet(QWidget):
    """桌宠主窗口类"""
    
    def __init__(self, config_manager, initial_ai_status=False):
        super().__init__()
        self.config = config_manager
        self.settings_dialog = None
        
        # 拖拽相关变量
        self.drag_start_position = QPoint()
        self.is_dragging = False
        
        # 动画相关
        self.opacity_animation = None
        self.move_animation = None
        
        # 初始化状态管理器
        self.ai_state_manager = None
        self.initial_ai_status = initial_ai_status
        
        # 对话气泡
        self.speech_bubble = None
        
        self.init_window()
        self.create_widgets()
        self.create_speech_bubble()
        self.setup_context_menu()
        self.setup_state_management()
        
    def init_window(self):
        """初始化窗口"""
        # 设置窗口标志：无边框、置顶
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Window
        )
        
        # 设置窗口属性，确保不会自动隐藏
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        
        # 设置窗口大小和位置
        width = self.config.get("window_width", 100)
        height = self.config.get("window_height", 100)
        x = self.config.get("window_x", 100)
        y = self.config.get("window_y", 100)
        
        self.setGeometry(x, y, width, height)
        
        # 设置透明度
        self.setWindowOpacity(self.config.get("transparency", 0.9))
        
        # 设置窗口标题
        self.setWindowTitle("桌面助手")
        
        # 设置样式表
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        
    def create_widgets(self):
        """创建窗口内容"""
        # 创建布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建支持动画的宠物标签
        self.pet_label = AnimatedEmojiLabel()
        
        # 直接显示睡眠表情，避免中间状态的表情切换
        self.pet_label.set_animated_emoji("sleeping.gif")
        
        layout.addWidget(self.pet_label)
        self.setLayout(layout)
        
    def create_speech_bubble(self):
        """创建对话气泡"""
        self.speech_bubble = SpeechBubble(self)
        
    def setup_context_menu(self):
        """设置右键菜单"""
        self.context_menu = QMenu(self)
        
        # 应用现代化菜单样式
        self.context_menu.setStyleSheet(ModernTheme.get_menu_style())
        
        # 创建菜单动作
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings)
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_app)
        
        # 添加动作到菜单
        self.context_menu.addAction(settings_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(quit_action)
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 开始拖拽
            self.is_dragging = True
            self.drag_start_position = event.globalPosition().toPoint() - self.pos()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            # 拖拽窗口
            new_pos = event.globalPosition().toPoint() - self.drag_start_position
            self.move(new_pos)
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            # 保存当前位置
            self.config.set("window_x", self.x())
            self.config.set("window_y", self.y())
            
            # 如果是简单点击（没有拖拽），通过状态管理器处理点击
            if self.drag_start_position == event.globalPosition().toPoint() - self.pos():
                if self.ai_state_manager:
                    self.ai_state_manager.handle_click()
                else:
                    # 回退到默认行为
                    self.bounce_animation()
            
    def contextMenuEvent(self, event):
        """右键菜单事件"""
        if self.ai_state_manager:
            self.ai_state_manager.handle_right_click()
        else:
            # 回退到默认行为
            self.context_menu.exec(QCursor.pos())
            
    def show_settings(self):
        """显示设置对话框"""
        self.open_settings()
        
    def open_settings(self):
        """打开设置对话框（公共方法，供状态调用）"""
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(
                self, 
                self.config, 
                self.on_settings_changed
            )
        
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
        
    def on_settings_changed(self):
        """设置更改后的回调"""
        # 更新窗口属性
        topmost = self.config.get("always_on_top", True)
        base_flags = (
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Window
        )
        
        if topmost:
            self.setWindowFlags(base_flags | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(base_flags)
        
        # 重新设置窗口属性
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        
        # 更新透明度
        self.setWindowOpacity(self.config.get("transparency", 0.9))
        
        # 通知状态管理器配置已更改
        if self.ai_state_manager:
            self.ai_state_manager.on_config_changed()
        
        # 显示窗口（设置标志后需要重新显示）
        self.show()
        # 应用淡入动画
        self.fade_in()
        
        # 重新检查AI配置：设置更改后重新进入唤醒状态进行完整的AI配置检查
        logger.info("设置已更改，重新进入唤醒状态检查AI配置")
        if self.ai_state_manager:
            # 延迟一下再切换状态，确保设置对话框已经关闭
            from PySide6.QtCore import QTimer
            # 使用实例变量避免定时器被垃圾回收
            self.recheck_timer = QTimer()
            self.recheck_timer.setSingleShot(True)
            self.recheck_timer.timeout.connect(self._trigger_ai_recheck)
            self.recheck_timer.start(500)  # 延迟500ms
    
    def _trigger_ai_recheck(self):
        """触发AI配置重新检查"""
        logger.info("触发AI配置重新检查，切换到唤醒状态")
        if self.ai_state_manager:
            success = self.ai_state_manager.switch_to_awakening()
            if success:
                logger.info("成功切换到唤醒状态进行AI配置检查")
            else:
                logger.error("切换到唤醒状态失败")
    
    def fade_in(self):
        """淡入动画"""
        if not self.config.get("enable_animations", True):
            return
            
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(self.config.get("animation_speed", 200))
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(self.config.get("transparency", 0.9))
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.opacity_animation.start()
    
    def fade_out(self):
        """淡出动画"""
        if not self.config.get("enable_animations", True):
            self.hide()
            return
            
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(self.config.get("animation_speed", 200))
        self.opacity_animation.setStartValue(self.windowOpacity())
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.opacity_animation.finished.connect(self.hide)
        self.opacity_animation.start()
    
    def bounce_animation(self):
        """弹跳动画效果"""
        if not self.config.get("enable_animations", True):
            return
            
        current_pos = self.pos()
        bounce_height = 20
        
        self.move_animation = QPropertyAnimation(self, b"pos")
        self.move_animation.setDuration(self.config.get("animation_speed", 200))
        self.move_animation.setStartValue(current_pos)
        self.move_animation.setEndValue(QPoint(current_pos.x(), current_pos.y() - bounce_height))
        self.move_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        # 反弹回来
        def bounce_back():
            back_animation = QPropertyAnimation(self, b"pos")
            back_animation.setDuration(self.config.get("animation_speed", 200))
            back_animation.setStartValue(QPoint(current_pos.x(), current_pos.y() - bounce_height))
            back_animation.setEndValue(current_pos)
            back_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
            back_animation.start()
        
        self.move_animation.finished.connect(bounce_back)
        self.move_animation.start()
        
    def quit_app(self):
        """退出应用"""
        QApplication.quit()
    
    def setup_state_management(self):
        """设置状态管理系统"""
        try:
            # 创建状态管理器
            self.ai_state_manager = AIStateManager(self)
            
            # 连接状态管理器的信号
            self.ai_state_manager.state_changed.connect(self.on_state_changed)
            self.ai_state_manager.state_entering.connect(self.on_state_entering)
            self.ai_state_manager.state_exited.connect(self.on_state_exited)
            
            # 应用启动时先进入唤醒状态进行AI检查
            # 检查通过后切换到正常状态，检查失败则切换到待机状态
            logger.info("应用启动，进入唤醒模式进行AI状态检查")
            self.ai_state_manager.switch_to_awakening()
                
        except Exception as e:
            logger.error(f"设置状态管理失败: {e}")
            # 如果状态管理设置失败，记录错误但不影响基本功能
    
    def on_state_changed(self, old_state: str, new_state: str):
        """状态切换完成回调"""
        logger.info(f"状态切换完成: {old_state} -> {new_state}")
        
        # 可以在这里添加状态切换后的额外处理
        if new_state == "唤醒模式":
            # 切换到唤醒模式时的处理
            self.setToolTip(self.ai_state_manager.get_tooltip_text())
        elif new_state == "正常模式":
            # 切换到正常模式时的处理
            self.setToolTip(self.ai_state_manager.get_tooltip_text())
        elif new_state == "待机模式":
            # 切换到待机模式时的处理
            self.setToolTip(self.ai_state_manager.get_tooltip_text())
    
    def on_state_entering(self, new_state: str):
        """即将进入新状态的回调"""
        logger.debug(f"即将进入状态: {new_state}")
    
    def on_state_exited(self, old_state: str):
        """已退出状态的回调"""
        logger.debug(f"已退出状态: {old_state}")
    
# 注释：移除了on_ai_config_success方法，因为现在改为设置关闭后重新进入唤醒状态检查配置
    
    def show_context_menu(self):
        """显示右键菜单（供状态管理器调用）"""
        self.context_menu.exec(QCursor.pos())
    
    def switch_to_normal_state(self):
        """切换到正常状态（供外部调用）"""
        if self.ai_state_manager:
            return self.ai_state_manager.switch_to_normal()
        return False
    
    def switch_to_standby_state(self):
        """切换到待机状态（供外部调用）"""
        if self.ai_state_manager:
            return self.ai_state_manager.switch_to_standby()
        return False
    
    def get_current_state(self) -> str:
        """获取当前状态名称"""
        if self.ai_state_manager:
            return self.ai_state_manager.get_current_state_name()
        return "unknown"
    
    def show_speech_bubble(self, text: str, emoji: str = None, duration: int = 3000):
        """
        显示对话气泡
        
        Args:
            text: 对话文本
            emoji: 配套表情（可选）
            duration: 显示时长（毫秒）
        """
        logger.info(f"show_speech_bubble调用: text='{text}', emoji='{emoji}', duration={duration}")
        
        if not self.speech_bubble:
            logger.error("speech_bubble不存在，无法显示气泡")
            return
            
        logger.info(f"speech_bubble状态: exists={self.speech_bubble is not None}, visible={self.speech_bubble.isVisible()}")
        
        # 如果指定了表情，先切换表情
        if emoji and hasattr(self, 'pet_label'):
            self.pet_label.set_animated_emoji(emoji)
            
        # 显示气泡
        logger.info(f"准备调用show_bubble: '{text}'")
        self.speech_bubble.show_bubble(text, duration, "top")
        logger.info(f"show_bubble完成，气泡现在visible: {self.speech_bubble.isVisible()}, size: {self.speech_bubble.size()}")
    
    def hide_speech_bubble(self):
        """隐藏对话气泡"""
        if self.speech_bubble:
            self.speech_bubble.hide_bubble()
    
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