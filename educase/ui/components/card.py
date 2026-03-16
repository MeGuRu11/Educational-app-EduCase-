# ui/components/card.py
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QVariantAnimation
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QVBoxLayout, QWidget

from ui.styles.theme import ANIM, COLORS, RADIUS


class Card(QWidget):
    """
    Базовый виджет-карточка со скругленными углами, обводкой и тенью.
    Опционально поддерживает эффект увеличения (поднятия) при наведении.
    """
    def __init__(self, parent=None, hover_effect: bool = False):
        super().__init__(parent)
        self.hover_effect = hover_effect
        self._bg_color = QColor(COLORS["bg_elevated"])
        self._border_color = QColor(0, 0, 0, 20) # stroke_card
        self._elevation = 0.0 # 0.0 to 1.0 (зависит от hover)

        self._setup_shadow()

        # Для анимации смены стилей при наведении
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(ANIM["fast"])
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.valueChanged.connect(self._on_anim_value_changed)

        # Выставляем layout, чтобы потомки не прилипали к краям
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)

    def _setup_shadow(self):
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(12)
        self.shadow.setColor(QColor(0, 0, 0, 20)) # Очень лёгкая тень по умолчанию
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)

    def _on_anim_value_changed(self, value):
        # value is float between 0.0 and 1.0
        self._elevation = value

        # Обновляем тень
        blur = 12 + (12 * value) # blur: 12 -> 24
        offset_y = 2 + (4 * value) # offset_y: 2 -> 6
        alpha = 20 + (10 * value) # alpha: 20 -> 30

        self.shadow.setBlurRadius(blur)
        self.shadow.setOffset(0, offset_y)
        self.shadow.setColor(QColor(0, 0, 0, int(alpha)))

        # Перерисовываем виджет (чтобы обновить border)
        self.update()

    def enterEvent(self, event):
        if self.hover_effect:
            self.anim.setDirection(QPropertyAnimation.Direction.Forward)
            self.anim.setStartValue(self._elevation)
            self.anim.setEndValue(1.0)
            self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.hover_effect:
            self.anim.setDirection(QPropertyAnimation.Direction.Backward)
            self.anim.setStartValue(0.0)
            self.anim.setEndValue(self._elevation)
            self.anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        rect = self.rect().adjusted(1, 1, -1, -1) # adjust for border thickness
        path.addRoundedRect(rect, RADIUS["card"], RADIUS["card"])

        p.fillPath(path, self._bg_color)

        # Меняем цвет обводки при наведении
        if self.hover_effect and self._elevation > 0:
            # Смешиваем stroke_card и accent
            r1, g1, b1, _ = self._border_color.getRgb()
            accent = QColor(COLORS["accent"])
            r2, g2, b2, _ = accent.getRgb()

            w = self._elevation
            r = int(r1 * (1-w) + r2 * w)
            g = int(g1 * (1-w) + g2 * w)
            b = int(b1 * (1-w) + b2 * w)
            pen_color = QColor(r, g, b)
        else:
            pen_color = self._border_color

        p.setPen(pen_color)
        p.drawPath(path)
