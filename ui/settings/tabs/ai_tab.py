"""
AI模型设置标签页
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QGroupBox, QGridLayout)
from PySide6.QtCore import Qt
from ui.theme import ModernTheme
from ..components.model_tester import ModelTester


class AISettingsTab(QWidget):
    """AI模型设置标签页"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_tester = ModelTester(self)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 视觉模型设置组
        vision_group = self._create_vision_model_group()
        main_layout.addWidget(vision_group)
        
        # 语言模型设置组
        language_group = self._create_language_model_group()
        main_layout.addWidget(language_group)
        
        # 添加弹性空间
        main_layout.addStretch()
    
    def _create_vision_model_group(self) -> QGroupBox:
        """创建视觉模型设置组"""
        vision_group = QGroupBox("视觉模型设置")
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
        self.vision_base_url_edit = QLineEdit()
        self.vision_base_url_edit.setPlaceholderText("https://api.openai.com/v1")
        self.vision_base_url_edit.setMinimumHeight(28)
        vision_grid_layout.addWidget(vision_url_label, 0, 0)
        vision_grid_layout.addWidget(self.vision_base_url_edit, 0, 1)
        
        # API Key
        vision_key_label = QLabel("API Key:")
        vision_key_label.setMinimumWidth(80)
        vision_key_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.vision_api_key_edit = QLineEdit()
        self.vision_api_key_edit.setPlaceholderText("可选")
        self.vision_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.vision_api_key_edit.setMinimumHeight(28)
        vision_grid_layout.addWidget(vision_key_label, 1, 0)
        vision_grid_layout.addWidget(self.vision_api_key_edit, 1, 1)
        
        # Model Name
        vision_model_label = QLabel("模型名称:")
        vision_model_label.setMinimumWidth(80)
        vision_model_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.vision_model_name_edit = QLineEdit()
        self.vision_model_name_edit.setPlaceholderText("gpt-4-vision-preview")
        self.vision_model_name_edit.setMinimumHeight(28)
        vision_grid_layout.addWidget(vision_model_label, 2, 0)
        vision_grid_layout.addWidget(self.vision_model_name_edit, 2, 1)
        
        vision_group_layout.addLayout(vision_grid_layout)
        
        # 视觉模型测试按钮和状态
        vision_test_layout = QHBoxLayout()
        vision_test_layout.setSpacing(12)
        self.vision_test_button = QPushButton("👁️ 测试图像理解")
        self.vision_test_button.setMinimumHeight(36)
        self.vision_test_button.setMinimumWidth(140)
        self.vision_test_button.clicked.connect(self._test_vision_model)
        self.vision_status_label = QLabel("")
        self.vision_status_label.setWordWrap(True)
        self.vision_status_label.setStyleSheet("color: #666; font-size: 12px;")
        vision_test_layout.addWidget(self.vision_test_button)
        vision_test_layout.addWidget(self.vision_status_label)
        vision_test_layout.addStretch()
        
        vision_group_layout.addLayout(vision_test_layout)
        
        return vision_group
    
    def _create_language_model_group(self) -> QGroupBox:
        """创建语言模型设置组"""
        language_group = QGroupBox("语言模型设置")
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
        self.language_base_url_edit = QLineEdit()
        self.language_base_url_edit.setPlaceholderText("https://api.openai.com/v1")
        self.language_base_url_edit.setMinimumHeight(28)
        language_grid_layout.addWidget(language_url_label, 0, 0)
        language_grid_layout.addWidget(self.language_base_url_edit, 0, 1)
        
        # API Key
        language_key_label = QLabel("API Key:")
        language_key_label.setMinimumWidth(80)
        language_key_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.language_api_key_edit = QLineEdit()
        self.language_api_key_edit.setPlaceholderText("可选")
        self.language_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.language_api_key_edit.setMinimumHeight(28)
        language_grid_layout.addWidget(language_key_label, 1, 0)
        language_grid_layout.addWidget(self.language_api_key_edit, 1, 1)
        
        # Model Name
        language_model_label = QLabel("模型名称:")
        language_model_label.setMinimumWidth(80)
        language_model_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.language_model_name_edit = QLineEdit()
        self.language_model_name_edit.setPlaceholderText("gpt-4")
        self.language_model_name_edit.setMinimumHeight(28)
        language_grid_layout.addWidget(language_model_label, 2, 0)
        language_grid_layout.addWidget(self.language_model_name_edit, 2, 1)
        
        language_group_layout.addLayout(language_grid_layout)
        
        # 语言模型测试按钮和状态
        language_test_layout = QHBoxLayout()
        language_test_layout.setSpacing(12)
        self.language_test_button = QPushButton("🤖 测试生成")
        self.language_test_button.setMinimumHeight(36)
        self.language_test_button.setMinimumWidth(120)
        self.language_test_button.clicked.connect(self._test_language_model)
        self.language_status_label = QLabel("")
        self.language_status_label.setWordWrap(True)
        self.language_status_label.setStyleSheet("color: #666; font-size: 12px;")
        language_test_layout.addWidget(self.language_test_button)
        language_test_layout.addWidget(self.language_status_label)
        language_test_layout.addStretch()
        
        language_group_layout.addLayout(language_test_layout)
        
        return language_group
    
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
    
    def _on_vision_test_finished(self, success: bool, message: str):
        """视觉模型测试完成回调"""
        if success:
            self.vision_status_label.setStyleSheet(f"color: {ModernTheme.COLORS['success']};")
        else:
            self.vision_status_label.setStyleSheet(f"color: {ModernTheme.COLORS['error']};")
    
    def _on_language_test_finished(self, success: bool, message: str):
        """语言模型测试完成回调"""
        if success:
            self.language_status_label.setStyleSheet(f"color: {ModernTheme.COLORS['success']};")
        else:
            self.language_status_label.setStyleSheet(f"color: {ModernTheme.COLORS['error']};")
    
    # 注释：移除了_check_and_emit_success_signal方法，因为不再需要在测试时立即发送信号
    # 现在的逻辑是：用户完成设置后关闭对话框，然后重新进入唤醒状态检查完整配置
    
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