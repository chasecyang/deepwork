#!/usr/bin/env python3
"""
专注功能测试脚本
用于测试专注功能的各个组件
"""
import sys
import os
import asyncio
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.screenshot_manager import ScreenshotManager
from utils.focus_analyzer import FocusAnalyzer
from utils.focus_data import FocusSessionManager

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_screenshot_manager():
    """测试截图管理器"""
    print("🖼️ 测试截图管理器...")
    
    config = {
        "screenshot_quality": 0.7,
        "save_screenshots": True
    }
    
    manager = ScreenshotManager(config)
    
    # 测试截图能力
    success, message = manager.test_screenshot_capability()
    print(f"截图测试: {'✅' if success else '❌'} {message}")
    
    if success:
        # 截取一张测试截图
        screenshot_path = manager.take_screenshot()
        if screenshot_path:
            print(f"测试截图已保存: {screenshot_path}")
            
            # 获取截图信息
            info = manager.get_screenshot_info(screenshot_path)
            if info:
                print(f"截图信息: {info['width']}x{info['height']}, {info['size_mb']}MB")
            
            # 清理测试文件
            # manager.delete_screenshot(screenshot_path)
        else:
            print("❌ 截图失败")
    
    # 获取显示器信息
    display_info = manager.get_display_info()
    print(f"显示器信息: {display_info}")


async def test_focus_analyzer():
    """测试专注分析器"""
    print("\n🧠 测试专注分析器...")
    
    config = {
        "vision_model": {},  # 空配置，将使用模拟分析
        "language_model": {}
    }
    
    analyzer = FocusAnalyzer(config)
    
    # 先获取一张截图
    screenshot_manager = ScreenshotManager()
    screenshot_path = screenshot_manager.take_screenshot()
    
    if screenshot_path:
        print(f"开始分析截图: {screenshot_path}")
        
        # 模拟分析
        result = await analyzer.analyze_focus(screenshot_path, "编程开发")
        
        if result:
            print(f"✅ 分析完成:")
            print(f"  是否专注: {'是' if result.is_focused else '否'}")
            print(f"  反馈消息: {result.feedback_message}")
            print(f"  推荐表情: {result.recommended_emoji}")
            print(f"  分析耗时: {result.analysis_duration:.2f}秒")
        else:
            print("❌ 分析失败")
        
        # 清理测试文件
        screenshot_manager.delete_screenshot(screenshot_path)
    else:
        print("❌ 无法获取测试截图")


def test_focus_session():
    """测试专注会话管理"""
    print("\n📊 测试专注会话管理...")
    
    manager = FocusSessionManager()
    
    # 创建会话
    session = manager.start_session("测试编程任务", 1)  # 1分钟测试
    print(f"✅ 会话已创建: {session.goal}")
    
    # 模拟一些分析结果
    from utils.focus_data import FocusAnalysisResult
    import time
    
    for i in range(3):
        result = FocusAnalysisResult(
            timestamp=time.time(),
            screenshot_path=f"test_{i}.jpg",
            visual_description=f"测试描述 {i}",
            is_focused=True,
            feedback_message=f"测试反馈 {i}",
            recommended_emoji="fire.gif",
            analysis_duration=0.5
        )
        session.add_analysis_result(result)
    
    # 获取会话摘要
    summary = session.get_summary()
    print("会话摘要:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # 完成会话
    manager.end_current_session()
    print("✅ 会话已完成")


async def main():
    """主测试函数"""
    print("🎯 专注功能测试开始\n")
    
    try:
        # 测试各个组件
        test_screenshot_manager()
        await test_focus_analyzer()
        test_focus_session()
        
        print("\n🎉 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())