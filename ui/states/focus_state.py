"""
专注状态类
管理专注模式下的所有逻辑，包括定时截图、AI分析、用户反馈等
"""
import logging
import asyncio
import os
import sys
from typing import Optional
from PySide6.QtCore import QTimer, QObject, Signal, QThread
from .base_state import BaseState
from ..focus import FocusConfigDialog
from utils.focus_data import FocusSessionManager, FocusSession, FocusAnalysisResult

logger = logging.getLogger(__name__)


class FocusAnalysisThread(QThread):
    """专注分析线程类"""
    
    analysis_completed = Signal(object)  # 分析结果信号
    analysis_failed = Signal(str)      # 分析失败信号
    
    def __init__(self, screenshot_path: str, focus_goal: str, config: dict):
        super().__init__()
        self.screenshot_path = screenshot_path
        self.focus_goal = focus_goal
        self.config = config
    
    def run(self):
        """运行专注分析"""
        try:
            # 设置事件循环策略
            if sys.platform == "win32":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 获取专注分析器
                from utils.focus_analyzer import get_focus_analyzer
                analyzer = get_focus_analyzer(self.config)
                
                # 执行分析
                result = loop.run_until_complete(
                    analyzer.analyze_focus(self.screenshot_path, self.focus_goal)
                )
                
                if result:
                    self.analysis_completed.emit(result)
                else:
                    self.analysis_failed.emit("专注分析返回空结果")
                    
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"专注分析失败: {e}")
            self.analysis_failed.emit(f"专注分析失败: {str(e)}")


