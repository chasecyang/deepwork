"""
唤醒状态类
应用启动时的初始状态，负责检测AI配置并显示唤醒进度
"""
import logging
import asyncio
import sys
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QTabWidget
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QPalette, QColor
from .base_state import BaseState
from utils.ai_status_checker import ai_status_checker

logger = logging.getLogger(__name__)


class AICheckThread(QThread):
    """AI配置检测线程"""
    
    progress_updated = Signal(int, str)  # 进度百分比, 当前状态消息
    check_completed = Signal(bool, str)  # 检测结果, 详细消息
    
    def __init__(self, config):
        super().__init__()
        self.config = config
    
    def run(self):
        """运行AI配置检测"""
        try:
            # 设置事件循环策略
            if sys.platform == "win32":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 模拟检测过程，分步骤显示进度
                self.progress_updated.emit(10, "正在检查配置文件...")
                self.msleep(300)
                
                self.progress_updated.emit(30, "正在连接AI服务...")
                self.msleep(500)
                
                self.progress_updated.emit(50, "正在验证API密钥...")
                self.msleep(400)
                
                self.progress_updated.emit(70, "正在测试模型响应...")
                
                # 实际进行AI可用性检测
                ai_available, message = loop.run_until_complete(
                    ai_status_checker.check_ai_availability(self.config)
                )
                
                self.progress_updated.emit(90, "正在完成初始化...")
                self.msleep(300)
                
                self.msleep(200)
                
                self.check_completed.emit(ai_available, message)
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"AI配置检测失败: {e}")
            self.check_completed.emit(False, f"检测过程出错: {str(e)}")


