# ui/components/feedback_panel.py
"""
Панель обратной связи — slide-up уведомление о результате проверки.
Три состояния: correct (зелёный), incorrect (красный), partial (оранжевый).
Премиальный дизайн с плавной анимацией.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsOpacityEffect
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSize
)
from PySide6.QtGui import QFont

from ui.styles.theme import COLORS


class FeedbackPanel(QWidget):
    """
    Панель обратной связи, появляющаяся снизу.
    Показывается один раз и остаётся до явного вызова hide_result()
    или перехода к другому заданию.
    """

    STATES: dict[str, dict] = {
        "correct": {
            "bg": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1B5E20, stop:1 #2E7D32)",
            "icon": "✓",
            "icon_bg": "#4CAF50",
            "title": "Правильно!",
            "border_top": "#4CAF50",
        },
        "incorrect": {
            "bg": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B71C1C, stop:1 #C62828)",
            "icon": "✕",
            "icon_bg": "#EF5350",
            "title": "Неверно",
            "border_top": "#EF5350",
        },
        "partial": {
            "bg": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E65100, stop:1 #EF6C00)",
            "icon": "~",
            "icon_bg": "#FF9800",
            "title": "Частично верно",
            "border_top": "#FF9800",
        },
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._visible = False
        self._target_h = 0
        self._anim_group: QParallelAnimationGroup | None = None
        self.setMaximumHeight(0)
        self.setMinimumHeight(0)
        self._build_ui()

    def _build_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # Внутренний контейнер с padding
        self._inner = QWidget()
        inner_layout = QVBoxLayout(self._inner)
        inner_layout.setContentsMargins(20, 14, 20, 14)
        inner_layout.setSpacing(6)

        # ── Строка 1: иконка + заголовок + баллы ──
        top = QHBoxLayout()
        top.setSpacing(12)

        # Круглая иконка
        self.lbl_icon = QLabel("")
        self.lbl_icon.setFixedSize(32, 32)
        self.lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top.addWidget(self.lbl_icon)

        self.lbl_title = QLabel("")
        self.lbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet("color: white;")
        top.addWidget(self.lbl_title)

        top.addStretch()

        # Баллы в pill-badge
        self.lbl_score = QLabel("")
        self.lbl_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_score.setStyleSheet("""
            color: white;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 4px 12px;
            font-size: 13px;
            font-weight: bold;
        """)
        top.addWidget(self.lbl_score)

        inner_layout.addLayout(top)

        # ── Строка 2: текст обратной связи ──
        self.lbl_feedback = QLabel("")
        self.lbl_feedback.setWordWrap(True)
        self.lbl_feedback.setStyleSheet("""
            color: rgba(255, 255, 255, 0.92);
            font-size: 13px;
            line-height: 1.4;
            padding-left: 44px;
        """)
        inner_layout.addWidget(self.lbl_feedback)

        self._main_layout.addWidget(self._inner)

    @property
    def is_visible(self) -> bool:
        return self._visible

    def show_result(self, state: str, feedback: str = "",
                    score: float = 0, max_score: float = 1,
                    explanation: str = ""):
        """
        Показывает панель с результатом.
        state: 'correct', 'incorrect', 'partial'
        """
        info = self.STATES.get(state, self.STATES["incorrect"])

        # Стиль контейнера
        self._inner.setStyleSheet(f"""
            QWidget {{
                background: {info['bg']};
            }}
        """)

        # Иконка в круге
        self.lbl_icon.setStyleSheet(f"""
            background: {info['icon_bg']};
            color: white;
            border-radius: 16px;
            font-size: 18px;
            font-weight: bold;
            font-family: 'Segoe UI';
        """)
        self.lbl_icon.setText(info["icon"])
        self.lbl_title.setText(info["title"])
        self.lbl_score.setText(f"{score:.1f} / {max_score:.1f}")

        # Текст обратной связи
        text_parts: list[str] = []
        if feedback:
            text_parts.append(feedback)
        if explanation:
            text_parts.append(f"💡 {explanation}")
        full_text = "\n".join(text_parts)
        self.lbl_feedback.setText(full_text)
        self.lbl_feedback.setVisible(bool(full_text))

        # Вычисляем нужную высоту
        self._target_h = 70 + (30 if full_text else 0)

        self._visible = True
        self._animate_show()

    def hide_result(self):
        """Скрывает панель с анимацией."""
        if not self._visible:
            return
        self._visible = False
        self._animate_hide()

    def _animate_show(self):
        """Плавное появление снизу."""
        if self._anim_group:
            self._anim_group.stop()

        anim = QPropertyAnimation(self, b"maximumHeight")
        anim.setDuration(280)
        anim.setStartValue(0)
        anim.setEndValue(self._target_h)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        anim_min = QPropertyAnimation(self, b"minimumHeight")
        anim_min.setDuration(280)
        anim_min.setStartValue(0)
        anim_min.setEndValue(self._target_h)
        anim_min.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(anim)
        group.addAnimation(anim_min)
        group.start()

        self._anim_group = group

    def _animate_hide(self):
        """Плавное схлопывание."""
        if self._anim_group:
            self._anim_group.stop()

        anim = QPropertyAnimation(self, b"maximumHeight")
        anim.setDuration(200)
        anim.setStartValue(self._target_h)
        anim.setEndValue(0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)

        anim_min = QPropertyAnimation(self, b"minimumHeight")
        anim_min.setDuration(200)
        anim_min.setStartValue(self._target_h)
        anim_min.setEndValue(0)
        anim_min.setEasingCurve(QEasingCurve.Type.InCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(anim)
        group.addAnimation(anim_min)
        group.start()

        self._anim_group = group
