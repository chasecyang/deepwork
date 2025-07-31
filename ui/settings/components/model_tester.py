"""
AI模型测试功能模块
"""

import asyncio
import sys
import os
from PySide6.QtCore import QThread, Signal

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class ModelTestThread(QThread):
    """模型测试线程类"""
    finished_signal = Signal(bool, str)  # success, message
    
    def __init__(self, model_type: str, config: dict):
        super().__init__()
        self.model_type = model_type
        self.config = config
    
    def run(self):
        """运行测试"""
        try:
            # 导入AI客户端
            from utils.ai_client import ai_client
            
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                if self.model_type == "vision":
                    # 获取测试图片路径（从项目根目录开始）
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                    test_image_path = os.path.join(project_root, "assets", "images", "test.jpg")
                    success, message = loop.run_until_complete(
                        ai_client.test_vision_generation_with_image(self.config, test_image_path)
                    )
                else:  # language
                    success, message = loop.run_until_complete(
                        ai_client.test_language_generation(self.config)
                    )
                
                self.finished_signal.emit(success, message)
            finally:
                loop.close()
                
        except Exception as e:
            self.finished_signal.emit(False, f"❌ 测试失败: {str(e)}")


class ModelTester:
    """AI模型测试器"""
    
    def __init__(self, parent):
        self.parent = parent
        self.vision_test_thread = None
        self.language_test_thread = None
    
    def test_vision_model(self, config: dict, test_button, status_label, 
                         on_finished_callback):
        """测试视觉模型"""
        test_button.setEnabled(False)
        test_button.setText("🔄 理解中...")
        status_label.setText("正在测试模型图像理解功能...")
        
        # 创建测试线程
        self.vision_test_thread = ModelTestThread("vision", config)
        self.vision_test_thread.finished_signal.connect(
            lambda success, message: self._on_test_finished(
                success, message, test_button, status_label, 
                "👁️ 测试图像理解", on_finished_callback
            )
        )
        self.vision_test_thread.start()
    
    def test_language_model(self, config: dict, test_button, status_label, 
                           on_finished_callback):
        """测试语言模型"""
        test_button.setEnabled(False)
        test_button.setText("🔄 生成中...")
        status_label.setText("正在测试模型生成功能...")
        
        # 创建测试线程
        self.language_test_thread = ModelTestThread("language", config)
        self.language_test_thread.finished_signal.connect(
            lambda success, message: self._on_test_finished(
                success, message, test_button, status_label, 
                "🤖 测试生成", on_finished_callback
            )
        )
        self.language_test_thread.start()
    
    def _on_test_finished(self, success: bool, message: str, test_button, 
                         status_label, button_text: str, callback):
        """测试完成回调"""
        test_button.setEnabled(True)
        test_button.setText(button_text)
        status_label.setText(message)
        
        if callback:
            callback(success, message)