class AwakeningUI(QWidget):
    """唤醒状态的UI组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 80)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # 状态标题
        self.title_label = QLabel("🌟 正在唤醒助手...")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPixelSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        
        # 状态信息
        self.status_label = QLabel("准备中...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_font = QFont()
        status_font.setPixelSize(10)
        self.status_label.setFont(status_font)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        # 设置样式
        self.setStyleSheet("""
            AwakeningUI {
                background-color: rgba(255, 255, 255, 240);
                border: 1px solid rgba(200, 200, 200, 150);
                border-radius: 10px;
            }
            QLabel {
                color: #333333;
                background: transparent;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4FC3F7, stop:1 #29B6F6);
                border-radius: 3px;
            }
        """)
    
    def update_progress(self, value: int, status: str):
        """更新进度"""
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
    
    def set_completed(self, success: bool):
        """设置完成状态"""
        if success:
            self.title_label.setText("✅ 助手已就绪!")
            self.status_label.setText("正在进入工作模式...")
        else:
            self.title_label.setText("💤 进入休眠模式")
            self.status_label.setText("请在设置中配置AI")


class AwakeningState(BaseState):
    """唤醒状态类"""
    
    def __init__(self, desktop_pet):
        """
        初始化唤醒状态
        
        Args:
            desktop_pet: 桌面宠物实例
        """
        super().__init__(desktop_pet, "唤醒模式")
        
        # UI组件
        self.awakening_ui: Optional[AwakeningUI] = None
        self.check_thread: Optional[AICheckThread] = None
        
        # 完成计时器
        self.completion_timer = QTimer()
        self.completion_timer.setSingleShot(True)
        self.completion_timer.timeout.connect(self._on_awakening_completed)
        
        # 检测结果
        self.ai_available = False
        self.check_message = ""
        
    def enter(self) -> None:
        """进入唤醒状态"""
        super().enter()
        logger.info("进入唤醒模式 - 开始AI配置检测流程")
        
        # 显示唤醒动画
        if hasattr(self.desktop_pet, 'pet_label'):
            self.desktop_pet.pet_label.set_animated_emoji("sleeping.gif")
            logger.info("✨ 已设置睡眠表情动画")
        
        # 创建并显示唤醒UI
        self._create_awakening_ui()
        logger.info("🎨 已创建唤醒UI界面")
        
        # 开始AI配置检测
        self._start_ai_check()
        logger.info("🔍 已开始AI配置检测")
        
    def exit(self) -> None:
        """退出唤醒状态"""
        super().exit()
        logger.info("退出唤醒模式")
        
        # 清理UI
        if self.awakening_ui:
            self.awakening_ui.hide()
            self.awakening_ui.deleteLater()
            self.awakening_ui = None
        
        # 停止检测线程
        if self.check_thread and self.check_thread.isRunning():
            self.check_thread.quit()
            self.check_thread.wait()
        
        # 停止计时器
        self.completion_timer.stop()
    
    def _create_awakening_ui(self):
        """创建唤醒UI"""
        self.awakening_ui = AwakeningUI()
        
        # 将UI定位到宠物下方
        pet_pos = self.desktop_pet.pos()
        pet_size = self.desktop_pet.size()
        ui_x = pet_pos.x() - (self.awakening_ui.width() - pet_size.width()) // 2
        ui_y = pet_pos.y() + pet_size.height() + 10
        
        self.awakening_ui.move(ui_x, ui_y)
        self.awakening_ui.show()
        
        # 设置窗口属性
        self.awakening_ui.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.awakening_ui.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def _start_ai_check(self):
        """开始AI配置检测"""
        if not hasattr(self.desktop_pet, 'config'):
            logger.error("无法获取配置管理器")
            self._on_check_completed(False, "配置管理器不可用")
            return
        
        # 创建检测线程
        self.check_thread = AICheckThread(self.desktop_pet.config.config)
        self.check_thread.progress_updated.connect(self._on_progress_updated)
        self.check_thread.check_completed.connect(self._on_check_completed)
        self.check_thread.start()
    
    def _on_progress_updated(self, progress: int, status: str):
        """进度更新回调"""
        if self.awakening_ui:
            self.awakening_ui.update_progress(progress, status)
            
        # 更新对话气泡内容
        if hasattr(self.desktop_pet, 'ai_state_manager'):
            speech_text = f"🔍 {status}"
            self.desktop_pet.ai_state_manager.show_speech_bubble(
                speech_text, "sleeping.gif", 2000
            )
    
    def _on_check_completed(self, ai_available: bool, message: str):
        """检测完成回调"""
        self.ai_available = ai_available
        self.check_message = message
        
        logger.info(f"AI配置检测完成: {ai_available}, {message}")
        
        if self.awakening_ui:
            self.awakening_ui.set_completed(ai_available)
        
        # 延迟一下再切换状态，让用户看到完成信息
        self.completion_timer.start(1500)
    
    def _on_awakening_completed(self):
        """唤醒完成，切换到相应状态"""
        if self.ai_available:
            # AI可用，切换到正常模式
            if hasattr(self.desktop_pet, 'ai_state_manager'):
                self.desktop_pet.ai_state_manager.switch_to_normal()
        else:
            # AI不可用，切换到待机模式并弹出配置页面
            if hasattr(self.desktop_pet, 'ai_state_manager'):
                self.desktop_pet.ai_state_manager.switch_to_standby()
            
            # 弹出AI配置页面
            self._show_ai_config_dialog()
    
    def handle_click(self) -> None:
        """处理点击事件（唤醒过程中禁用）"""
        logger.debug("唤醒过程中，点击被忽略")
        pass
    
    def handle_right_click(self) -> None:
        """处理右键点击事件（唤醒过程中允许设置菜单）"""
        if hasattr(self.desktop_pet, 'context_menu'):
            from PySide6.QtGui import QCursor
            self.desktop_pet.context_menu.exec(QCursor.pos())
    
    def handle_hover_enter(self) -> None:
        """处理鼠标悬停进入事件"""
        # 唤醒过程中不显示额外提示
        pass
    
    def handle_hover_leave(self) -> None:
        """处理鼠标悬停离开事件"""
        # 唤醒过程中不处理
        pass
    
    def get_tooltip_text(self) -> str:
        """获取工具提示文本"""
        return "🌟 正在唤醒助手，请稍候..."
    
    def _show_ai_config_dialog(self):
        """显示AI配置对话框"""
        try:
            logger.info("AI检查失败，弹出配置对话框")
            
            # 延迟弹出配置对话框，确保状态切换完成
            from PySide6.QtCore import QTimer
            config_timer = QTimer()
            config_timer.setSingleShot(True)
            config_timer.timeout.connect(self._open_settings_dialog)
            config_timer.start(500)  # 延迟500ms
            
        except Exception as e:
            logger.error(f"弹出配置对话框失败: {e}")
    
    def _open_settings_dialog(self):
        """打开设置对话框并切换到AI标签页"""
        try:
            if hasattr(self.desktop_pet, 'open_settings'):
                # 调用桌面宠物的设置方法
                self.desktop_pet.open_settings()
                
                # 如果设置对话框存在，切换到AI标签页
                if hasattr(self.desktop_pet, 'settings_dialog') and self.desktop_pet.settings_dialog:
                    # 获取标签页组件并切换到AI标签页
                    tab_widget = self.desktop_pet.settings_dialog.findChild(QTabWidget)
                    if tab_widget:
                        # AI标签页通常是第二个标签页（索引1）
                        tab_widget.setCurrentIndex(1)
                        logger.info("已切换到AI配置标签页")
                
            else:
                logger.warning("桌面宠物没有open_settings方法")
                
        except Exception as e:
            logger.error(f"打开设置对话框失败: {e}")
    
    def get_speech_text(self) -> str:
        """获取唤醒状态的对话文本"""
        return "🔍 检测AI能力中...\n请稍等片刻~"
    
    def get_speech_emoji(self) -> str:
        """获取唤醒状态的表情"""
        return "sleeping.gif"
    
    def should_show_speech_on_enter(self) -> bool:
        """唤醒状态进入时显示对话"""
        return True