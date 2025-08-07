"""
拖拽处理器
负责桌面宠物的拖拽行为
"""
from PySide6.QtCore import Qt, QPoint


class DragHandler:
    """拖拽处理器"""
    
    def __init__(self, widget, window_manager):
        self.widget = widget
        self.window_manager = window_manager
        self.drag_start_position = QPoint()
        self.is_dragging = False
        
    def handle_mouse_press(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_start_position = event.globalPosition().toPoint() - self.widget.pos()
            
    def handle_mouse_move(self, event):
        """处理鼠标移动事件"""
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_start_position
            self.widget.move(new_pos)
            
    def handle_mouse_release(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            # 保存位置
            self.window_manager.save_position()
            
            # 检查是否是简单点击（没有拖拽）
            if self.drag_start_position == event.globalPosition().toPoint() - self.widget.pos():
                return True  # 表示是点击事件
        return False  # 表示是拖拽事件
