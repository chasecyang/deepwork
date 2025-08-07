"""
AI服务自动检测标签页
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QGroupBox, QComboBox, QMessageBox, 
                               QProgressBar, QTextEdit, QScrollArea)
from PySide6.QtCore import Qt, QThread, Signal
from ui.theme import ModernTheme
from utils.service_detector import service_detector, ServiceInfo
import asyncio


class ServiceDetectionThread(QThread):
    """服务检测线程"""
    detection_finished = Signal(list)  # 检测完成信号
    
    def run(self):
        """运行服务检测"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            services = loop.run_until_complete(service_detector.detect_services())
            self.detection_finished.emit(services)
        except Exception as e:
            print(f"服务检测出错: {e}")
            self.detection_finished.emit([])
        finally:
            loop.close()


class AIAutoDetectionTab(QWidget):
    """AI服务自动检测标签页"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.detected_services = []
        self.detection_thread = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 创建主布局（用于放置滚动区域）
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # 创建滚动内容容器
        scroll_content = QWidget()
        scroll_content.setMinimumHeight(600)  # 设置最小高度，确保内容不会过度压缩
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        # 顶部说明区域
        info_group = self._create_info_group()
        content_layout.addWidget(info_group)
        
        # 服务检测控制区域
        detection_group = self._create_detection_group()
        content_layout.addWidget(detection_group)
        
        # 检测结果展示区域
        results_group = self._create_results_group()
        content_layout.addWidget(results_group)
        
        # 添加弹性空间
        content_layout.addStretch()
        
        # 设置滚动区域的内容
        scroll_area.setWidget(scroll_content)
        
        # 启用平滑滚动
        scroll_area.verticalScrollBar().setSingleStep(20)
        scroll_area.verticalScrollBar().setPageStep(100)
        
        main_layout.addWidget(scroll_area)
    
    def _create_info_group(self) -> QGroupBox:
        """创建信息说明组"""
        info_group = QGroupBox("🔍 自动检测AI服务")
        info_layout = QVBoxLayout(info_group)
        info_layout.setSpacing(10)
        info_layout.setContentsMargins(15, 20, 15, 15)
        
        # 主要说明
        main_info = QLabel("自动检测本地运行的AI服务，如Ollama、Lemonade等")
        main_info.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
        info_layout.addWidget(main_info)
        
        # 详细说明
        detail_info = QLabel(
            "• 支持检测常见的本地AI服务\n"
            "• 自动获取可用模型列表\n"
            "• 一键应用最佳配置\n"
            "• 无需手动输入复杂的API参数"
        )
        detail_info.setStyleSheet("color: #666; font-size: 12px; line-height: 1.4;")
        detail_info.setWordWrap(True)
        info_layout.addWidget(detail_info)
        
        return info_group
    
    def _create_detection_group(self) -> QGroupBox:
        """创建检测控制组"""
        detection_group = QGroupBox("检测控制")
        detection_layout = QVBoxLayout(detection_group)
        detection_layout.setSpacing(15)
        detection_layout.setContentsMargins(15, 20, 15, 15)
        
        # 控制按钮区域
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        
        # 检测按钮
        self.detect_button = QPushButton("🚀 开始检测")
        self.detect_button.setMinimumHeight(40)
        self.detect_button.setMinimumWidth(140)
        self.detect_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.COLORS['primary_hover']};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
        """)
        self.detect_button.clicked.connect(self._start_service_detection)
        control_layout.addWidget(self.detect_button)
        
        # 刷新按钮
        self.refresh_button = QPushButton("🔄 重新检测")
        self.refresh_button.setMinimumHeight(40)
        self.refresh_button.setMinimumWidth(120)
        self.refresh_button.setEnabled(False)
        self.refresh_button.clicked.connect(self._start_service_detection)
        control_layout.addWidget(self.refresh_button)
        
        control_layout.addStretch()
        detection_layout.addLayout(control_layout)
        
        # 检测状态栏
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)
        
        self.detection_progress = QProgressBar()
        self.detection_progress.setVisible(False)
        self.detection_progress.setMaximum(0)  # 无限进度条
        self.detection_progress.setMinimumHeight(6)
        self.detection_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: #f5f5f5;
            }}
            QProgressBar::chunk {{
                background-color: {ModernTheme.COLORS['primary']};
                border-radius: 2px;
            }}
        """)
        status_layout.addWidget(self.detection_progress)
        
        self.detection_status_label = QLabel("点击'开始检测'来查找可用的AI服务")
        self.detection_status_label.setStyleSheet("color: #666; font-size: 12px;")
        self.detection_status_label.setWordWrap(True)
        status_layout.addWidget(self.detection_status_label)
        
        status_layout.addStretch()
        detection_layout.addLayout(status_layout)
        
        return detection_group
    
    def _create_results_group(self) -> QGroupBox:
        """创建检测结果组"""
        results_group = QGroupBox("检测结果")
        results_layout = QVBoxLayout(results_group)
        results_layout.setSpacing(15)
        results_layout.setContentsMargins(15, 20, 15, 15)
        
        # 服务选择区域
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(12)
        
        service_label = QLabel("检测到的服务:")
        service_label.setMinimumWidth(100)
        service_label.setStyleSheet("font-weight: bold; color: #333;")
        selection_layout.addWidget(service_label)
        
        self.service_combo = QComboBox()
        self.service_combo.setMinimumHeight(36)
        self.service_combo.setMinimumWidth(300)
        self.service_combo.addItem("请先进行服务检测")
        self.service_combo.setEnabled(False)
        self.service_combo.currentIndexChanged.connect(self._on_service_selection_changed)
        selection_layout.addWidget(self.service_combo)
        
        # 应用配置按钮
        self.apply_service_button = QPushButton("⚡ 应用此配置")
        self.apply_service_button.setMinimumHeight(36)
        self.apply_service_button.setMinimumWidth(130)
        self.apply_service_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.COLORS['success']};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
        """)
        self.apply_service_button.clicked.connect(self._apply_service_config)
        self.apply_service_button.setEnabled(False)
        selection_layout.addWidget(self.apply_service_button)
        
        selection_layout.addStretch()
        results_layout.addLayout(selection_layout)
        
        # 模型选择区域
        self.model_selection_group = QGroupBox("模型选择")
        model_selection_layout = QVBoxLayout(self.model_selection_group)
        model_selection_layout.setSpacing(12)
        model_selection_layout.setContentsMargins(15, 15, 15, 15)
        
        # 视觉模型选择
        vision_model_layout = QHBoxLayout()
        vision_model_label = QLabel("视觉模型:")
        vision_model_label.setMinimumWidth(80)
        vision_model_label.setStyleSheet("font-weight: bold; color: #333;")
        self.vision_model_combo = QComboBox()
        self.vision_model_combo.setMinimumHeight(32)
        self.vision_model_combo.setEnabled(False)
        vision_model_layout.addWidget(vision_model_label)
        vision_model_layout.addWidget(self.vision_model_combo)
        vision_model_layout.addStretch()
        model_selection_layout.addLayout(vision_model_layout)
        
        # 语言模型选择
        language_model_layout = QHBoxLayout()
        language_model_label = QLabel("语言模型:")
        language_model_label.setMinimumWidth(80)
        language_model_label.setStyleSheet("font-weight: bold; color: #333;")
        self.language_model_combo = QComboBox()
        self.language_model_combo.setMinimumHeight(32)
        self.language_model_combo.setEnabled(False)
        language_model_layout.addWidget(language_model_label)
        language_model_layout.addWidget(self.language_model_combo)
        language_model_layout.addStretch()
        model_selection_layout.addLayout(language_model_layout)
        
        # 默认隐藏模型选择组
        self.model_selection_group.setVisible(False)
        results_layout.addWidget(self.model_selection_group)
        
        # 服务详情展示区域
        self.service_details = QTextEdit()
        self.service_details.setMaximumHeight(120)
        self.service_details.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                color: #495057;
            }
        """)
        self.service_details.setPlainText("选择一个服务查看详细信息...")
        self.service_details.setReadOnly(True)
        results_layout.addWidget(self.service_details)
        
        return results_group
    
    def _start_service_detection(self):
        """开始服务检测"""
        self.detect_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        self.detection_progress.setVisible(True)
        self.detection_status_label.setText("正在扫描本地AI服务...")
        self.detection_status_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        
        # 清空服务列表和模型选择
        self.service_combo.clear()
        self.service_combo.addItem("检测中，请稍候...")
        self.service_combo.setEnabled(False)
        self.apply_service_button.setEnabled(False)
        self.service_details.setPlainText("检测中...")
        self.model_selection_group.setVisible(False)
        self.vision_model_combo.clear()
        self.language_model_combo.clear()
        
        # 启动检测线程
        self.detection_thread = ServiceDetectionThread()
        self.detection_thread.detection_finished.connect(self._on_detection_finished)
        self.detection_thread.start()
    
    def _on_detection_finished(self, services):
        """服务检测完成回调"""
        self.detection_progress.setVisible(False)
        self.detect_button.setEnabled(True)
        self.refresh_button.setEnabled(True)
        self.detected_services = services
        
        # 更新UI
        self.service_combo.clear()
        
        if services:
            # 有检测到的服务
            self.detection_status_label.setText(f"✅ 成功检测到 {len(services)} 个可用AI服务")
            self.detection_status_label.setStyleSheet(f"color: {ModernTheme.COLORS['success']}; font-weight: bold;")
            
            for service in services:
                display_text = f"{service.display_name}"
                self.service_combo.addItem(display_text, service)
            
            self.service_combo.setEnabled(True)
            self.apply_service_button.setEnabled(True)
            
            # 自动选择第一个服务并显示详情
            if self.service_combo.count() > 0:
                self._on_service_selection_changed(0)
        else:
            # 没有检测到服务
            self.detection_status_label.setText("❌ 未检测到可用的AI服务")
            self.detection_status_label.setStyleSheet(f"color: {ModernTheme.COLORS['error']}; font-weight: bold;")
            self.service_combo.addItem("未检测到任何服务")
            self.service_combo.setEnabled(False)
            self.apply_service_button.setEnabled(False)
            self.service_details.setPlainText(
                "未检测到AI服务。\n\n"
                "可能的原因：\n"
                "• Ollama或其他AI服务未启动\n"
                "• 服务运行在非标准端口\n"
                "• 防火墙阻止了连接\n\n"
                "请确保AI服务正在运行，然后重新检测。"
            )
    
    def _on_service_selection_changed(self, index):
        """服务选择改变时的回调"""
        if index < 0 or not self.detected_services:
            self.model_selection_group.setVisible(False)
            return
        
        try:
            selected_service = self.service_combo.currentData()
            if not selected_service:
                self.model_selection_group.setVisible(False)
                return
            
            # 获取可用模型分类
            models_info = service_detector.get_available_models_for_service(selected_service)
            
            # 填充视觉模型下拉框
            self.vision_model_combo.clear()
            vision_models = models_info.get("vision_models", [])
            if vision_models:
                for model in vision_models:
                    self.vision_model_combo.addItem(model)
                # 设置默认选择
                default_vision = selected_service.default_models.get("vision_model", "")
                if default_vision and default_vision in vision_models:
                    self.vision_model_combo.setCurrentText(default_vision)
            else:
                # 如果没有专门的视觉模型，显示所有模型
                all_models = models_info.get("all_models", [])
                for model in all_models:
                    self.vision_model_combo.addItem(model)
                if all_models:
                    default_vision = selected_service.default_models.get("vision_model", "")
                    if default_vision and default_vision in all_models:
                        self.vision_model_combo.setCurrentText(default_vision)
            
            # 填充语言模型下拉框
            self.language_model_combo.clear()
            language_models = models_info.get("language_models", [])
            if language_models:
                for model in language_models:
                    self.language_model_combo.addItem(model)
                # 设置默认选择
                default_language = selected_service.default_models.get("language_model", "")
                if default_language and default_language in language_models:
                    self.language_model_combo.setCurrentText(default_language)
            else:
                # 如果没有专门的语言模型，显示所有模型
                all_models = models_info.get("all_models", [])
                for model in all_models:
                    self.language_model_combo.addItem(model)
                if all_models:
                    default_language = selected_service.default_models.get("language_model", "")
                    if default_language and default_language in all_models:
                        self.language_model_combo.setCurrentText(default_language)
            
            # 启用模型选择并显示
            has_models = bool(models_info.get("all_models", []))
            self.vision_model_combo.setEnabled(has_models)
            self.language_model_combo.setEnabled(has_models)
            self.model_selection_group.setVisible(has_models)
            
            # 显示服务详细信息
            available_count = len(selected_service.available_models)
            details = (
                f"服务名称: {selected_service.display_name}\n"
                f"服务地址: {selected_service.base_url}\n"
                f"API密钥: {'需要' if selected_service.api_key_required else '不需要'}\n"
                f"状态: {selected_service.status}\n"
                f"可用模型数量: {available_count}\n\n"
                f"推荐模型配置:\n"
                f"• 视觉模型: {selected_service.default_models.get('vision_model', 'N/A')}\n"
                f"• 语言模型: {selected_service.default_models.get('language_model', 'N/A')}\n\n"
                f"您可以在上方的模型选择中更改配置。"
            )
            self.service_details.setPlainText(details)
            
        except Exception as e:
            self.service_details.setPlainText(f"获取服务详情出错: {str(e)}")
            self.model_selection_group.setVisible(False)
    
    def _apply_service_config(self):
        """应用选中服务的配置"""
        current_index = self.service_combo.currentIndex()
        if current_index < 0 or not self.detected_services:
            return
        
        try:
            # 获取选中的服务
            selected_service = self.service_combo.currentData()
            if not selected_service:
                return
            
            # 获取用户选择的模型
            vision_model = self.vision_model_combo.currentText() if self.vision_model_combo.isEnabled() else None
            language_model = self.language_model_combo.currentText() if self.language_model_combo.isEnabled() else None
            
            # 获取服务配置（使用用户选择的模型）
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            config = loop.run_until_complete(
                service_detector.get_service_config(selected_service, vision_model, language_model)
            )
            loop.close()
            
            # 通知父窗口应用配置
            parent_dialog = self.parent()
            while parent_dialog and not hasattr(parent_dialog, 'apply_auto_config'):
                parent_dialog = parent_dialog.parent()
            
            if parent_dialog and hasattr(parent_dialog, 'apply_auto_config'):
                parent_dialog.apply_auto_config(config)
            
            # 显示成功消息
            vision_config = config.get("vision_model", {})
            language_config = config.get("language_model", {})
            
            QMessageBox.information(
                self, 
                "配置应用成功",
                f"已成功应用 {selected_service.display_name} 的配置！\n\n"
                f"视觉模型: {vision_config.get('model_name', 'N/A')}\n"
                f"语言模型: {language_config.get('model_name', 'N/A')}\n\n"
                "配置已自动同步到手动配置标签页。\n"
                "您可以切换到手动配置页面查看详细参数。"
            )
            
        except Exception as e:
            QMessageBox.warning(self, "配置失败", f"应用服务配置时出错：\n{str(e)}")
    
    def get_detected_services(self) -> list:
        """获取检测到的服务列表"""
        return self.detected_services