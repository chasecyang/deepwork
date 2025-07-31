#!/usr/bin/env python3
"""
开发模式启动脚本
直接启用热重载功能，方便开发调试
"""
import os
import sys
import logging

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志 - 开发模式使用INFO级别，避免第三方库的调试信息
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 设置第三方库的日志级别为WARNING，避免过多调试信息
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

from PySide6.QtWidgets import QApplication
from config.config import Config
from ui.desktop_pet import DesktopPet
from utils.hot_reload import HotReloader

def main():
    """开发模式主函数"""
    print("🚀 开发模式启动中...")
    print("📁 监控目录: 项目根目录")
    print("🔄 热重载延迟: 1.0 秒")
    print("📝 日志级别: DEBUG (详细日志输出)")
    print("⚠️  注意: 修改任何Python文件将自动重启应用")
    print("---")
    
    try:
        # 创建QApplication实例
        app = QApplication(sys.argv)
        
        # 设置应用程序信息
        app.setApplicationName("桌面宠物 (开发模式)")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("DesktopPet")
        
        # 初始化配置管理器
        config_manager = Config()
        
        # 创建桌宠
        pet = DesktopPet(config_manager)
        
        # 初始化并启动热重载功能
        hot_reloader = HotReloader(app, config_manager)
        hot_reloader.enabled = True  # 直接启用，不依赖配置
        hot_reloader.reload_delay = 1.0
        app.hot_reloader = hot_reloader
        app.pet = pet
        
        print("桌面宠物启动中...")
        print("右键点击宠物可以打开设置菜单")
        print("拖拽宠物可以移动位置")
        print("🔥 热重载功能已启用")
        
        # 启动热重载
        hot_reloader.start()
        
        # 显示宠物窗口
        pet.show()
        
        # 运行主循环
        sys.exit(app.exec())
        
    except KeyboardInterrupt:
        print("\n🛑 开发模式已停止")
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("开发模式已退出")

if __name__ == "__main__":
    main()