"""
桌面宠物主程序
一个简单可爱的桌面宠物应用 - PySide6版本
"""
import sys
import os
import logging

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from config.config import Config
from ui.desktop_pet import DesktopPet

# 导入工具类
from utils.common import LogUtils

# 配置日志
LogUtils.suppress_third_party_logs()
logger = LogUtils.setup_logger(__name__)



def main():
    """主函数"""
    try:
        # 创建QApplication实例
        app = QApplication(sys.argv)
        
        # 设置应用程序信息
        app.setApplicationName("Deepwork")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("Deepwork")
        
        # 初始化配置管理器
        config_manager = Config()
        
        # 创建桌宠
        logger.info("桌面助手启动中...")
        pet = DesktopPet(config_manager)
        
        # 输出启动信息
        print("🐾 桌面助手启动完成!")
        print("🌟 正在唤醒助手...")
        print("💡 使用提示:")
        print("  • 点击助手进行互动")
        print("  • 右键打开设置菜单")
        print("  • 拖拽可移动位置")
        print("  • 助手将自动检测AI配置状态")
        
        # 显示宠物窗口
        pet.show()
        
        # 运行主循环
        sys.exit(app.exec())
        
    except KeyboardInterrupt:
        logger.info("用户中断，程序退出")
        print("\n用户中断，程序退出")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("桌面宠物已退出")
        print("桌面宠物已退出")


if __name__ == "__main__":
    main()