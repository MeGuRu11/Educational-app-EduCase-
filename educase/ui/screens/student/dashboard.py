# ui/screens/student/dashboard.py
from datetime import datetime
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, 
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget
)

import app
from ui.components.common import CardFrame, GradeBadge, ScorePill, SectionLabel
from ui.components.continue_banner import ContinueBanner
from ui.components.ring_progress import RingProgress
from ui.components.score_chart import ScoreChart
from ui.components.stat_card import StatCard
from ui.styles.dashboard_theme import COLORS, FONT
from .dashboard_presenter import StudentDashboardPresenter, StudentStat, ActiveCaseInfo, HistoryEntry

class StudentDashboard(QWidget):
    """Экран S-1: Student Dashboard (Refactored to MVP)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StudentDashboard")
        self.setStyleSheet(f"background-color: {COLORS['bg']};")
        
        self.container = getattr(parent, "container", None)
        self.presenter = StudentDashboardPresenter(self, self.container)

        self._setup_ui()
        self.presenter.load_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. TopBar
        topbar = QFrame()
        topbar.setFixedHeight(60)
        topbar.setStyleSheet(f"""
            background-color: {COLORS['card']};
            border-bottom: 1px solid {COLORS['border']};
        """)
        top_l = QHBoxLayout(topbar)
        top_l.setContentsMargins(28, 0, 28, 0)

        self.lbl_welcome = QLabel("Добро пожаловать")
        self.lbl_welcome.setStyleSheet(
            f"color: {COLORS['t1']}; font-family: '{FONT}'; "
            "font-size: 18px; font-weight: 800;"
        )
        top_l.addWidget(self.lbl_welcome)
        top_l.addStretch()
        
        lbl_date = QLabel(datetime.now().strftime("%d %B %Y"))
        lbl_date.setStyleSheet(
            f"color: {COLORS['t2']}; font-family: '{FONT}'; "
            "font-size: 13px; font-weight: 600;"
        )
        top_l.addWidget(lbl_date)
        main_layout.addWidget(topbar)

        # 2. Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        self.clayout = QVBoxLayout(content)
        self.clayout.setContentsMargins(28, 24, 28, 40)
        self.clayout.setSpacing(24)
        self.clayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 3. Stat Row
        self.stat_row = QHBoxLayout()
        self.stat_row.setSpacing(16)
        self.clayout.addLayout(self.stat_row)

        # 4. Banner Container
        self.banner_container = QVBoxLayout()
        self.clayout.addLayout(self.banner_container)

        # 5. Middle Grid (RingProgress + Chart)
        mid_grid = QHBoxLayout()
        mid_grid.setSpacing(20)
        
        self.ring = RingProgress(0, "Загрузка...", "", [])
        self.ring.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.chart_card = CardFrame()
        self.chart_card.setFixedHeight(180)
        self.chart_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        chart_l = QVBoxLayout(self.chart_card)
        chart_l.setContentsMargins(20, 20, 20, 20)
        lbl_ch = QLabel("Динамика баллов")
        lbl_ch.setStyleSheet(f"color: {COLORS['t1']}; font-size: 15px; font-weight: 800;")
        chart_l.addWidget(lbl_ch)
        self.chart_container = QVBoxLayout()
        chart_l.addLayout(self.chart_container)
        
        mid_grid.addWidget(self.ring, 10)
        mid_grid.addWidget(self.chart_card, 16)
        self.clayout.addLayout(mid_grid)

        # 6. Bottom Table
        self.history_card = CardFrame()
        self.history_card.setMinimumHeight(240)
        tl = QVBoxLayout(self.history_card)
        tl.setContentsMargins(24, 20, 24, 20)
        tl.addWidget(SectionLabel("Последние результаты"))
        
        self.history_layout = QVBoxLayout()
        tl.addLayout(self.history_layout)
        tl.addStretch()
        self.clayout.addWidget(self.history_card)

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

    def display_stats(self, stats: List[StudentStat]):
        for i in reversed(range(self.stat_row.count())): self.stat_row.itemAt(i).widget().setParent(None)
        for s in stats:
            card = StatCard(s.label, s.value, s.delta, s.delta_type, s.icon_svg, 
                            s.accent or COLORS["accent"], s.icon_bg or "transparent")
            self.stat_row.addWidget(card, 1)
        
        if app.current_user:
            self.lbl_welcome.setText(f"Добро пожаловать, {app.current_user.full_name}")

    def display_active_case(self, info: ActiveCaseInfo):
        for i in reversed(range(self.banner_container.count())): self.banner_container.itemAt(i).widget().setParent(None)
        banner = ContinueBanner(info.title, info.subtitle, info.progress, info.score_info)
        self.banner_container.addWidget(banner)

    def display_chart(self, data: dict):
        for i in reversed(range(self.chart_container.count())): 
            item = self.chart_container.itemAt(i).widget()
            if item: item.setParent(None)
        chart = ScoreChart(data["labels"], data["values"])
        self.chart_container.addWidget(chart)

    def display_history(self, history: List[HistoryEntry]):
        for i in reversed(range(self.history_layout.count())):
            item = self.history_layout.itemAt(i).widget()
            if item: item.setParent(None)
        
        for entry in history:
            row = QHBoxLayout()
            n_lbl = QLabel(entry.name); n_lbl.setStyleSheet(f"color: {COLORS['t1']}; font-weight: 600;")
            row.addWidget(n_lbl, 2)
            row.addWidget(ScorePill(entry.score), 1)
            row.addWidget(GradeBadge(entry.grade), 1)
            d_lbl = QLabel(entry.date); d_lbl.setStyleSheet(f"color: {COLORS['t2']}; font-size: 11px;")
            row.addWidget(d_lbl, 1)
            self.history_layout.addLayout(row)
