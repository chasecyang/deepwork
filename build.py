#!/usr/bin/env python3
"""
Deepwork 应用打包脚本
自动化构建可执行文件
"""

import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_build_dirs():
    """清理之前的构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            logger.info(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 清理.pyc文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def install_dependencies():
    """安装构建依赖"""
    logger.info("检查并安装构建依赖...")
    
    try:
        # 检查是否在虚拟环境中
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.info("检测到虚拟环境")
        else:
            logger.warning("建议在虚拟环境中进行打包")
        
        # 安装依赖
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        logger.info("依赖安装完成")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"依赖安装失败: {e}")
        return False
    
    return True

def build_executable(target_platform=None):
    """使用PyInstaller构建可执行文件"""
    logger.info("开始构建可执行文件...")
    
    try:
        # 使用spec文件构建
        cmd = [sys.executable, '-m', 'PyInstaller', 'deepwork.spec', '--clean']
        
        # 如果指定了目标平台，添加相应参数
        if target_platform:
            if target_platform == 'windows':
                # 注意：在macOS上无法直接编译Windows exe
                logger.warning("在macOS上无法直接编译Windows .exe文件")
                logger.info("建议使用Windows机器或虚拟机进行Windows版本的构建")
            elif target_platform == 'macos':
                cmd.extend(['--target-arch', 'universal2'])  # 支持Intel和Apple Silicon
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        logger.info(f"当前平台: {sys.platform}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        logger.info("构建完成!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"构建失败: {e}")
        if e.stdout:
            logger.error(f"标准输出: {e.stdout}")
        if e.stderr:
            logger.error(f"错误输出: {e.stderr}")
        return False

def post_build_tasks():
    """构建后的处理任务"""
    logger.info("执行构建后任务...")
    
    dist_dir = Path('dist/deepwork')
    
    if not dist_dir.exists():
        logger.error("构建输出目录不存在")
        return False
    
    # 检查可执行文件（根据操作系统选择不同扩展名）
    if os.name == 'nt':  # Windows
        exe_path = dist_dir / 'deepwork.exe'
    else:  # macOS/Linux
        exe_path = dist_dir / 'deepwork'
    
    if exe_path.exists():
        logger.info(f"可执行文件已生成: {exe_path}")
        logger.info(f"文件大小: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    else:
        logger.error("可执行文件未找到")
        # 列出dist目录内容以便调试
        logger.info(f"dist目录内容: {list(dist_dir.iterdir())}")
        return False
    
    # 创建发布文件夹
    release_dir = Path('release')
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    # 复制整个dist目录到release
    shutil.copytree(dist_dir, release_dir)
    logger.info(f"发布文件已复制到: {release_dir}")
    
    # 复制重要文件到发布目录
    important_files = ['README.md', 'config.json', 'docs/']
    for file_path in important_files:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                if not (release_dir / file_path).exists():
                    shutil.copytree(file_path, release_dir / file_path)
            else:
                shutil.copy2(file_path, release_dir)
            logger.info(f"已复制: {file_path}")
    
    logger.info("构建后处理完成!")
    return True

def main():
    """主函数"""
    logger.info("=== Deepwork 应用打包开始 ===")
    logger.info(f"当前操作系统: {sys.platform}")
    
    # 检查是否存在spec文件
    if not os.path.exists('deepwork.spec'):
        logger.error("未找到 deepwork.spec 文件")
        return 1
    
    # 检查命令行参数
    target_platform = None
    if len(sys.argv) > 1:
        target_platform = sys.argv[1].lower()
        if target_platform not in ['windows', 'macos', 'linux']:
            logger.error("无效的目标平台，支持: windows, macos, linux")
            return 1
        logger.info(f"目标平台: {target_platform}")
    
    # 1. 清理构建目录
    clean_build_dirs()
    
    # 2. 安装依赖
    if not install_dependencies():
        logger.error("依赖安装失败，终止构建")
        return 1
    
    # 3. 构建可执行文件
    if not build_executable(target_platform):
        logger.error("构建失败，终止打包")
        return 1
    
    # 4. 构建后处理
    if not post_build_tasks():
        logger.error("构建后处理失败")
        return 1
    
    logger.info("=== Deepwork 应用打包完成 ===")
    exe_name = 'deepwork.exe' if os.name == 'nt' else 'deepwork'
    logger.info(f"可执行文件位置: release/{exe_name}")
    logger.info("完整应用目录: release/")
    
    if sys.platform == 'darwin' and target_platform != 'windows':
        logger.info("\n💡 提示：要构建Windows版本，请在Windows系统上运行:")
        logger.info("   python build.py windows")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())