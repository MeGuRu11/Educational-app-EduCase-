# ui/windows/student_dashboard.py
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import app
from ui.components.common import CardFrame, GradeBadge, ScorePill, SectionLabel
from ui.components.continue_banner import ContinueBanner
from ui.components.ring_progress import RingProgress
from ui.components.score_chart import ScoreChart
from ui.components.stat_card import StatCard
from ui.styles.dashboard_theme import COLORS, FONT


# Временная заглушка для CaseCard (будет браться из core/components/case_card.py если есть)
class DummyCaseCard(CardFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFixedHeight(140)
        layout_main = QVBoxLayout(self)
        layout_main.addWidget(QLabel(title))

class StudentDashboard(QWidget):
    """Экран S-1: Student Dashboard"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StudentDashboard")
        self.setStyleSheet(f"background-color: {COLORS['bg']};")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.user = app.current_user
        full_name = self.user.full_name if self.user else "Студент"

        # 1. TopBar
        topbar = QFrame()
        topbar.setFixedHeight(60)
        topbar.setStyleSheet(f"""
            background-color: {COLORS['card']};
            border-bottom: 1px solid {COLORS['border']};
        """)
        top_l = QHBoxLayout(topbar)
        top_l.setContentsMargins(28, 0, 28, 0)

        lbl_welcome = QLabel(f"Добро пожаловать, {full_name}")
        lbl_welcome.setStyleSheet(
            f"color: {COLORS['t1']}; font-family: '{FONT}'; "
            "font-size: 18px; font-weight: 800;"
        )

        lbl_date = QLabel(datetime.now().strftime("%d %B %Y"))
        lbl_date.setStyleSheet(
            f"color: {COLORS['t2']}; font-family: '{FONT}'; "
            "font-size: 13px; font-weight: 600;"
        )

        top_l.addWidget(lbl_welcome)
        top_l.addStretch()
        top_l.addWidget(lbl_date)

        main_layout.addWidget(topbar)

        # 2. Scroll Area (Content)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 40)
        c_layout.setSpacing(24)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Загрузка данных (заглушки для UI-теста, в реале из container)
        # stats = app.container.analytics_service.get_student_stats(self.user.id)
        # 3. Stat Row
        stat_row = QHBoxLayout()
        stat_row.setSpacing(16)

        s1 = StatCard(
            "ДОСТУПНО КЕЙСОВ", "12", "+2 с прошлой недели", "up",
            '<rect x="4" y="4" width="16" height="16" rx="3" stroke="#0078D4" stroke-width="2"/>'
        )
        s2 = StatCard(
            "ВЫПОЛНЕНО", "8", "3 в этом месяце", "neutral",
            '<circle cx="12" cy="12" r="8" stroke="#107C10" stroke-width="2"/>'
            '<path d="M8 12l3 3 5-5" stroke="#107C10" stroke-width="2"/>',
            COLORS["success"], COLORS["success_bg"]
        )
        s3 = StatCard(
            "СРЕДНИЙ БАЛЛ", "84%", "+5% к прошлому", "up",
            '<path d="M4 18h16M4 12h16M4 6h16" stroke="#4DA3E8" stroke-width="2"/>',
            COLORS["accent_light"], "#EFF6FC"
        )

        stat_row.addWidget(s1, 1)
        stat_row.addWidget(s2, 1)
        stat_row.addWidget(s3, 1)
        c_layout.addLayout(stat_row)

        # 4. Continue Banner (если есть активная попытка)
        # active_attempt = app.container.attempt_service.get_active(self.user.id)
        # if active_attempt:
        banner = ContinueBanner(
            "Острый коронарный синдром",
            "Модуль 3: Инструментальная диагностика",
            65, "Текущий балл: 48/75"
        )
        banner.continue_clicked.connect(lambda: print("Продолжить кейс"))
        c_layout.addWidget(banner)

        # 5. Middle Grid (RingProgress + ScoreChart)
        mid_grid = QHBoxLayout()
        mid_grid.setSpacing(20)

        ring = RingProgress(
            88, "Дифференциальный диагноз анемий", "Пройдено вчера",
            [
                ("Сбор анамнеза", 100),
                ("Лабораторная диагностика", 90),
                ("Лечение", 70)
            ]
        )
        ring.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        chart_card = CardFrame()
        chart_card.setFixedHeight(180)
        chart_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        chart_l = QVBoxLayout(chart_card)
        chart_l.setContentsMargins(20, 20, 20, 20)

        ch_top = QHBoxLayout()
        lbl_ch = QLabel("Динамика баллов")
        lbl_ch.setStyleSheet(
            f"color: {COLORS['t1']}; font-family: '{FONT}'; "
            "font-size: 15px; font-weight: 800;"
        )
        ch_top.addWidget(lbl_ch)
        ch_top.addStretch()
        chart_l.addLayout(ch_top)

        chart = ScoreChart(["12.02", "18.02", "25.02", "01.03", "10.03"], [65, 72, 68, 85, 84])
        chart_l.addWidget(chart, 1)

        # Соотношение 1 к 1.6
        mid_grid.addWidget(ring, 10)
        mid_grid.addWidget(chart_card, 16)
        c_layout.addLayout(mid_grid)

        # 6. Bottom Grid (Последние результаты + Достижения)
        bot_grid = QHBoxLayout()
        bot_grid.setSpacing(20)

        table_card = CardFrame()
        table_card.setMinimumHeight(240)
        tl = QVBoxLayout(table_card)
        tl.setContentsMargins(24, 20, 24, 20)
        lbl_tbl = QLabel("Последние результаты")
        lbl_tbl.setStyleSheet(
            f"color: {COLORS['t1']}; font-family: '{FONT}'; "
            "font-size: 15px; font-weight: 800;"
        )
        tl.addWidget(lbl_tbl)

        # Table Header
        h_row = QHBoxLayout()
        for t in ["Кейс", "Балл", "Оценка", "Дата"]:
            lbl_col = QLabel(t)
            lbl_col.setStyleSheet(
                f"color: {COLORS['t3']}; font-family: '{FONT}'; "
                "font-size: 11px;"
            )
            h_row.addWidget(lbl_col, 2 if t=="Кейс" else 1)
        tl.addLayout(h_row)

        # Table Rows (mock)
        mock_data = [
            ("Пневмония", 85, 5, "10.03.2026"),
            ("Язва желудка", 72, 3, "01.03.2026"),
            ("Бронхит", 91, 5, "25.02.2026"),
        ]
        for name, score, grade, date in mock_data:
            r = QHBoxLayout()
            n_lbl = QLabel(name)
            n_lbl.setStyleSheet(
                f"color: {COLORS['t1']}; font-family: '{FONT}'; "
                "font-weight: 600; font-size: 12px;"
            )
            r.addWidget(n_lbl, 2)

            p_wrap = QWidget()
            pl = QHBoxLayout(p_wrap)
            pl.setContentsMargins(0,0,0,0)
            pl.addWidget(ScorePill(score))
            pl.addStretch()
            r.addWidget(p_wrap, 1)

            g_wrap = QWidget()
            gl = QHBoxLayout(g_wrap)
            gl.setContentsMargins(0,0,0,0)
            gl.addWidget(GradeBadge(grade))
            gl.addStretch()
            r.addWidget(g_wrap, 1)

            d_lbl = QLabel(date)
            d_lbl.setStyleSheet(
                f"color: {COLORS['t2']}; font-family: '{FONT}'; "
                "font-size: 11px;"
            )
            r.addWidget(d_lbl, 1)
            tl.addLayout(r)
        tl.addStretch()

        ach_card = CardFrame()
        ach_card.setMinimumHeight(240)
        al = QVBoxLayout(ach_card)
        al.setContentsMargins(24, 20, 24, 20)
        al.addWidget(QLabel("Достижения (в разработке)"))
        al.addStretch()

        bot_grid.addWidget(table_card, 1)
        bot_grid.addWidget(ach_card, 1)
        c_layout.addLayout(bot_grid)

        # 7. Recommended Cases
        c_layout.addSpacing(16)
        c_layout.addWidget(SectionLabel("Рекомендованные кейсы"))

        rec_grid = QGridLayout()
        rec_grid.setSpacing(16)
        rec_grid.addWidget(DummyCaseCard("Клиническая фармакология"), 0, 0)
        rec_grid.addWidget(DummyCaseCard("Хирургия"), 0, 1)
        rec_grid.addWidget(DummyCaseCard("Терапия"), 0, 2)
        c_layout.addLayout(rec_grid)

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

    def refresh(self):
        """Обновление данных при показе экрана или событиях."""
        pass
