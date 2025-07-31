# -*- mode: python ; coding: utf-8 -*-
"""
桌面宠物应用 PyInstaller 配置文件
用于打包成独立的可执行文件
"""

import os
import sys
from pathlib import Path

# 添加必要的隐藏导入
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'openai',
    'PIL',
    'PIL.Image',
    'watchdog',
    'watchdog.observers',
    'watchdog.events',
]

# 收集数据文件
datas = [
    ('assets', 'assets'),  # 包含所有资源文件
    ('config.json', '.'),  # 配置文件
    ('docs', 'docs'),      # 文档文件
]

# 收集二进制文件（如果有的话）
binaries = []

a = Analysis(
    ['main.py'],
    pathex=[os.getcwd()],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',  # 排除不需要的tkinter
        'matplotlib',  # 排除matplotlib减小体积
        'numpy',    # 如果不需要numpy也可以排除
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='deepwork',  # 应用名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 改为窗口应用，不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='deepwork',  # 应用名称
)
