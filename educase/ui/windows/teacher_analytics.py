# ui/windows/teacher_analytics.py
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.components.common import CardFrame, ScorePill
from ui.components.heatmap_widget import HeatmapWidget
from ui.components.stat_card import StatCard
from ui.components.weak_tasks_list import WeakTasksList
from ui.styles.chart_style import apply_dashboard_style
from ui.styles.dashboard_theme import COLORS, FONT


class TeacherAnalytics(QWidget):
    """Экран T-6: Аналитика"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TeacherAnalytics")
        self.setStyleSheet(f"background-color: {COLORS['bg']};")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 40)
        main_layout.setSpacing(24)

        # 1. Header & Filters
        head_l = QHBoxLayout()
        title = QLabel("Углубленная аналитика")
        title.setStyleSheet(f"color: {COLORS['t1']}; font-family: '{FONT}'; font-size: 24px; font-weight: 800;")
        head_l.addWidget(title)

        filter_l = QHBoxLayout()
        filter_l.setSpacing(10)

        for p in ["Все группы", "Все кейсы", "За 30 дней"]:
            cb = QComboBox()
            cb.addItem(p)
            cb.setStyleSheet(self._combo_style())
            filter_l.addWidget(cb)

        head_l.addStretch()
        head_l.addLayout(filter_l)

        # Export buttons
        btn_pdf = QPushButton("PDF отчёт")
        btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pdf.setStyleSheet(self._btn_ghost_style())

        btn_ex = QPushButton("Excel")
        btn_ex.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ex.setStyleSheet(self._btn_ghost_style())

        head_l.addSpacing(20)
        head_l.addWidget(btn_pdf)
        head_l.addWidget(btn_ex)

        main_layout.addLayout(head_l)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(24)

        # 2. Stat Row
        stat_row = QHBoxLayout()
        stat_row.setSpacing(16)
        stat_row.addWidget(StatCard("СР. БАЛЛ", "72.4%", "", "neutral"))
        stat_row.addWidget(StatCard("ЗАВЕРШИЛИ", "85%", "24/28 студ.", "neutral", accent_color=COLORS["success"]))
        stat_row.addWidget(StatCard("СР. ВРЕМЯ", "14м 20с", "", "neutral", accent_color="#F59E0B"))
        stat_row.addWidget(StatCard("ЛУЧШИЙ", "100%", "Иванов И.", "neutral", accent_color=COLORS["accent_light"]))
        c_layout.addLayout(stat_row)

        # 3. Middle Grid (Heatmap + DistChart)
        mid_grid = QHBoxLayout()
        mid_grid.setSpacing(20)

        hm_card = CardFrame()
        hm_l = QVBoxLayout(hm_card)
        hm_lbl = QLabel("Тепловая карта выполнения заданий")
        hm_lbl.setStyleSheet(f"color: {COLORS['t1']}; font-family: '{FONT}'; font-size: 15px; font-weight: 800;")
        hm_l.addWidget(hm_lbl)

        mock_students = ["Иванов И.", "Петрова А.", "Сидоров В.", "Смирнова К.", "Попов Д."]
        mock_hm_data = [
            [1.0, 1.0, 0.8, 1.0, 0.2, 1.0],
            [0.8, 0.9, 0.5, 0.4, 0.8, 1.0],
            [0.5, 0.8, 0.2, 0.0, 0.4, 0.6],
            [1.0, 1.0, 1.0, 1.0, 0.8, 1.0],
            [0.6, 0.4, 0.4, 0.5, 0.2, 0.2],
        ]

        hm = HeatmapWidget(mock_students, 6, mock_hm_data)

        hm_scroll = QScrollArea()
        hm_scroll.setWidgetResizable(True)
        hm_scroll.setFrameShape(QFrame.Shape.NoFrame)
        hm_scroll.setWidget(hm)

        hm_l.addWidget(hm_scroll, 1)

        dist_card = CardFrame()
        dist_l = QVBoxLayout(dist_card)
        dist_lbl = QLabel("Распределение оценок")
        dist_lbl.setStyleSheet(f"color: {COLORS['t1']}; font-family: '{FONT}'; font-size: 15px; font-weight: 800;")
        dist_l.addWidget(dist_lbl)

        apply_dashboard_style()
        fig_d = Figure(figsize=(4, 3), dpi=100)
        canvas_d = FigureCanvasQTAgg(fig_d)
        ax_d = fig_d.add_subplot(111)

        bins = ["<50%", "50-70", "70-85", ">85%"]
        counts = [2, 5, 12, 9]
        colors = [COLORS["error"], "#F59E0B", "#F59E0B", COLORS["success"]]

        ax_d.bar(bins, counts, color=colors, edgecolor="none", width=0.6)
        # У скругление для баров matplotlib нет прямого API, оставляем плоские

        ax_d.tick_params(axis='both', length=0, pad=8)
        fig_d.tight_layout(pad=1.5)
        dist_l.addWidget(canvas_d, 1)

        mid_grid.addWidget(hm_card, 15)
        mid_grid.addWidget(dist_card, 10)
        c_layout.addLayout(mid_grid)

        # 4. Bottom Grid (Rating + Weak Tasks)
        bot_grid = QHBoxLayout()
        bot_grid.setSpacing(20)

        rating_card = CardFrame()
        rating_card.setMinimumHeight(240)
        rl = QVBoxLayout(rating_card)
        r_lbl = QLabel("Рейтинг студентов")
        r_lbl.setStyleSheet(f"color: {COLORS['t1']}; font-family: '{FONT}'; font-size: 15px; font-weight: 800;")
        rl.addWidget(r_lbl)

        # Заголовки рейтинга
        hr = QHBoxLayout()
        for t, s in [("#", 1), ("Студент", 3), ("Балл", 1), ("Время", 1)]:
            l = QLabel(t)
            l.setStyleSheet(f"color: {COLORS['t3']}; font-family: '{FONT}'; font-size: 11px;")
            hr.addWidget(l, s)
        rl.addLayout(hr)

        # Строки рейтинга
        for i, (name, b, t) in enumerate([("Смирнова К.", 95, "10м"), ("Иванов И.", 90, "12м"), ("Петрова А.", 78, "15м")]):
            row = QHBoxLayout()
            row.addWidget(QLabel(str(i+1)), 1)
            row.addWidget(QLabel(name), 3)
            pw = QWidget()
            pl = QHBoxLayout(pw)
            pl.setContentsMargins(0,0,0,0)
            pl.addWidget(ScorePill(b))
            pl.addStretch()
            row.addWidget(pw, 1)
            row.addWidget(QLabel(t), 1)
            rl.addLayout(row)
        rl.addStretch()

        mock_weak = [
            {"name": "Назначение антибиотиков", "type": "Множественный выбор", "fail_pct": 68},
            {"name": "Сбор жалоб", "type": "Порядок действий", "fail_pct": 45},
            {"name": "Расчет дозы адреналина", "type": "Ввод числа", "fail_pct": 42},
        ]
        weak_list = WeakTasksList(mock_weak)

        bot_grid.addWidget(rating_card, 1)
        bot_grid.addWidget(weak_list, 1)
        c_layout.addLayout(bot_grid)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)


    def _combo_style(self):
        return f"""
            QComboBox {{
                background-color: {COLORS["card"]}; border: 1px solid {COLORS["border"]};
                border-radius: 6px; padding: 6px 14px; color: {COLORS["t1"]};
                font-family: "{FONT}"; font-size: 13px; min-width: 130px;
            }}
            QComboBox::drop-down {{ border: none; }}
        """

    def _btn_ghost_style(self):
        return f"""
            QPushButton {{
                background-color: transparent; color: {COLORS["t1"]};
                border: 1px solid {COLORS["border"]}; border-radius: 6px;
                padding: 6px 14px; font-family: "{FONT}"; font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: #F0F2F5; }}
        """
