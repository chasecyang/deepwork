"""
专注分析器
使用AI分析屏幕截图，判断用户是否专注于目标任务
"""
import asyncio
import base64
import json
import logging
import time
from typing import Optional, Tuple, Dict, Any
from .ai_client import ai_client
from .focus_data import FocusAnalysisResult

logger = logging.getLogger(__name__)


class FocusAnalyzer:
    """专注分析器类"""
    
    def __init__(self, config: dict = None):
        """
        初始化专注分析器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
    
    async def analyze_focus(self, screenshot_path: str, focus_goal: str) -> Optional[FocusAnalysisResult]:
        """
        分析专注状态
        
        Args:
            screenshot_path: 截图文件路径
            focus_goal: 专注目标
            
        Returns:
            Optional[FocusAnalysisResult]: 分析结果
        """
        start_time = time.time()
        
        try:
            # 第一步：使用视觉模型描述屏幕内容
            visual_description = await self._describe_screenshot(screenshot_path)
            
            if not visual_description:
                logger.error("视觉描述失败")
                return None
            
            # 第二步：使用语言模型分析专注状态
            focus_analysis = await self._analyze_focus_with_llm(visual_description, focus_goal)
            
            if not focus_analysis:
                logger.error("专注状态分析失败")
                return None
            
            # 构建分析结果
            analysis_duration = time.time() - start_time
            
            result = FocusAnalysisResult(
                timestamp=time.time(),
                screenshot_path=screenshot_path,
                visual_description=visual_description,
                is_focused=focus_analysis["is_focused"],
                feedback_message=focus_analysis["feedback_message"],
                recommended_emoji=focus_analysis["recommended_emoji"],
                analysis_duration=analysis_duration
            )
            
            logger.debug(f"专注状态分析完成，耗时 {analysis_duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"专注状态分析失败: {e}")
            return None
    
    async def _describe_screenshot(self, screenshot_path: str) -> Optional[str]:
        """
        使用视觉模型描述截图内容
        
        Args:
            screenshot_path: 截图文件路径
            
        Returns:
            Optional[str]: 视觉描述
        """
        try:
            # 获取视觉模型配置
            vision_config = self.config.get("vision_model", {})
            
            if not vision_config.get("base_url") or not vision_config.get("model_name"):
                logger.warning("视觉模型未配置")
                return None
            
            # 使用AI客户端进行视觉分析
            description = await ai_client.call_vision_model(
                vision_config,
                screenshot_path,
                "请详细描述这张屏幕截图中显示的内容，包括应用程序、窗口、文本内容等。"
            )
            
            if description:
                return description
            else:
                logger.warning("视觉模型调用失败")
                return None
                
        except Exception as e:
            logger.error(f"视觉描述失败: {e}")
            return None
        
    async def _analyze_focus_with_llm(self, visual_description: str, focus_goal: str) -> Optional[Dict[str, Any]]:
        """
        使用语言模型分析专注状态
        
        Args:
            visual_description: 视觉描述
            focus_goal: 专注目标
            
        Returns:
            Optional[Dict[str, Any]]: 分析结果字典
        """
        try:
            # 获取语言模型配置
            language_config = self.config.get("language_model", {})
            
            if not language_config.get("base_url") or not language_config.get("model_name"):
                logger.error("语言模型未配置")
                return None
            
            # 构建分析提示
            prompt = self._build_analysis_prompt(visual_description, focus_goal)
            
            # 调用语言模型
            response = await ai_client.call_language_model(
                language_config,
                prompt
            )
            
            if response:
                # 解析响应
                return self._parse_llm_response(response)
            else:
                logger.error("语言模型调用失败")
                return None
                
        except Exception as e:
            logger.error(f"语言模型分析失败: {e}")
            return None
    
    def _build_analysis_prompt(self, visual_description: str, focus_goal: str) -> str:
        """
        构建分析提示词
        
        Args:
            visual_description: 视觉描述
            focus_goal: 专注目标
            
        Returns:
            str: 分析提示词
        """
        # 获取所有可用表情列表
        available_emojis = [
            "fire.gif", "rocket.gif", "heart_eyes.gif", "thumbs_up.gif", 
            "smile.gif", "ok_hand.gif", "thinking.gif", "confused.gif", 
            "sleeping.gif", "wink.gif", "heart.gif", "laugh.gif", 
            "cool.gif", "grin.gif", "party.gif", "clap.gif", "wave.gif",
            "sparkling_heart.gif", "surprised.gif", "love.gif", 
            "smiling_face.gif", "joy.gif"
        ]
        
        emoji_list = ", ".join(available_emojis)
        
        prompt = f"""
你是一个贴心的AI助手，需要分析用户当前的专注状态，并给出很懂用户的个性化回应。

专注目标: {focus_goal}
屏幕内容: {visual_description}

请结合用户的专注目标和当前行为，分析专注状态并给出回应。按以下json格式回答：

{{
    "is_focused": [true/false],
    "feedback_message": [结合目标和当前状态，用接地气的语气给用户说一句话],
    "recommended_emoji": [从以下表情中选择最匹配的一个：{emoji_list}],
}}

分析要点：
1. 屏幕内容是否与专注目标直接相关
2. 是否出现明显分心内容（社交媒体、娱乐、游戏等）
3. 工作状态和进度如何
4. 用户目标是什么
5. 响应的feedback可以让 用户感受到 你懂他在做什么/想做什么/目标是什么
6. feedback的语气一定要自然，像一个朋友在聊天一样


只响应json格式，不要返回其他内容。
"""
        return prompt.strip()
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        解析语言模型响应
        
        Args:
            response: 模型响应
            
        Returns:
            Dict[str, Any]: 解析后的结果
        """
        try:
            logger.info(f"解析LLM响应: {response}")
            jsonResult = json.loads(response)
            is_focused = jsonResult["is_focused"]
            feedback = jsonResult["feedback_message"]
            recommended_emoji = jsonResult["recommended_emoji"]
            
            return {
                "is_focused": is_focused,
                "feedback_message": feedback,
                "recommended_emoji": recommended_emoji
            }
        except Exception as e:
            logger.error(f"解析LLM响应失败: {e}")
            return None


# 全局分析器实例
_focus_analyzer = None


def get_focus_analyzer(config: dict = None) -> FocusAnalyzer:
    """
    获取专注分析器实例（单例模式）
    
    Args:
        config: 配置字典
        
    Returns:
        FocusAnalyzer: 专注分析器实例
    """
    global _focus_analyzer
    if _focus_analyzer is None:
        _focus_analyzer = FocusAnalyzer(config)
    return _focus_analyzer
    