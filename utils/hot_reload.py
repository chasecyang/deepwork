"""
热重载模块
监控Python文件变化并自动重启应用程序
"""
import os
import sys
import subprocess
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PySide6.QtCore import QThread, Signal, QObject


class FileChangeHandler(FileSystemEventHandler):
    """文件变化处理器"""
    
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.last_modified = {}
        self.ignore_patterns = {'.pyc', '__pycache__', '.git', '.vscode', 'config.json'}
        
    def should_ignore(self, file_path):
        """检查是否应该忽略文件"""
        path_str = str(file_path)
        
        # 忽略特定模式的文件和目录
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True
                
        # 只监控Python文件
        if not path_str.endswith('.py'):
            return True
            
        return False
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        
        # 检查是否应该忽略
        if self.should_ignore(file_path):
            return
            
        # 防止重复触发
        current_time = time.time()
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < 1.0:  # 1秒内的重复修改忽略
                return
                
        self.last_modified[file_path] = current_time
        
        print(f"检测到文件变化: {file_path}")
        self.callback(file_path)


class HotReloadThread(QThread):
    """热重载线程"""
    
    reload_signal = Signal(str)  # 发出重载信号
    
    def __init__(self, watch_paths=None, parent=None):
        super().__init__(parent)
        self.watch_paths = watch_paths or [os.getcwd()]
        self.observer = None
        self.is_running = False
        
    def run(self):
        """运行热重载监控"""
        try:
            self.observer = Observer()
            handler = FileChangeHandler(self.on_file_changed)
            
            # 监控指定路径
            for path in self.watch_paths:
                if os.path.exists(path):
                    self.observer.schedule(handler, path, recursive=True)
                    print(f"开始监控目录: {path}")
                    
            self.observer.start()
            self.is_running = True
            
            # 保持线程运行
            while self.is_running:
                self.msleep(100)
                
        except Exception as e:
            print(f"热重载监控出错: {e}")
        finally:
            if self.observer:
                self.observer.stop()
                
    def on_file_changed(self, file_path):
        """文件变化回调"""
        self.reload_signal.emit(file_path)
        
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()


class HotReloader(QObject):
    """热重载管理器"""
    
    def __init__(self, app, config_manager, parent=None):
        super().__init__(parent)
        self.app = app
        self.config = config_manager
        self.thread = None
        self.enabled = self.config.get("hot_reload_enabled", False)
        self.reload_delay = self.config.get("hot_reload_delay", 1.0)  # 重载延迟（秒）
        
    def start(self):
        """启动热重载"""
        if not self.enabled:
            return
            
        if self.thread and self.thread.isRunning():
            return
            
        # 确定监控路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        watch_paths = [
            project_root,  # 项目根目录
        ]
        
        # 创建并启动监控线程
        self.thread = HotReloadThread(watch_paths)
        self.thread.reload_signal.connect(self.on_reload_requested)
        self.thread.start()
        
        print("热重载已启动")
        
    def stop(self):
        """停止热重载"""
        if self.thread:
            self.thread.stop_monitoring()
            self.thread.wait()
            self.thread = None
        print("热重载已停止")
        
    def on_reload_requested(self, file_path):
        """处理重载请求"""
        print(f"准备重载应用程序（触发文件: {file_path}）...")
        
        # 延迟一下再重载，确保文件写入完成
        self.thread.msleep(int(self.reload_delay * 1000))
        
        # 重启应用程序
        self.restart_application()
        
    def restart_application(self):
        """重启应用程序"""
        try:
            print("正在重启应用程序...")
            
            # 保存当前窗口位置等信息
            if hasattr(self.app, 'pet') and self.app.pet:
                pos = self.app.pet.pos()
                self.config.set("window_x", pos.x())
                self.config.set("window_y", pos.y())
            
            # 停止热重载监控
            self.stop()
            
            # 获取当前Python解释器和脚本路径
            python_executable = sys.executable
            script_path = sys.argv[0]
            
            # 启动新进程
            subprocess.Popen([python_executable, script_path] + sys.argv[1:])
            
            # 退出当前进程
            self.app.quit()
            
        except Exception as e:
            print(f"重启应用程序失败: {e}")
            
    def toggle_enabled(self, enabled):
        """切换热重载开关"""
        self.enabled = enabled
        self.config.set("hot_reload_enabled", enabled)
        
        if enabled:
            self.start()
        else:
            self.stop()
            
    def set_delay(self, delay):
        """设置重载延迟"""
        self.reload_delay = delay
        self.config.set("hot_reload_delay", delay)