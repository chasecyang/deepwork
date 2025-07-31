"""
AI客户端模块
负责OpenAI API的集成和配置检查
"""
import asyncio
import base64
import os
from typing import Dict, Any, Optional, Tuple
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)


def _suppress_third_party_logs():
    """抑制第三方库的调试日志"""
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


# 初始化时就抑制第三方库日志
_suppress_third_party_logs()


class AIClient:
    """AI客户端类，用于管理OpenAI API连接和配置检查"""
    
    def __init__(self):
        self.vision_client: Optional[AsyncOpenAI] = None
        self.language_client: Optional[AsyncOpenAI] = None
    
    def update_vision_client(self, config: Dict[str, str]) -> None:
        """更新视觉模型客户端配置"""
        if not config.get("base_url") or not config.get("model_name"):
            self.vision_client = None
            return
            
        self.vision_client = AsyncOpenAI(
            base_url=config["base_url"],
            api_key=config.get("api_key", "dummy-key"),  # 某些兼容API不需要真实key
        )
    
    def update_language_client(self, config: Dict[str, str]) -> None:
        """更新语言模型客户端配置"""
        if not config.get("base_url") or not config.get("model_name"):
            self.language_client = None
            return
            
        self.language_client = AsyncOpenAI(
            base_url=config["base_url"],
            api_key=config.get("api_key", "dummy-key"),  # 某些兼容API不需要真实key
        )
    
    async def check_vision_model(self, config: Dict[str, str]) -> Tuple[bool, str]:
        """
        检查视觉模型配置是否可用
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        if not config.get("base_url") or not config.get("model_name"):
            return False, "请填写完整的Base URL和模型名称"
        
        try:
            # 创建临时客户端进行测试
            test_client = AsyncOpenAI(
                base_url=config["base_url"],
                api_key=config.get("api_key", "dummy-key"),
            )
            
            # 测试模型列表接口
            models = await test_client.models.list()
            model_names = [model.id for model in models.data]
            
            # 检查指定的模型是否存在
            if config["model_name"] in model_names:
                return True, f"✅ 模型 {config['model_name']} 可用"
            else:
                available_models = ", ".join(model_names[:5])  # 显示前5个可用模型
                if len(model_names) > 5:
                    available_models += f" 等({len(model_names)}个模型)"
                return False, f"❌ 模型 {config['model_name']} 不可用。可用模型: {available_models}"
                
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "authentication" in error_msg.lower():
                return False, "❌ API密钥无效或未提供"
            elif "404" in error_msg or "not found" in error_msg.lower():
                return False, "❌ API端点不存在，请检查Base URL"
            elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                return False, "❌ 连接超时，请检查网络或Base URL"
            else:
                return False, f"❌ 连接失败: {error_msg}"
    
    async def check_language_model(self, config: Dict[str, str]) -> Tuple[bool, str]:
        """
        检查语言模型配置是否可用
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        if not config.get("base_url") or not config.get("model_name"):
            return False, "请填写完整的Base URL和模型名称"
        
        try:
            # 创建临时客户端进行测试
            test_client = AsyncOpenAI(
                base_url=config["base_url"],
                api_key=config.get("api_key", "dummy-key"),
            )
            
            # 测试模型列表接口
            models = await test_client.models.list()
            model_names = [model.id for model in models.data]
            
            # 检查指定的模型是否存在
            if config["model_name"] in model_names:
                return True, f"✅ 模型 {config['model_name']} 可用"
            else:
                available_models = ", ".join(model_names[:5])  # 显示前5个可用模型
                if len(model_names) > 5:
                    available_models += f" 等({len(model_names)}个模型)"
                return False, f"❌ 模型 {config['model_name']} 不可用。可用模型: {available_models}"
                
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "authentication" in error_msg.lower():
                return False, "❌ API密钥无效或未提供"
            elif "404" in error_msg or "not found" in error_msg.lower():
                return False, "❌ API端点不存在，请检查Base URL"
            elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                return False, "❌ 连接超时，请检查网络或Base URL"
            else:
                return False, f"❌ 连接失败: {error_msg}"
    
    def _encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """
        将图像文件编码为base64格式
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            Optional[str]: base64编码的图像数据，如果失败返回None
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"图像文件不存在: {image_path}")
                return None
                
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
                return base64_image
        except Exception as e:
            logger.error(f"编码图像失败: {e}")
            return None

    async def test_vision_generation_with_image(self, config: Dict[str, str], image_path: str, test_prompt: str = "请描述这张图片的内容") -> Tuple[bool, str]:
        """
        测试视觉模型的图像理解功能
        
        Args:
            config: 模型配置
            image_path: 测试图片路径
            test_prompt: 测试提示词
            
        Returns:
            Tuple[bool, str]: (是否成功, 响应消息)
        """
        if not config.get("base_url") or not config.get("model_name"):
            return False, "请填写完整的配置信息"
        
        # 编码图像
        base64_image = self._encode_image_to_base64(image_path)
        if not base64_image:
            return False, f"❌ 无法读取测试图片: {image_path}"
        
        try:
            test_client = AsyncOpenAI(
                base_url=config["base_url"],
                api_key=config.get("api_key", "dummy-key"),
            )
            
            # 构建包含图像的消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": test_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            response = await test_client.chat.completions.create(
                model=config["model_name"],
                messages=messages,
            )
            
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
                return True, f"✅ 视觉模型图像理解测试成功: {content[:100]}..."
            else:
                return False, "❌ 视觉模型生成失败，无响应"
                
        except Exception as e:
            return False, f"❌ 视觉模型图像测试失败: {str(e)}"
    
    async def test_language_generation(self, config: Dict[str, str], test_prompt: str = "请简单回复'测试成功'") -> Tuple[bool, str]:
        """
        测试语言模型的文本生成功能
        
        Args:
            config: 模型配置
            test_prompt: 测试提示词
            
        Returns:
            Tuple[bool, str]: (是否成功, 响应消息)
        """
        if not config.get("base_url") or not config.get("model_name"):
            return False, "请填写完整的配置信息"
        
        try:
            test_client = AsyncOpenAI(
                base_url=config["base_url"],
                api_key=config.get("api_key", "dummy-key"),
            )
            
            response = await test_client.chat.completions.create(
                model=config["model_name"],
                messages=[
                    {"role": "user", "content": test_prompt}
                ],

            )
            
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
                return True, f"✅ 语言模型生成测试成功: {content[:50]}..."
            else:
                return False, "❌ 语言模型生成失败，无响应"
                
        except Exception as e:
            return False, f"❌ 语言模型生成测试失败: {str(e)}"
    
    async def call_vision_model(self, config: Dict[str, str], image_path: str, prompt: str) -> Optional[str]:
        """
        调用视觉语言模型进行图像分析
        
        Args:
            config: 模型配置
            image_path: 图像文件路径
            prompt: 分析提示词
            
        Returns:
            Optional[str]: 模型响应内容，失败时返回None
        """
        if not config.get("base_url") or not config.get("model_name"):
            logger.error("视觉模型配置不完整")
            return None
        
        # 编码图像
        base64_image = self._encode_image_to_base64(image_path)
        if not base64_image:
            logger.error(f"无法读取图像文件: {image_path}")
            return None
        
        try:
            # 确保客户端使用最新配置
            self.update_vision_client(config)
            
            if not self.vision_client:
                logger.error("视觉模型客户端初始化失败")
                return None
            
            # 构建包含图像的消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            response = await self.vision_client.chat.completions.create(
                model=config["model_name"],
                messages=messages,
            )
            
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                if content:
                    return content.strip()
            
            logger.error("视觉模型响应为空")
            return None
                
        except Exception as e:
            logger.error(f"视觉模型调用失败: {e}")
            return None
    
    async def call_language_model(self, config: Dict[str, str], prompt: str) -> Optional[str]:
        """
        调用大语言模型进行文本生成
        
        Args:
            config: 模型配置
            prompt: 输入提示词
            
        Returns:
            Optional[str]: 模型响应内容，失败时返回None
        """
        if not config.get("base_url") or not config.get("model_name"):
            logger.error("语言模型配置不完整")
            return None
        
        try:
            # 确保客户端使用最新配置
            self.update_language_client(config)
            
            if not self.language_client:
                logger.error("语言模型客户端初始化失败")
                return None
            
            response = await self.language_client.chat.completions.create(
                model=config["model_name"],
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                if content:
                    return content.strip()
            
            logger.error("语言模型响应为空")
            return None
                
        except Exception as e:
            logger.error(f"语言模型调用失败: {e}")
            return None



# 全局AI客户端实例
ai_client = AIClient()