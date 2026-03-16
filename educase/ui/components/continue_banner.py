# ui/components/continue_banner.py
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ui.styles.dashboard_theme import FONT


class ContinueBanner(QFrame):
    """
    Градиентный баннер для незаконченной попытки.
    """
    continue_clicked = Signal()

    def __init__(self, case_title: str, module_info: str,
                 progress_pct: int, score_info: str, parent=None):
        super().__init__(parent)
        self.setObjectName("ContinueBanner")
        self.setFixedHeight(110)
        self.setStyleSheet("""
            #ContinueBanner {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                         stop:0 #0052a3, stop:0.6 #0078D4, stop:1 #4DA3E8);
                border-radius: 12px;
            }
        """)

        # Тень
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 120, 212, 90)) # 0.35 opacity
        self.setGraphicsEffect(shadow)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(20)

        # 1. Иконка-заглушка (полупрозрачная)
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(52, 52)
        icon_lbl.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.15);
            border-radius: 14px;
        """)
        icon_layout = QVBoxLayout(icon_lbl)
        # В макете там иконка Resume, можно добавить SVG потом
        main_layout.addWidget(icon_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

        # 2. Инфо блок
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        info_layout.setContentsMargins(0, 0, 0, 0)

        lbl_badge = QLabel("ПРОДОЛЖИТЬ")
        lbl_badge.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.65);
            font-family: "{FONT}";
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.8px;
        """)

        lbl_title = QLabel(case_title)
        lbl_title.setStyleSheet(f"""
            color: #FFFFFF;
            font-family: "{FONT}";
            font-size: 17px;
            font-weight: 800;
        """)

        lbl_subtitle = QLabel(module_info)
        lbl_subtitle.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.65);
            font-family: "{FONT}";
            font-size: 12px;
        """)

        # Прогресс бар
        prog_layout = QHBoxLayout()
        prog_layout.setSpacing(12)
        prog_layout.setContentsMargins(0, 6, 0, 0)

        # Кастомный бар
        bar_bg = QFrame()
        bar_bg.setFixedHeight(4)
        bar_bg.setStyleSheet("background-color: rgba(255, 255, 255, 0.2); border-radius: 2px;")

        bar_fill = QFrame(bar_bg)
        bar_fill.setStyleSheet("background-color: rgba(255, 255, 255, 0.85); border-radius: 2px;")
        bar_fill.resize((300 * progress_pct) // 100, 4) # approximate fill
        # В идеале ширина должна пересчитываться по resizeEvent

        lbl_pct = QLabel(f"{progress_pct}%")
        lbl_pct.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.7);
            font-family: "{FONT}";
            font-size: 11px;
            font-weight: 700;
        """)

        prog_layout.addWidget(bar_bg, 1) # stretch
        prog_layout.addWidget(lbl_pct)

        info_layout.addWidget(lbl_badge)
        info_layout.addWidget(lbl_title)
        info_layout.addWidget(lbl_subtitle)
        info_layout.addLayout(prog_layout)

        main_layout.addLayout(info_layout, 1)

        # 3. Кнопка
        btn = QPushButton("Продолжить")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: #0078D4;
                border: none;
                border-radius: 8px;
                padding: 11px 22px;
                font-family: "{FONT}";
                font-size: 13px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                background-color: #F8F9FA;
            }}
        """)
        btn.clicked.connect(self.continue_clicked)
        main_layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def paintEvent(self, event):
        """Отрисовка декоративных кругов по правому краю."""
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 12)) # 0.05 opacity approx

        w = self.width()
        p.drawEllipse(w - 60, -40, 140, 140)
        p.drawEllipse(w - 180, 40, 100, 100)