class FocusState(BaseState):
    """专注状态类"""
    
    # 信号定义
    focus_completed = Signal()  # 专注完成信号
    focus_interrupted = Signal()  # 专注中断信号
    
    def __init__(self, desktop_pet):
        """
        初始化专注状态
        
        Args:
            desktop_pet: 桌面宠物实例
        """
        super().__init__(desktop_pet, "专注模式")
        
        # 专注会话管理
        self.session_manager = FocusSessionManager()
        self.current_session: Optional[FocusSession] = None
        
        # 定时器
        self.analysis_timer = QTimer()
        self.analysis_timer.timeout.connect(self._perform_analysis)
        
        # UI更新定时器
        self.ui_update_timer = QTimer()
        self.ui_update_timer.timeout.connect(self._update_ui)
        
        # 配置对话框
        self.config_dialog: Optional[FocusConfigDialog] = None
        
        # 分析状态
        self.is_analyzing = False
        self.last_analysis_result = None
        self.analysis_thread = None
        
        # 从配置获取分析间隔
        self.analysis_interval = self.desktop_pet.config.get("focus", {}).get("analysis_interval", 10) * 1000  # 转换为毫秒
        
        logger.info("专注状态初始化完成")
    
    def enter(self) -> None:
        """进入专注状态"""
        super().enter()
        logger.info("进入专注模式")
        
        # 如果没有活跃会话，显示配置对话框
        if not self.session_manager.is_session_active():
            self._show_config_dialog()
        else:
            # 恢复已有会话
            self.current_session = self.session_manager.get_current_session()
            self._start_focus_monitoring()
    
    def exit(self) -> None:
        """退出专注状态"""
        super().exit()
        logger.info("退出专注模式")
        
        # 停止所有定时器
        self.analysis_timer.stop()
        self.ui_update_timer.stop()
        
        # 停止分析线程
        if self.analysis_thread and self.analysis_thread.isRunning():
            self.analysis_thread.quit()
            self.analysis_thread.wait(5000)  # 等待最多5秒
            self.analysis_thread = None
        
        # 如果有活跃会话，暂停它
        if self.session_manager.is_session_active():
            self.session_manager.pause_current_session()
    
    def _show_config_dialog(self):
        """显示专注配置对话框"""
        if not self.config_dialog:
            self.config_dialog = FocusConfigDialog(self.desktop_pet)
            self.config_dialog.focus_started.connect(self._on_focus_started)
            self.config_dialog.focus_cancelled.connect(self._on_focus_cancelled)
        
        self.config_dialog.show()
        self.config_dialog.raise_()
        self.config_dialog.activateWindow()
    
    def _on_focus_started(self, goal: str, duration: int):
        """处理开始专注的信号"""
        logger.info(f"开始专注会话: {goal}, 时长: {duration}分钟")
        
        # 创建新的专注会话
        self.current_session = self.session_manager.start_session(goal, duration)
        
        # 开始监控
        self._start_focus_monitoring()
        
        # 显示开始提示
        self.desktop_pet.show_speech_bubble(
            f"🎯 开始专注：{goal}\n⏰ 目标时长：{duration}分钟",
            "rocket.gif",
            4000
        )
    
    def _on_focus_cancelled(self):
        """处理取消专注的信号"""
        logger.info("用户取消专注")
        
        # 切换回正常状态
        if hasattr(self.desktop_pet, 'ai_state_manager'):
            self.desktop_pet.ai_state_manager.switch_to_normal()
    
    def _start_focus_monitoring(self):
        """开始专注监控"""
        if not self.current_session:
            logger.error("没有活跃的专注会话")
            return
        
        logger.info("开始专注监控")
        
        # 设置专注表情
        if hasattr(self.desktop_pet, 'pet_label'):
            self.desktop_pet.pet_label.set_animated_emoji("fire.gif")
        
        # 启动分析定时器
        self.analysis_timer.start(self.analysis_interval)
        
        # 启动UI更新定时器（每秒更新一次）
        self.ui_update_timer.start(1000)
        
        # 更新窗口标题
        self.desktop_pet.setWindowTitle(f"桌面助手 - 专注中: {self.current_session.goal}")
    
    def _perform_analysis(self):
        """执行专注分析"""
        if self.is_analyzing:
            logger.debug("上一次分析尚未完成，跳过本次分析")
            return
        
        if not self.current_session or not self.current_session.is_active:
            logger.warning("没有活跃的专注会话，停止分析")
            self.analysis_timer.stop()
            return
        
        # 检查是否已完成
        if self.current_session.is_completed():
            self._complete_focus_session()
            return
        
        logger.debug("开始执行专注分析")
        self.is_analyzing = True
        
        # 使用线程执行分析（避免阻塞UI）
        self._start_analysis_thread()
    
    def _start_analysis_thread(self):
        """启动分析线程"""
        try:
            # 获取截图管理器
            from utils.screenshot_manager import get_screenshot_manager
            screenshot_manager = get_screenshot_manager(self.desktop_pet.config.get("focus", {}))
            
            # 截图
            screenshot_path = screenshot_manager.take_screenshot()
            if not screenshot_path:
                logger.error("截图失败")
                self.is_analyzing = False
                return
            
            # 准备配置
            focus_config = self.desktop_pet.config.get("focus", {}).copy()
            # 添加AI模型配置
            focus_config["vision_model"] = self.desktop_pet.config.get("vision_model", {})
            focus_config["language_model"] = self.desktop_pet.config.get("language_model", {})
            
            # 创建并启动分析线程
            self.analysis_thread = FocusAnalysisThread(
                screenshot_path, 
                self.current_session.goal, 
                focus_config
            )
            self.analysis_thread.analysis_completed.connect(self._on_analysis_completed)
            self.analysis_thread.analysis_failed.connect(self._on_analysis_failed)
            self.analysis_thread.finished.connect(self._on_analysis_thread_finished)
            self.analysis_thread.start()
            
        except Exception as e:
            logger.error(f"启动专注分析线程失败: {e}")
            self.is_analyzing = False
    
    def _on_analysis_completed(self, result):
        """处理分析完成"""
        try:
            # 添加到会话
            self.current_session.add_analysis_result(result)
            self.last_analysis_result = result
            
            # 更新表情和反馈
            self._update_feedback(result)
            
            # 清理截图文件（除非配置保留）
            if not self.desktop_pet.config.get("focus", {}).get("save_screenshots", False):
                from utils.screenshot_manager import get_screenshot_manager
                screenshot_manager = get_screenshot_manager(self.desktop_pet.config.get("focus", {}))
                screenshot_manager.delete_screenshot(result.screenshot_path)
                
        except Exception as e:
            logger.error(f"处理分析结果失败: {e}")
            import traceback
            logger.error(f"错误详情: {traceback.format_exc()}")
    
    def _on_analysis_failed(self, error_message):
        """处理分析失败"""
        logger.error(f"专注分析失败: {error_message}")
        
        # 清理可能存在的截图文件
        if self.analysis_thread and hasattr(self.analysis_thread, 'screenshot_path'):
            try:
                from utils.screenshot_manager import get_screenshot_manager
                screenshot_manager = get_screenshot_manager(self.desktop_pet.config.get("focus", {}))
                screenshot_manager.delete_screenshot(self.analysis_thread.screenshot_path)
            except Exception as e:
                logger.error(f"清理截图文件失败: {e}")
    
    def _on_analysis_thread_finished(self):
        """分析线程完成"""
        self.is_analyzing = False
        self.analysis_thread = None
    
    def _update_feedback(self, result: FocusAnalysisResult):
        """根据分析结果更新反馈"""
        # 更新表情
        if hasattr(self.desktop_pet, 'pet_label'):
            self.desktop_pet.pet_label.set_animated_emoji(result.recommended_emoji)
        
        self.desktop_pet.show_speech_bubble(
            result.feedback_message,
            result.recommended_emoji,
            5000  # 延长到5秒
        )
    
    def _update_ui(self):
        """更新UI显示"""
        if not self.current_session:
            return
        
        # 更新工具提示
        remaining_time = self.current_session.get_remaining_time()
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        
        tooltip = f"专注中: {self.current_session.goal}\n剩余时间: {minutes:02d}:{seconds:02d}"
        self.desktop_pet.setToolTip(tooltip)
        
        # 检查是否完成
        if self.current_session.is_completed():
            self._complete_focus_session()
    
    def _complete_focus_session(self):
        """完成专注会话"""
        logger.info("专注会话完成")
        
        # 停止定时器
        self.analysis_timer.stop()
        self.ui_update_timer.stop()
        
        # 完成会话
        if self.current_session:
            self.session_manager.end_current_session()
            summary = self.current_session.get_summary()
            
            # 显示完成庆祝
            self.desktop_pet.show_speech_bubble(
                f"🎉 专注完成！\n⏰ 专注时长: {summary['actual_duration']:.1f}分钟",
                "party.gif",
                5000
            )
            
            # 发出完成信号
            self.focus_completed.emit()
        
        # 延迟后切换回正常状态
        from PySide6.QtCore import QTimer
        switch_timer = QTimer()
        switch_timer.setSingleShot(True)
        switch_timer.timeout.connect(self._switch_to_normal)
        switch_timer.start(6000)  # 6秒后切换
    
    def _switch_to_normal(self):
        """切换到正常状态"""
        if hasattr(self.desktop_pet, 'ai_state_manager'):
            self.desktop_pet.ai_state_manager.switch_to_normal()
    
    def on_click(self) -> None:
        """处理点击事件"""
        # 专注模式下点击显示当前状态
        if self.current_session:
            remaining_time = self.current_session.get_remaining_time()
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            
            message = f"🎯 专注目标: {self.current_session.goal}\n⏰ 剩余: {minutes:02d}:{seconds:02d}"
            
            self.desktop_pet.show_speech_bubble(message, "thinking.gif", 3000)
    
    def on_right_click(self) -> None:
        """处理右键点击事件"""
        # 专注模式下的特殊右键菜单
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction, QCursor
        from ..theme import ModernTheme
        
        menu = QMenu(self.desktop_pet)
        menu.setStyleSheet(ModernTheme.get_menu_style())
        
        if self.current_session and self.current_session.is_active:
            # 暂停/恢复
            if self.current_session.is_paused:
                resume_action = QAction("继续专注", self.desktop_pet)
                resume_action.triggered.connect(self._resume_focus)
                menu.addAction(resume_action)
            else:
                pause_action = QAction("暂停专注", self.desktop_pet)
                pause_action.triggered.connect(self._pause_focus)
                menu.addAction(pause_action)
            
            # 结束专注
            stop_action = QAction("结束专注", self.desktop_pet)
            stop_action.triggered.connect(self._stop_focus)
            menu.addAction(stop_action)
            
            menu.addSeparator()
        
        # 设置
        settings_action = QAction("设置", self.desktop_pet)
        settings_action.triggered.connect(self.desktop_pet.show_settings)
        menu.addAction(settings_action)
        
        menu.exec(QCursor.pos())
    
    def _pause_focus(self):
        """暂停专注"""
        if self.current_session:
            self.session_manager.pause_current_session()
            self.analysis_timer.stop()
            
            if hasattr(self.desktop_pet, 'pet_label'):
                self.desktop_pet.pet_label.set_animated_emoji("sleeping.gif")
            
            self.desktop_pet.show_speech_bubble("⏸️ 专注已暂停", "sleeping.gif", 2000)
            logger.info("专注已暂停")
    
    def _resume_focus(self):
        """恢复专注"""
        if self.current_session:
            self.session_manager.resume_current_session()
            self.analysis_timer.start(self.analysis_interval)
            
            if hasattr(self.desktop_pet, 'pet_label'):
                self.desktop_pet.pet_label.set_animated_emoji("fire.gif")
            
            self.desktop_pet.show_speech_bubble("▶️ 继续专注！", "fire.gif", 2000)
            logger.info("专注已恢复")
    
    def _stop_focus(self):
        """停止专注"""
        if self.current_session:
            # 显示确认对话框
            from PySide6.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self.desktop_pet,
                "确认结束",
                f"确定要结束当前专注吗？\n\n目标: {self.current_session.goal}\n已专注: {self.current_session.get_elapsed_time()/60:.1f}分钟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._complete_focus_session()
                self.focus_interrupted.emit()
                logger.info("用户手动结束专注")
    
    def get_tooltip_text(self) -> str:
        """获取工具提示文本"""
        if self.current_session:
            remaining_time = self.current_session.get_remaining_time()
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            
            status = "暂停中" if self.current_session.is_paused else "专注中"
            return f"{status}: {self.current_session.goal} - 剩余 {minutes:02d}:{seconds:02d}"
        else:
            return "准备开始专注..."
    
    def get_speech_text(self) -> str:
        """获取专注状态的对话文本"""
        return "🎯 进入专注模式！\n让我们一起专注于目标吧~"
    
    def get_speech_emoji(self) -> str:
        """获取专注状态的表情"""
        return "rocket.gif"
    
    def should_show_speech_on_enter(self) -> bool:
        """专注状态进入时不自动显示对话（由配置对话框处理）"""
        return False