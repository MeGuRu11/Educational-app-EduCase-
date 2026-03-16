# ui/components/ring_progress.py
from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.styles.dashboard_theme import FONT


class _RingCanvas(QWidget):
    """Кастомный виджет рисующий дугу."""
    def __init__(self, target_pct: int, parent=None):
        super().__init__(parent)
        self.setFixedSize(140, 140)
        self._target = target_pct
        self._current_value = 0.0

        if target_pct >= 75:
            self.arc_color = QColor("#4ee87a")
        elif target_pct >= 60:
            self.arc_color = QColor("#F59E0B")
        else:
            self.arc_color = QColor("#C42B1C")

        self.anim = QPropertyAnimation(self, b"arc_value", self)
        self.anim.setDuration(1200)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(float(target_pct))
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuart)

    def start_animation(self):
        self.anim.start()

    def get_arc_value(self) -> float:
        return self._current_value

    def set_arc_value(self, val: float):
        self._current_value = val
        self.update()

    arc_value = Property(float, get_arc_value, set_arc_value)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = QRectF(7, 7, 126, 126) # 140-14=126

        # Фоновое кольцо
        bg_pen = QPen(QColor(255, 255, 255, 20)) # 0.08
        bg_pen.setWidth(14)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(bg_pen)
        p.drawArc(r, 0, 360 * 16)

        # Дуга значения
        if self._current_value > 0:
            val_pen = QPen(self.arc_color)
            val_pen.setWidth(14)
            val_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(val_pen)

            # Qt angles are in 1/16ths of a degree, starting at 3 o'clock
            # We want to start at 12 o'clock (90 deg) and go clockwise (- direction)
            start_angle = 90 * 16
            span_angle = int(- (self._current_value / 100.0) * 360 * 16)
            p.drawArc(r, start_angle, span_angle)

        # Текст в центре
        p.setPen(self.arc_color)
        p.setFont(QFont(FONT, 28, QFont.Weight.ExtraBold))
        text_val = str(int(self._current_value))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text_val)

        p.setPen(QColor(255, 255, 255, 115)) # 0.45
        p.setFont(QFont(FONT, 9, QFont.Weight.Bold))
        # Сдвиг вниз
        r2 = QRectF(0, 30, self.width(), self.height())
        p.drawText(r2, Qt.AlignmentFlag.AlignCenter, "БАЛЛ")


class RingProgress(QFrame):
    def __init__(self, score_pct: int, case_title: str,
                 subtitle: str, modules: list[tuple[str, int]], parent=None):
        super().__init__(parent)
        self.setObjectName("RingProgress")
        self.setFixedHeight(180)
        self.setStyleSheet("""
            #RingProgress {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                         stop:0 #0D1B2E, stop:1 #0a2040);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.06);
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(32)

        # 1. Canvas дуги
        self.canvas = _RingCanvas(score_pct)
        main_layout.addWidget(self.canvas)

        # 2. Инфо справа
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0,0,0,0)
        info_layout.setSpacing(4)

        lbl_wrapper = QHBoxLayout()
        # Оценка
        grade = "2"
        if score_pct >= 85: grade = "5"
        elif score_pct >= 75: grade = "4"
        elif score_pct >= 60: grade = "3"

        grade_lbl = QLabel(f"● Оценка {grade}")
        color_hex = self.canvas.arc_color.name()
        grade_lbl.setStyleSheet(f"""
            background-color: rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 4px 12px;
            color: {color_hex};
            font-family: "{FONT}";
            font-size: 11px;
            font-weight: 700;
        """)
        lbl_wrapper.addWidget(grade_lbl)
        lbl_wrapper.addStretch()

        title_lbl = QLabel(case_title)
        title_lbl.setStyleSheet(f"""color: white; font-family: "{FONT}"; font-size: 18px; font-weight: 800;""")

        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet(f"""color: rgba(255,255,255,0.45); font-family: "{FONT}"; font-size: 12px;""")

        info_layout.addLayout(lbl_wrapper)
        info_layout.addWidget(title_lbl)
        info_layout.addWidget(sub_lbl)
        info_layout.addSpacing(6)

        # Модули (progress bars)
        for mod_name, mod_pct in modules[:3]: # макс 3
            row = QHBoxLayout()
            m_lbl = QLabel(mod_name)
            m_lbl.setStyleSheet(f"""color: rgba(255,255,255,0.6); font-family: "{FONT}"; font-size: 11px;""")

            p_bg = QFrame()
            p_bg.setFixedSize(60, 4)
            p_bg.setStyleSheet("background-color: rgba(255,255,255,0.1); border-radius: 2px;")
            p_fill = QFrame(p_bg)
            p_fill.setStyleSheet("background-color: #4DA3E8; border-radius: 2px;")
            p_fill.resize((60 * mod_pct) // 100, 4)

            p_lbl = QLabel(f"{mod_pct}%")
            p_lbl.setStyleSheet(f"""color: rgba(255,255,255,0.8); font-family: "{FONT}"; font-size: 10px; font-weight: 700;""")

            row.addWidget(m_lbl, 1)
            row.addWidget(p_bg, 0, Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(p_lbl)
            info_layout.addLayout(row)

        info_layout.addStretch()
        main_layout.addLayout(info_layout, 1)

    def showEvent(self, event):
        super().showEvent(event)
        self.canvas.start_animation()
