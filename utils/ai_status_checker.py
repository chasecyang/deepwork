"""
AI功能状态检查器
负责检查AI模型的可用性状态
"""
import asyncio
import logging
from typing import Dict, Any, Tuple
from .ai_client import AIClient

logger = logging.getLogger(__name__)


class AIStatusChecker:
    """AI功能状态检查器"""
    
    def __init__(self):
        self.ai_client = AIClient()
    
    async def check_ai_availability(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        检查AI功能整体可用性
        
        Args:
            config: 完整配置字典
            
        Returns:
            Tuple[bool, str]: (是否可用, 状态消息)
        """
        vision_available = False
        language_available = False
        messages = []
        
        # 检查视觉模型
        vision_config = config.get("vision_model", {})
        if self._has_valid_config(vision_config):
            try:
                vision_available, vision_msg = await self.check_vision_model_basic(vision_config)
                if vision_available:
                    messages.append("✅ 视觉模型可用")
                else:
                    messages.append(f"❌ 视觉模型: {vision_msg}")
            except Exception as e:
                messages.append(f"❌ 视觉模型检查失败: {str(e)}")
        else:
            messages.append("⚠️ 视觉模型未配置")
        
        # 检查语言模型
        language_config = config.get("language_model", {})
        if self._has_valid_config(language_config):
            try:
                language_available, language_msg = await self.check_language_model_basic(language_config)
                if language_available:
                    messages.append("✅ 语言模型可用")
                else:
                    messages.append(f"❌ 语言模型: {language_msg}")
            except Exception as e:
                messages.append(f"❌ 语言模型检查失败: {str(e)}")
        else:
            messages.append("⚠️ 语言模型未配置")
        
        # 需要两个模型都可用
        ai_available = vision_available and language_available
        status_message = " \n ".join(messages)
        
        if ai_available:
            logger.info(f"AI功能可用: {status_message}")
        else:
            logger.warning(f"AI功能不可用:\n {status_message}")
        
        return ai_available, status_message
    
    async def check_vision_model_basic(self, config: Dict[str, str]) -> Tuple[bool, str]:
        """
        基础视觉模型检查（仅检查连接和模型列表，不进行实际生成）
        
        Args:
            config: 视觉模型配置
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        return await self.ai_client.check_vision_model(config)
    
    async def check_language_model_basic(self, config: Dict[str, str]) -> Tuple[bool, str]:
        """
        基础语言模型检查（仅检查连接和模型列表，不进行实际生成）
        
        Args:
            config: 语言模型配置
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        return await self.ai_client.check_language_model(config)
    
    def _has_valid_config(self, model_config: Dict[str, str]) -> bool:
        """
        检查模型配置是否有效
        
        Args:
            model_config: 模型配置字典
            
        Returns:
            bool: 配置是否有效
        """
        return (
            model_config.get("base_url", "").strip() != "" and
            model_config.get("model_name", "").strip() != ""
        )
    
    async def quick_health_check(self, config: Dict[str, Any]) -> bool:
        """
        快速健康检查（用于启动时的快速验证）
        
        Args:
            config: 完整配置字典
            
        Returns:
            bool: AI功能是否可用
        """
        try:
            available, _ = await self.check_ai_availability(config)
            return available
        except Exception as e:
            logger.error(f"快速健康检查失败: {e}")
            return False


# 全局AI状态检查器实例
ai_status_checker = AIStatusChecker()