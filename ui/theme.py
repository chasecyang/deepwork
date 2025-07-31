"""
现代化主题样式系统
提供统一的颜色、字体和样式定义
"""

class ModernTheme:
    """现代化主题类"""
    
    # 颜色定义 - 简约黑白灰配色
    COLORS = {
        # 主色调
        'primary': '#2d2d2d',           # 深灰色
        'primary_hover': '#1a1a1a',     # 深灰色悬停
        'primary_light': '#404040',     # 浅深灰色
        
        # 辅助色
        'secondary': '#6b6b6b',         # 中性灰色
        'accent': '#8a8a8a',           # 浅灰色
        
        # 背景色
        'bg_primary': '#ffffff',        # 主背景
        'bg_secondary': '#f9f9f9',      # 次背景
        'bg_tertiary': '#f0f0f0',       # 第三背景
        'bg_dark': '#1a1a1a',          # 深色背景
        
        # 文本色
        'text_primary': '#1a1a1a',      # 主文本
        'text_secondary': '#4a4a4a',    # 次文本
        'text_muted': '#8a8a8a',       # 弱化文本
        'text_light': '#ffffff',       # 浅色文本
        
        # 边框色
        'border_light': '#e0e0e0',     # 浅边框
        'border_medium': '#c0c0c0',     # 中等边框
        'border_dark': '#4a4a4a',       # 深边框
        
        # 状态色
        'success': '#2d5a2d',          # 成功 (深绿色)
        'warning': '#8a7c00',          # 警告 (深黄色)  
        'error': '#8a2d2d',            # 错误 (深红色)
        'info': '#2d5a8a',             # 信息 (深蓝色)
        
        # 特殊效果
        'shadow': 'rgba(0, 0, 0, 0.1)', # 阴影
        'overlay': 'rgba(0, 0, 0, 0.5)', # 遮罩
    }
    
    # 字体定义
    FONTS = {
        'size_xs': '10px',
        'size_sm': '12px',
        'size_base': '14px',
        'size_lg': '16px',
        'size_xl': '18px',
        'size_2xl': '20px',
        'size_3xl': '24px',
        
        'weight_light': '300',
        'weight_normal': '400',
        'weight_medium': '500',
        'weight_semibold': '600',
        'weight_bold': '700',
        
        'family_sans': '"Microsoft YaHei", "PingFang SC", "Segoe UI", Roboto, sans-serif',
        'family_mono': '"JetBrains Mono", "SF Mono", Consolas, monospace',
    }
    
    # 间距定义
    SPACING = {
        'xs': '4px',
        'sm': '8px',
        'base': '12px',
        'lg': '16px',
        'xl': '20px',
        '2xl': '24px',
        '3xl': '32px',
        '4xl': '40px',
    }
    
    # 圆角定义
    RADIUS = {
        'none': '0',
        'sm': '6px',
        'base': '8px',
        'lg': '12px',
        'xl': '16px',
        'full': '9999px',
    }
    
    # 阴影定义
    SHADOWS = {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'base': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    }
    
    @classmethod
    def get_dialog_style(cls):
        """获取对话框样式"""
        return f"""
        QDialog {{
            background: {cls.COLORS['bg_primary']};
            border: 1px solid {cls.COLORS['border_light']};
            border-radius: {cls.RADIUS['lg']};
            font-family: {cls.FONTS['family_sans']};
            font-size: {cls.FONTS['size_base']};
            color: {cls.COLORS['text_primary']};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {cls.COLORS['border_light']};
            border-radius: {cls.RADIUS['base']};
            background-color: {cls.COLORS['bg_primary']};
            margin-top: -1px;
        }}
        
        QTabBar::tab {{
            background: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_secondary']};
            padding: {cls.SPACING['base']} {cls.SPACING['lg']};
            margin-right: 2px;
            border-top-left-radius: {cls.RADIUS['base']};
            border-top-right-radius: {cls.RADIUS['base']};
            border: 1px solid {cls.COLORS['border_light']};
            border-bottom: none;
            font-weight: {cls.FONTS['weight_medium']};
            min-width: 70px;
            font-size: {cls.FONTS['size_base']};
        }}
        
        QTabBar::tab:selected {{
            background: {cls.COLORS['bg_primary']};
            color: {cls.COLORS['primary']};
            border-color: {cls.COLORS['border_light']};
            font-weight: {cls.FONTS['weight_semibold']};
        }}
        
        QTabBar::tab:hover:!selected {{
            background: {cls.COLORS['bg_tertiary']};
            color: {cls.COLORS['text_primary']};
        }}
        
        QGroupBox {{
            font-weight: {cls.FONTS['weight_semibold']};
            border: 1px solid {cls.COLORS['border_light']};
            border-radius: {cls.RADIUS['base']};
            margin-top: {cls.SPACING['base']};
            padding-top: {cls.SPACING['base']};
            background-color: {cls.COLORS['bg_secondary']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {cls.SPACING['lg']};
            padding: 0 {cls.SPACING['sm']} 0 {cls.SPACING['sm']};
            color: {cls.COLORS['text_primary']};
            background-color: {cls.COLORS['bg_primary']};
            border-radius: {cls.RADIUS['sm']};
        }}
        
        QLabel {{
            color: {cls.COLORS['text_primary']};
            font-weight: {cls.FONTS['weight_medium']};
        }}
        
        QLineEdit {{
            border: 2px solid {cls.COLORS['border_light']};
            border-radius: {cls.RADIUS['base']};
            padding: {cls.SPACING['sm']} {cls.SPACING['lg']};
            background-color: {cls.COLORS['bg_primary']};
            font-size: {cls.FONTS['size_base']};
            color: {cls.COLORS['text_primary']};
            selection-background-color: {cls.COLORS['primary_light']};
            min-height: 16px;
        }}
        
        QLineEdit:focus {{
            border-color: {cls.COLORS['primary']};
            background-color: {cls.COLORS['bg_primary']};
        }}
        
        QLineEdit:hover {{
            border-color: {cls.COLORS['border_medium']};
        }}
        
        QCheckBox {{
            color: {cls.COLORS['text_primary']};
            font-weight: {cls.FONTS['weight_medium']};
            spacing: {cls.SPACING['base']};
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {cls.COLORS['border_medium']};
            border-radius: {cls.RADIUS['sm']};
            background-color: {cls.COLORS['bg_primary']};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {cls.COLORS['primary']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {cls.COLORS['primary']};
            border-color: {cls.COLORS['primary']};
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }}
        
        QSlider::groove:horizontal {{
            border: none;
            height: 6px;
            background: {cls.COLORS['bg_tertiary']};
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background: {cls.COLORS['primary']};
            border: 2px solid {cls.COLORS['bg_primary']};
            width: 20px;
            height: 20px;
            margin: -9px 0;
            border-radius: 11px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {cls.COLORS['primary_hover']};
        }}
        
        QSlider::sub-page:horizontal {{
            background: {cls.COLORS['primary']};
            border-radius: 3px;
        }}
        
        QPushButton {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text_light']};
            border: none;
            border-radius: {cls.RADIUS['base']};
            padding: {cls.SPACING['sm']} {cls.SPACING['lg']};
            font-weight: {cls.FONTS['weight_semibold']};
            font-size: {cls.FONTS['size_base']};
            min-width: 60px;
            min-height: 28px;
        }}
        
        QPushButton:hover {{
            background-color: {cls.COLORS['primary_hover']};
            color: {cls.COLORS['text_light']};
        }}
        
        QPushButton:pressed {{
            background-color: {cls.COLORS['primary_hover']};
            color: {cls.COLORS['text_light']};
        }}
        
        QPushButton:default {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text_light']};
            border: 2px solid {cls.COLORS['primary']};
        }}
        
        QPushButton:default:hover {{
            background-color: {cls.COLORS['primary_hover']};
            color: {cls.COLORS['text_light']};
            border-color: {cls.COLORS['primary_hover']};
        }}
        
        QPushButton:flat {{
            background-color: transparent;
            color: {cls.COLORS['text_secondary']};
            border: 1px solid {cls.COLORS['border_light']};
        }}
        
        QPushButton:flat:hover {{
            background-color: {cls.COLORS['bg_secondary']};
            color: {cls.COLORS['text_primary']};
            border-color: {cls.COLORS['border_medium']};
        }}
        
        QPushButton:disabled {{
            background-color: {cls.COLORS['bg_tertiary']};
            color: {cls.COLORS['text_muted']};
            border: 1px solid {cls.COLORS['border_light']};
        }}
        """
    
    @classmethod
    def get_menu_style(cls):
        """获取菜单样式"""
        return f"""
        QMenu {{
            background: {cls.COLORS['bg_primary']};
            border: 1px solid {cls.COLORS['border_light']};
            border-radius: {cls.RADIUS['lg']};
            padding: {cls.SPACING['base']};
            font-family: {cls.FONTS['family_sans']};
            font-size: {cls.FONTS['size_base']};
        }}
        
        QMenu::item {{
            padding: {cls.SPACING['base']} {cls.SPACING['xl']};
            border-radius: {cls.RADIUS['base']};
            color: {cls.COLORS['text_primary']};
            font-weight: {cls.FONTS['weight_medium']};
            margin: 2px;
        }}
        
        QMenu::item:selected {{
            background: {cls.COLORS['bg_tertiary']};
            color: {cls.COLORS['text_primary']};
        }}
        
        QMenu::item:pressed {{
            background: {cls.COLORS['primary_hover']};
        }}
        
        QMenu::separator {{
            height: 1px;
            background: {cls.COLORS['border_light']};
            margin: {cls.SPACING['base']} {cls.SPACING['lg']};
        }}
        
        QMenu::icon {{
            padding-left: {cls.SPACING['base']};
        }}
        """
    
    @classmethod
    def get_tooltip_style(cls):
        """获取工具提示样式"""
        return f"""
        QToolTip {{
            background: {cls.COLORS['bg_dark']};
            color: {cls.COLORS['text_light']};
            border: 1px solid {cls.COLORS['border_dark']};
            border-radius: {cls.RADIUS['base']};
            padding: {cls.SPACING['base']} {cls.SPACING['lg']};
            font-size: {cls.FONTS['size_sm']};
            font-weight: {cls.FONTS['weight_medium']};
        }}
        """

class DarkTheme(ModernTheme):
    """深色主题变体"""
    
    COLORS = {
        **ModernTheme.COLORS,
        
        # 深色主题颜色覆盖
        'bg_primary': '#0f172a',        # 深色主背景
        'bg_secondary': '#1e293b',      # 深色次背景
        'bg_tertiary': '#334155',       # 深色第三背景
        
        'text_primary': '#f8fafc',      # 深色主文本
        'text_secondary': '#cbd5e1',    # 深色次文本
        'text_muted': '#64748b',       # 深色弱化文本
        
        'border_light': '#334155',     # 深色浅边框
        'border_medium': '#475569',     # 深色中等边框
    }