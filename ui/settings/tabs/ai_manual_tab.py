"""
AI模型手动配置标签页
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QGroupBox, QGridLayout,
                               QMessageBox, QScrollArea)
from PySide6.QtCore import Qt
from ui.theme import ModernTheme
from ..components.model_tester import ModelTester


class AIManualConfigTab(QWidget):
    """AI模型手动配置标签页"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_tester = ModelTester(self)
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
        scroll_content.setMinimumHeight(700)  # 设置最小高度，手动配置内容更多
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        # 顶部说明区域
        info_group = self._create_info_group()
        content_layout.addWidget(info_group)
        
        # 视觉模型设置组
        vision_group = self._create_vision_model_group()
        content_layout.addWidget(vision_group)
        
        # 语言模型设置组
        language_group = self._create_language_model_group()
        content_layout.addWidget(language_group)
        
        # 批量操作区域
        batch_group = self._create_batch_operations_group()
        content_layout.addWidget(batch_group)
        
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
        info_group = QGroupBox("⚙️ 手动配置AI模型")
        info_layout = QVBoxLayout(info_group)
        info_layout.setSpacing(10)
        info_layout.setContentsMargins(15, 20, 15, 15)
        
        # 主要说明
        main_info = QLabel("手动配置AI模型的连接参数和模型名称")
        main_info.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
        info_layout.addWidget(main_info)
        
        # 详细说明
        detail_info = QLabel(
            "• 支持OpenAI兼容的API接口\n"
            "• 可配置自定义的Base URL和API Key\n"
            "• 分别设置视觉模型和语言模型\n"
            "• 提供连接测试功能验证配置"
        )
        detail_info.setStyleSheet("color: #666; font-size: 12px; line-height: 1.4;")
        detail_info.setWordWrap(True)
        info_layout.addWidget(detail_info)
        
        return info_group
    
    def _create_vision_model_group(self) -> QGroupBox:
        """创建视觉模型设置组"""
        vision_group = QGroupBox("👁️ 视觉模型设置")
        vision_group_layout = QVBoxLayout(vision_group)
        vision_group_layout.setSpacing(15)
        vision_group_layout.setContentsMargins(15, 20, 15, 15)
        
        # 使用网格布局确保字段整齐排列
        vision_grid_layout = QGridLayout()
        vision_grid_layout.setHorizontalSpacing(15)
        vision_grid_layout.setVerticalSpacing(12)
        vision_grid_layout.setColumnStretch(1, 1)  # 让输入框列可以扩展
        
        # Base URL
        vision_url_label = QLabel("Base URL:")
        vision_url_label.setMinimumWidth(80)
        vision_url_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        vision_url_label.setStyleSheet("font-weight: bold; color: #333;")
        self.vision_base_url_edit = QLineEdit()
        self.vision_base_url_edit.setPlaceholderText("例如: https://api.openai.com/v1")
        self.vision_base_url_edit.setMinimumHeight(32)
        self.vision_base_url_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e5e9;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #0066cc;
            }
        """)
        vision_grid_layout.addWidget(vision_url_label, 0, 0)
        vision_grid_layout.addWidget(self.vision_base_url_edit, 0, 1)
        
        # API Key
        vision_key_label = QLabel("API Key:")
        vision_key_label.setMinimumWidth(80)
        vision_key_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        vision_key_label.setStyleSheet("font-weight: bold; color: #333;")
        self.vision_api_key_edit = QLineEdit()
        self.vision_api_key_edit.setPlaceholderText("可选 - 某些服务需要API密钥")
        self.vision_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.vision_api_key_edit.setMinimumHeight(32)
        self.vision_api_key_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e5e9;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #0066cc;
            }
        """)
        vision_grid_layout.addWidget(vision_key_label, 1, 0)
        vision_grid_layout.addWidget(self.vision_api_key_edit, 1, 1)
        
        # Model Name
        vision_model_label = QLabel("模型名称:")
        vision_model_label.setMinimumWidth(80)
        vision_model_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        vision_model_label.setStyleSheet("font-weight: bold; color: #333;")
        self.vision_model_name_edit = QLineEdit()
        self.vision_model_name_edit.setPlaceholderText("例如: gpt-4-vision-preview 或 llava:latest")
        self.vision_model_name_edit.setMinimumHeight(32)
        self.vision_model_name_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e5e9;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #0066cc;
            }
        """)
        vision_grid_layout.addWidget(vision_model_label, 2, 0)
        vision_grid_layout.addWidget(self.vision_model_name_edit, 2, 1)
        
        vision_group_layout.addLayout(vision_grid_layout)
        
        # 视觉模型测试按钮和状态
        vision_test_layout = QHBoxLayout()
        vision_test_layout.setSpacing(12)
        self.vision_test_button = QPushButton("🧪 测试视觉模型")
        self.vision_test_button.setMinimumHeight(38)
        self.vision_test_button.setMinimumWidth(140)
        self.vision_test_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
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
        self.vision_test_button.clicked.connect(self._test_vision_model)
        self.vision_status_label = QLabel("点击测试按钮验证配置")
        self.vision_status_label.setWordWrap(True)
        self.vision_status_label.setStyleSheet("color: #666; font-size: 12px;")
        vision_test_layout.addWidget(self.vision_test_button)
        vision_test_layout.addWidget(self.vision_status_label)
        vision_test_layout.addStretch()
        
        vision_group_layout.addLayout(vision_test_layout)
        
        return vision_group
    
    def _create_language_model_group(self) -> QGroupBox:
        """创建语言模型设置组"""
        language_group = QGroupBox("🤖 语言模型设置")
        language_group_layout = QVBoxLayout(language_group)
        language_group_layout.setSpacing(15)
        language_group_layout.setContentsMargins(15, 20, 15, 15)
        
        # 使用网格布局确保字段整齐排列
        language_grid_layout = QGridLayout()
        language_grid_layout.setHorizontalSpacing(15)
        language_grid_layout.setVerticalSpacing(12)
        language_grid_layout.setColumnStretch(1, 1)  # 让输入框列可以扩展
        
        # Base URL
        language_url_label = QLabel("Base URL:")
        language_url_label.setMinimumWidth(80)
        language_url_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        language_url_label.setStyleSheet("font-weight: bold; color: #333;")
        self.language_base_url_edit = QLineEdit()
        self.language_base_url_edit.setPlaceholderText("例如: https://api.openai.com/v1")
        self.language_base_url_edit.setMinimumHeight(32)
        self.language_base_url_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e5e9;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #0066cc;
            }
        """)
        language_grid_layout.addWidget(language_url_label, 0, 0)
        language_grid_layout.addWidget(self.language_base_url_edit, 0, 1)
        
        # API Key
        language_key_label = QLabel("API Key:")
        language_key_label.setMinimumWidth(80)
        language_key_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        language_key_label.setStyleSheet("font-weight: bold; color: #333;")
        self.language_api_key_edit = QLineEdit()
        self.language_api_key_edit.setPlaceholderText("可选 - 某些服务需要API密钥")
        self.language_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.language_api_key_edit.setMinimumHeight(32)
        self.language_api_key_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e5e9;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #0066cc;
            }
        """)
        language_grid_layout.addWidget(language_key_label, 1, 0)
        language_grid_layout.addWidget(self.language_api_key_edit, 1, 1)
        
        # Model Name
        language_model_label = QLabel("模型名称:")
        language_model_label.setMinimumWidth(80)
        language_model_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        language_model_label.setStyleSheet("font-weight: bold; color: #333;")
        self.language_model_name_edit = QLineEdit()
        self.language_model_name_edit.setPlaceholderText("例如: gpt-4 或 llama3.1:latest")
        self.language_model_name_edit.setMinimumHeight(32)
        self.language_model_name_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e5e9;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #0066cc;
            }
        """)
        language_grid_layout.addWidget(language_model_label, 2, 0)
        language_grid_layout.addWidget(self.language_model_name_edit, 2, 1)
        
        language_group_layout.addLayout(language_grid_layout)
        
        # 语言模型测试按钮和状态
        language_test_layout = QHBoxLayout()
        language_test_layout.setSpacing(12)
        self.language_test_button = QPushButton("🧪 测试语言模型")
        self.language_test_button.setMinimumHeight(38)
        self.language_test_button.setMinimumWidth(140)
        self.language_test_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
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
        self.language_test_button.clicked.connect(self._test_language_model)
        self.language_status_label = QLabel("点击测试按钮验证配置")
        self.language_status_label.setWordWrap(True)
        self.language_status_label.setStyleSheet("color: #666; font-size: 12px;")
        language_test_layout.addWidget(self.language_test_button)
        language_test_layout.addWidget(self.language_status_label)
        language_test_layout.addStretch()
        
        language_group_layout.addLayout(language_test_layout)
        
        return language_group
    
    def _create_batch_operations_group(self) -> QGroupBox:
        """创建批量操作组"""
        batch_group = QGroupBox("批量操作")
        batch_layout = QHBoxLayout(batch_group)
        batch_layout.setSpacing(15)
        batch_layout.setContentsMargins(15, 20, 15, 15)
        
        # 同步配置按钮
        self.sync_config_button = QPushButton("🔄 同步配置")
        self.sync_config_button.setMinimumHeight(38)
        self.sync_config_button.setMinimumWidth(120)
        self.sync_config_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.sync_config_button.clicked.connect(self._sync_configurations)
        self.sync_config_button.setToolTip("将语言模型的配置复制到视觉模型")
        batch_layout.addWidget(self.sync_config_button)
        
        # 清空配置按钮
        self.clear_config_button = QPushButton("🗑️ 清空配置")
        self.clear_config_button.setMinimumHeight(38)
        self.clear_config_button.setMinimumWidth(120)
        self.clear_config_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.COLORS['error']};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #c82333;
            }}
        """)
        self.clear_config_button.clicked.connect(self._clear_all_configurations)
        self.clear_config_button.setToolTip("清空所有配置信息")
        batch_layout.addWidget(self.clear_config_button)
        
        # 测试所有配置按钮
        self.test_all_button = QPushButton("🚀 测试所有配置")
        self.test_all_button.setMinimumHeight(38)
        self.test_all_button.setMinimumWidth(140)
        self.test_all_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.COLORS['warning']};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #e0a800;
            }}
        """)
        self.test_all_button.clicked.connect(self._test_all_models)
        self.test_all_button.setToolTip("同时测试视觉和语言模型")
        batch_layout.addWidget(self.test_all_button)
        
        batch_layout.addStretch()
        
        return batch_group
    
    def _test_vision_model(self):
        """测试视觉模型"""
        config = {
            "base_url": self.vision_base_url_edit.text().strip(),
            "api_key": self.vision_api_key_edit.text().strip(),
            "model_name": self.vision_model_name_edit.text().strip()
        }
        
        self.model_tester.test_vision_model(
            config,
            self.vision_test_button,
            self.vision_status_label,
            self._on_vision_test_finished
        )
    
    def _test_language_model(self):
        """测试语言模型"""
        config = {
            "base_url": self.language_base_url_edit.text().strip(),
            "api_key": self.language_api_key_edit.text().strip(),
            "model_name": self.language_model_name_edit.text().strip()
        }
        
        self.model_tester.test_language_model(
            config,
            self.language_test_button,
            self.language_status_label,
            self._on_language_test_finished
        )
    
    def _test_all_models(self):
        """测试所有模型配置"""
        # 先测试视觉模型
        self._test_vision_model()
        # 稍后测试语言模型 (避免同时进行)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1000, self._test_language_model)
    
    def _sync_configurations(self):
        """同步配置 - 将语言模型配置复制到视觉模型"""
        reply = QMessageBox.question(
            self,
            "确认同步",
            "确定要将语言模型的配置复制到视觉模型吗？\n这将覆盖当前的视觉模型配置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 复制配置
            self.vision_base_url_edit.setText(self.language_base_url_edit.text())
            self.vision_api_key_edit.setText(self.language_api_key_edit.text())
            # 模型名称不复制，因为通常不同
            
            QMessageBox.information(self, "同步完成", "已将语言模型的URL和API Key同步到视觉模型配置。")
    
    def _clear_all_configurations(self):
        """清空所有配置"""
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有AI模型配置吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 清空所有输入框
            self.vision_base_url_edit.clear()
            self.vision_api_key_edit.clear()
            self.vision_model_name_edit.clear()
            self.language_base_url_edit.clear()
            self.language_api_key_edit.clear()
            self.language_model_name_edit.clear()
            
            # 重置状态标签
            self.vision_status_label.setText("点击测试按钮验证配置")
            self.vision_status_label.setStyleSheet("color: #666; font-size: 12px;")
            self.language_status_label.setText("点击测试按钮验证配置")
            self.language_status_label.setStyleSheet("color: #666; font-size: 12px;")
            
            QMessageBox.information(self, "清空完成", "已清空所有AI模型配置。")
    
    def _on_vision_test_finished(self, success: bool, message: str):
        """视觉模型测试完成回调"""
        if success:
            self.vision_status_label.setStyleSheet(f"color: {ModernTheme.COLORS['success']}; font-weight: bold;")
        else:
            self.vision_status_label.setStyleSheet(f"color: {ModernTheme.COLORS['error']}; font-weight: bold;")
    
    def _on_language_test_finished(self, success: bool, message: str):
        """语言模型测试完成回调"""
        if success:
            self.language_status_label.setStyleSheet(f"color: {ModernTheme.COLORS['success']}; font-weight: bold;")
        else:
            self.language_status_label.setStyleSheet(f"color: {ModernTheme.COLORS['error']}; font-weight: bold;")
    
    def load_settings(self, config):
        """加载设置"""
        # 加载AI模型设置
        vision_model = config.get("vision_model", {})
        self.vision_base_url_edit.setText(vision_model.get("base_url", ""))
        self.vision_api_key_edit.setText(vision_model.get("api_key", ""))
        self.vision_model_name_edit.setText(vision_model.get("model_name", ""))
        
        language_model = config.get("language_model", {})
        self.language_base_url_edit.setText(language_model.get("base_url", ""))
        self.language_api_key_edit.setText(language_model.get("api_key", ""))
        self.language_model_name_edit.setText(language_model.get("model_name", ""))
    
    def get_settings(self) -> dict:
        """获取设置"""
        vision_model_config = {
            "base_url": self.vision_base_url_edit.text().strip(),
            "api_key": self.vision_api_key_edit.text().strip(),
            "model_name": self.vision_model_name_edit.text().strip()
        }
        
        language_model_config = {
            "base_url": self.language_base_url_edit.text().strip(),
            "api_key": self.language_api_key_edit.text().strip(),
            "model_name": self.language_model_name_edit.text().strip()
        }
        
        return {
            "vision_model": vision_model_config,
            "language_model": language_model_config
        }
    
    def apply_config(self, config):
        """应用配置（通常来自自动检测）"""
        self.load_settings(config)
        
        # 重置状态标签为提示测试
        self.vision_status_label.setText("已应用自动配置，建议点击测试验证")
        self.vision_status_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        self.language_status_label.setText("已应用自动配置，建议点击测试验证")
        self.language_status_label.setStyleSheet("color: #2196F3; font-weight: bold;")