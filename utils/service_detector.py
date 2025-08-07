"""
服务检测器模块
用于自动检测ollama和lemonade等AI服务
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ServiceInfo:
    """服务信息数据类"""
    name: str
    display_name: str
    base_url: str
    api_key_required: bool
    default_models: Dict[str, str]  # vision_model, language_model
    status: str = "unknown"  # unknown, available, unavailable
    available_models: List[str] = None  # 实际可用的模型列表
    
    def __post_init__(self):
        """初始化后处理"""
        if self.available_models is None:
            self.available_models = []


class ServiceDetector:
    """AI服务检测器"""
    
    def __init__(self):
        # 预定义的服务配置
        self.known_services = {
            "ollama": ServiceInfo(
                name="ollama",
                display_name="Ollama 本地服务",
                base_url="http://localhost:11434/v1",
                api_key_required=False,
                default_models={
                    "vision_model": "llava:latest",
                    "language_model": "llama3.1:latest"
                }
            ),
            "lemonade": ServiceInfo(
                name="lemonade", 
                display_name="Lemonade API 服务",
                base_url="http://localhost:8000/api/v1",
                api_key_required=False,
                default_models={
                    "vision_model": "gpt-4-vision-preview",
                    "language_model": "gpt-4"
                }
            )
        }
    
    async def detect_services(self, timeout: float = 3.0) -> List[ServiceInfo]:
        """
        检测可用的AI服务
        
        Args:
            timeout: 检测超时时间（秒）
            
        Returns:
            List[ServiceInfo]: 检测到的服务列表
        """
        available_services = []
        
        for service_name, service_info in self.known_services.items():
            try:
                is_available = await self._check_service_availability(
                    service_info.base_url, timeout
                )
                
                if is_available:
                    # 获取可用模型列表
                    models = await self._get_available_models(
                        service_info.base_url, timeout
                    )
                    
                    # 存储可用模型列表
                    service_info.available_models = models
                    
                    # 更新默认模型为实际可用的模型
                    if models:
                        service_info = self._update_default_models(service_info, models)
                    
                    service_info.status = "available"
                    available_services.append(service_info)
                    logger.info(f"检测到可用服务: {service_info.display_name}")
                else:
                    service_info.status = "unavailable"
                    
            except Exception as e:
                logger.debug(f"检测服务 {service_name} 时出错: {e}")
                service_info.status = "unavailable"
        
        return available_services
    
    async def _check_service_availability(self, base_url: str, timeout: float) -> bool:
        """
        检查服务是否可用
        
        Args:
            base_url: 服务基础URL
            timeout: 超时时间
            
        Returns:
            bool: 服务是否可用
        """
        try:
            # 构建健康检查URL
            health_urls = [
                f"{base_url}/models",  # OpenAI兼容接口
                f"{base_url.rstrip('/v1')}/api/tags",  # Ollama原生接口
                f"{base_url}/health",  # 通用健康检查
            ]
            
            connector = aiohttp.TCPConnector(limit=10)
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            
            async with aiohttp.ClientSession(
                connector=connector, 
                timeout=timeout_config
            ) as session:
                for url in health_urls:
                    try:
                        async with session.get(url) as response:
                            if response.status == 200:
                                return True
                    except Exception:
                        continue
                        
            return False
            
        except Exception as e:
            logger.debug(f"检查服务可用性失败 {base_url}: {e}")
            return False
    
    async def _get_available_models(self, base_url: str, timeout: float) -> List[str]:
        """
        获取服务的可用模型列表
        
        Args:
            base_url: 服务基础URL
            timeout: 超时时间
            
        Returns:
            List[str]: 可用模型列表
        """
        try:
            connector = aiohttp.TCPConnector(limit=10)
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout_config
            ) as session:
                # 尝试OpenAI兼容接口
                try:
                    models_url = f"{base_url}/models"
                    async with session.get(models_url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if "data" in data and isinstance(data["data"], list):
                                return [model.get("id", "") for model in data["data"] if model.get("id")]
                except Exception:
                    pass
                
                # 尝试Ollama原生接口
                try:
                    ollama_url = f"{base_url.rstrip('/v1')}/api/tags"
                    async with session.get(ollama_url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if "models" in data and isinstance(data["models"], list):
                                return [model.get("name", "") for model in data["models"] if model.get("name")]
                except Exception:
                    pass
            
            return []
            
        except Exception as e:
            logger.debug(f"获取模型列表失败 {base_url}: {e}")
            return []
    
    def _update_default_models(self, service_info: ServiceInfo, available_models: List[str]) -> ServiceInfo:
        """
        根据可用模型更新默认模型配置
        
        Args:
            service_info: 服务信息
            available_models: 可用模型列表
            
        Returns:
            ServiceInfo: 更新后的服务信息
        """
        if not available_models:
            return service_info
        
        # 为不同服务类型推荐合适的模型
        vision_keywords = ["vision", "llava", "gpt-4", "qwen", "claude"]
        language_keywords = ["llama", "qwen", "gpt", "claude", "mistral"]
        
        # 查找视觉模型
        vision_model = None
        for model in available_models:
            model_lower = model.lower()
            if any(keyword in model_lower for keyword in vision_keywords):
                vision_model = model
                break
        
        # 查找语言模型
        language_model = None
        for model in available_models:
            model_lower = model.lower()
            if any(keyword in model_lower for keyword in language_keywords):
                language_model = model
                break
        
        # 如果没找到特定类型的模型，使用第一个可用模型
        if not vision_model and available_models:
            vision_model = available_models[0]
        if not language_model and available_models:
            language_model = available_models[0]
        
        # 更新默认模型
        if vision_model:
            service_info.default_models["vision_model"] = vision_model
        if language_model:
            service_info.default_models["language_model"] = language_model
        
        return service_info
    
    async def get_service_config(self, service_info: ServiceInfo, 
                                vision_model: str = None, 
                                language_model: str = None) -> Dict[str, Dict[str, str]]:
        """
        获取服务的完整配置
        
        Args:
            service_info: 服务信息
            vision_model: 用户选择的视觉模型（可选）
            language_model: 用户选择的语言模型（可选）
            
        Returns:
            Dict: 完整的AI配置
        """
        # 使用用户选择的模型，如果没有则使用默认模型
        final_vision_model = vision_model or service_info.default_models.get("vision_model", "")
        final_language_model = language_model or service_info.default_models.get("language_model", "")
        
        return {
            "vision_model": {
                "base_url": service_info.base_url,
                "api_key": "" if not service_info.api_key_required else "",
                "model_name": final_vision_model
            },
            "language_model": {
                "base_url": service_info.base_url,
                "api_key": "" if not service_info.api_key_required else "",
                "model_name": final_language_model
            }
        }
    
    def get_available_models_for_service(self, service_info: ServiceInfo) -> Dict[str, List[str]]:
        """
        获取服务的可用模型，按类型分类
        
        Args:
            service_info: 服务信息
            
        Returns:
            Dict: 分类后的模型列表
        """
        if not service_info.available_models:
            return {"vision_models": [], "language_models": [], "all_models": []}
        
        vision_keywords = ["vision", "llava", "gpt-4"]
        language_keywords = ["llama", "qwen", "gpt", "claude", "mistral"]
        
        vision_models = []
        language_models = []
        
        for model in service_info.available_models:
            model_lower = model.lower()
            is_vision = any(keyword in model_lower for keyword in vision_keywords)
            is_language = any(keyword in model_lower for keyword in language_keywords)
            
            if is_vision:
                vision_models.append(model)
            if is_language:
                language_models.append(model)
        
        return {
            "vision_models": vision_models,
            "language_models": language_models,
            "all_models": service_info.available_models
        }


# 全局服务检测器实例
service_detector = ServiceDetector()