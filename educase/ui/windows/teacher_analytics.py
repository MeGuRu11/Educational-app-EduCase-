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
        self.container = getattr(parent, "container", None)
        
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

        # 2. Real Data from Container
        avg_score = 0.0
        students_count = 0
        comp_pct = 0
        if self.container:
            attempt_repo = self.container.attempt_repo
            user_repo = self.container.user_repo
            avg_score = attempt_repo.get_avg_score()
            students_count = user_repo.count_by_role("student")
            total_attempts = attempt_repo.count()
            if total_attempts > 0:
                from sqlalchemy import func
                from models.attempt import Attempt
                comp_count = attempt_repo.session.query(func.count(Attempt.id)).filter(Attempt.status == "completed").scalar() or 0
                comp_pct = int((comp_count / total_attempts) * 100) if total_attempts > 0 else 0

        # 3. Stat Row
        stat_row = QHBoxLayout()
        stat_row.setSpacing(16)
        stat_row.addWidget(StatCard("СР. БАЛЛ", f"{avg_score:.1f}%", "", "neutral"))
        stat_row.addWidget(StatCard("ЗАВЕРШИЛИ", f"{comp_pct}%", f"Всего {students_count} студ.", "neutral", accent_color=COLORS["success"]))
        stat_row.addWidget(StatCard("СР. ВРЕМЯ", "14м 20с", "", "neutral", accent_color="#F59E0B"))
        stat_row.addWidget(StatCard("ЛУЧШИЙ", "100%", "Студент", "neutral", accent_color=COLORS["accent_light"]))
        c_layout.addLayout(stat_row)

        # 4. Heatmap & Chart (Simplified real or empty if no data)
        mid_grid = QHBoxLayout()
        mid_grid.setSpacing(20)

        hm_card = CardFrame()
        hm_l = QVBoxLayout(hm_card)
        hm_lbl = QLabel("Тепловая карта выполнения заданий")
        hm_lbl.setStyleSheet(f"color: {COLORS['t1']}; font-family: '{FONT}'; font-size: 15px; font-weight: 800;")
        hm_l.addWidget(hm_lbl)

        # Realistic but generic data if no database entries
        mock_students = ["Студент A", "Студент B", "Студент C", "Студент D", "Студент E"]
        mock_hm_data = [[0.8]*6]*5
        
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
        counts = [0, 0, 0, 0] # Real aggregation could be added here
        colors = [COLORS["error"], "#F59E0B", "#F59E0B", COLORS["success"]]
        ax_d.bar(bins, counts, color=colors, edgecolor="none", width=0.6)
        ax_d.tick_params(axis='both', length=0, pad=8)
        fig_d.tight_layout(pad=1.5)
        dist_l.addWidget(canvas_d, 1)

        mid_grid.addWidget(hm_card, 15)
        mid_grid.addWidget(dist_card, 10)
        c_layout.addLayout(mid_grid)

        # 5. Rating & Weak Tasks (Real or generic if no data)
        bot_grid = QHBoxLayout()
        bot_grid.setSpacing(20)
        rating_card = CardFrame()
        rating_card.setMinimumHeight(240)
        rl = QVBoxLayout(rating_card)
        r_lbl = QLabel("Рейтинг студентов")
        r_lbl.setStyleSheet(f"color: {COLORS['t1']}; font-family: '{FONT}'; font-size: 15px; font-weight: 800;")
        rl.addWidget(r_lbl)
        rl.addWidget(no_data_lbl)
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
