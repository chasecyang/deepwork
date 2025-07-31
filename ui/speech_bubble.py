"""
对话气泡组件
为桌面助手提供可爱的对话气泡功能
"""
import logging
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QPainter, QPainterPath, QColor, QFont, QFontMetrics

logger = logging.getLogger(__name__)


class SpeechBubble(QWidget):
    """对话气泡组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 气泡样式配置
        self.bubble_color = QColor(255, 255, 255, 240)  # 白色背景，略透明
        self.text_color = QColor(60, 60, 60)  # 深灰色文字
        self.border_color = QColor(200, 200, 200, 150)  # 淡灰色边框
        self.shadow_color = QColor(0, 0, 0, 50)  # 阴影
        
        # 气泡参数
        self.border_radius = 15
        self.tail_size = 10
        self.padding = 15
        self.max_width = 200
        
        # 文本
        self.text = ""
        self.font = QFont("Microsoft YaHei", 10)
        
        # 动画
        self.show_animation = None
        self.hide_animation = None
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide_bubble)
        
        self.setFixedSize(250, 80)  # 初始大小
        self.hide()
        
    def set_text(self, text: str):
        """设置气泡文本"""
        logger.info(f"set_text: 接收到text='{text}', 类型={type(text)}")
        self.text = text
        logger.info(f"设置后: self.text='{self.text}'")
        self._update_size()
        logger.info(f"尺寸更新后: size={self.size()}")
        self.update()
        logger.info("update()调用完成")
        
    def _update_size(self):
        """根据文本内容更新气泡大小"""
        if not self.text:
            return
            
        font_metrics = QFontMetrics(self.font)
        
        # 计算文本所需的大小
        text_rect = font_metrics.boundingRect(
            0, 0, self.max_width - 2 * self.padding, 1000,
            Qt.TextFlag.TextWordWrap, self.text
        )
        
        # 计算气泡总大小（包含尾巴和内边距）
        bubble_width = min(text_rect.width() + 2 * self.padding, self.max_width)
        bubble_height = text_rect.height() + 2 * self.padding + self.tail_size
        
        self.setFixedSize(int(bubble_width), int(bubble_height))
        
    def show_bubble(self, text: str, duration: int = 3000, position: str = "top"):
        """
        显示气泡
        
        Args:
            text: 要显示的文本
            duration: 显示持续时间（毫秒），0表示不自动隐藏
            position: 气泡位置，"top"或"bottom"
        """
        logger.info(f"SpeechBubble.show_bubble: text='{text}', duration={duration}")
        
        self.set_text(text)
        logger.info(f"文本设置完成: self.text='{self.text}', 长度={len(self.text) if self.text else 0}")
        
        # 定位气泡位置
        if self.parent_widget:
            self._position_bubble(position)
            logger.info(f"气泡位置: {self.pos()}")
        else:
            logger.warning("没有parent_widget，无法定位气泡")
        
        # 停止之前的动画
        if self.show_animation:
            self.show_animation.stop()
        if self.hide_animation:
            self.hide_animation.stop()
            
        # 停止自动隐藏定时器
        self.auto_hide_timer.stop()
        
        # 显示动画
        self.setWindowOpacity(0)
        self.show()
        logger.info(f"调用show()后: visible={self.isVisible()}, size={self.size()}")
        
        self.show_animation = QPropertyAnimation(self, b"windowOpacity")
        self.show_animation.setDuration(300)
        self.show_animation.setStartValue(0)
        self.show_animation.setEndValue(1)
        self.show_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.show_animation.start()
        logger.info("动画已启动")
        
        # 设置自动隐藏
        if duration > 0:
            self.auto_hide_timer.start(duration)
            logger.info(f"自动隐藏定时器已设置: {duration}ms")
        
    def hide_bubble(self):
        """隐藏气泡"""
        if not self.isVisible():
            return
            
        # 停止显示动画
        if self.show_animation:
            self.show_animation.stop()
            
        # 停止自动隐藏定时器
        self.auto_hide_timer.stop()
        
        # 隐藏动画
        self.hide_animation = QPropertyAnimation(self, b"windowOpacity")
        self.hide_animation.setDuration(300)
        self.hide_animation.setStartValue(self.windowOpacity())
        self.hide_animation.setEndValue(0)
        self.hide_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.hide_animation.finished.connect(self.hide)
        self.hide_animation.start()
        
        logger.debug("隐藏对话气泡")
        
    def _position_bubble(self, position: str):
        """定位气泡位置"""
        if not self.parent_widget:
            return
            
        parent_rect = self.parent_widget.geometry()
        bubble_width = self.width()
        bubble_height = self.height()
        
        # 计算水平位置（居中）
        x = parent_rect.x() + (parent_rect.width() - bubble_width) // 2
        
        # 计算垂直位置
        if position == "top":
            # 在宠物上方
            y = parent_rect.y() - bubble_height - 10
        else:  # bottom
            # 在宠物下方
            y = parent_rect.y() + parent_rect.height() + 10
            
        # 确保气泡不会超出屏幕
        screen = self.screen()
        if screen:
            screen_rect = screen.availableGeometry()
            x = max(0, min(x, screen_rect.width() - bubble_width))
            y = max(0, min(y, screen_rect.height() - bubble_height))
        
        self.move(x, y)
        
    def paintEvent(self, event):
        """绘制气泡"""
        logger.info(f"paintEvent: self.text='{self.text}', visible={self.isVisible()}")
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制气泡背景
        self._draw_bubble_background(painter)
        
        # 绘制文本
        self._draw_text(painter)
        logger.info("paintEvent完成")
        
    def _draw_bubble_background(self, painter):
        """绘制气泡背景"""
        # 创建气泡路径
        bubble_rect = self.rect().adjusted(5, 5, -5, -self.tail_size - 5)
        
        path = QPainterPath()
        path.addRoundedRect(bubble_rect, self.border_radius, self.border_radius)
        
        # 添加尾巴（指向宠物）
        tail_center_x = bubble_rect.center().x()
        tail_bottom_y = bubble_rect.bottom()
        tail_tip_y = tail_bottom_y + self.tail_size
        
        tail_path = QPainterPath()
        tail_path.moveTo(tail_center_x - self.tail_size // 2, tail_bottom_y)
        tail_path.lineTo(tail_center_x + self.tail_size // 2, tail_bottom_y)
        tail_path.lineTo(tail_center_x, tail_tip_y)
        tail_path.closeSubpath()
        
        path.addPath(tail_path)
        
        # 绘制阴影
        shadow_path = QPainterPath(path)
        shadow_path.translate(2, 2)
        painter.fillPath(shadow_path, self.shadow_color)
        
        # 绘制边框
        painter.strokePath(path, self.border_color)
        
        # 填充背景
        painter.fillPath(path, self.bubble_color)
        
    def _draw_text(self, painter):
        """绘制文本"""
        logger.info(f"_draw_text: self.text='{self.text}', 长度={len(self.text) if self.text else 0}")
        if not self.text:
            logger.info("文本为空，跳过绘制")
            return
            
        painter.setFont(self.font)
        painter.setPen(self.text_color)
        
        # 文本区域（扣除内边距和尾巴）
        text_rect = self.rect().adjusted(
            self.padding, self.padding,
            -self.padding, -self.padding - self.tail_size
        )
        
        logger.info(f"绘制文本到区域: {text_rect}, 文本: '{self.text}'")
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            self.text
        )
        logger.info("文本绘制完成")
        
    def mousePressEvent(self, event):
        """点击气泡隐藏"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.hide_bubble()
        super().mousePressEvent(event)