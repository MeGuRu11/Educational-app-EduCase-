# ui/screens/student/dashboard.py
"""
Дашборд студента: сводка (статистика), последние кейсы.
Использует MVP (Model-View-Presenter).
"""
from typing import List, Dict, Any

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QScrollArea, QPushButton, QGridLayout, QSizePolicy
)

import app
from core.di_container import Container
from ui.styles.theme import COLORS, RADIUS, TYPO
from ui.styles.icons import get_icon


class DashboardPresenter:
    def __init__(self, view: 'StudentDashboard', container: Container):
        self.view = view
        self.attempt_service = container.attempt_service
        self.case_service = container.case_service

    def load_data(self):
        user = app.current_user
        if not user:
            return

        # Загрузка статистики
        stats = self.attempt_service.get_user_stats(user.id)
        self.view.show_stats(stats)

        # Загрузка последних попыток
        recent_attempts = self.attempt_service.get_recent_attempts(user.id, limit=5)
        
        # Подгрузка названий кейсов
        cases_data = []
        for a in recent_attempts:
            case = self.case_service.get_case(a.case_id)
            if case:
                cases_data.append({
                    "id": a.id,
                    "case_id": case.id,
                    "title": case.title,
                    "status": a.status,
                    "score": a.score_earned,
                    "date": a.started_at.strftime("%d.%m.%Y")
                })
        self.view.show_recent_cases(cases_data)


class StatCard(QFrame):
    def __init__(self, title: str, value: str, icon_name: str, color_key: str):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: {RADIUS['large']}px;
            }}
        """)
        self.setFixedHeight(120)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Иконка
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon(icon_name, COLORS[color_key], 48).pixmap(48, 48))
        layout.addWidget(icon_lbl)
        
        # Текст
        text_layout = QVBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        
        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 28px; font-weight: bold;")
        
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(self.val_lbl)
        text_layout.addStretch()
        layout.addLayout(text_layout)
        layout.addStretch()

    def set_value(self, val: str):
        self.val_lbl.setText(val)


class RecentCaseCard(QFrame):
    def __init__(self, data: dict):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: {RADIUS['card']}px;
            }}
            QFrame:hover {{
                border: 1px solid {COLORS['accent_light']};
            }}
        """)
        self.setFixedHeight(80)
        
        layout = QHBoxLayout(self)
        
        # Title
        title_lbl = QLabel(data["title"])
        title_lbl.setStyleSheet(f"font-size: 16px; font-weight: 500; color: {COLORS['text_primary']};")
        
        # Status / Date
        status_text = "Завершён" if data["status"] == "completed" else "В процессе"
        color = COLORS["success"] if data["status"] == "completed" else COLORS["warning"]
        status_lbl = QLabel(f"{status_text} • {data['date']}")
        status_lbl.setStyleSheet(f"color: {color}; font-size: 13px;")
        
        left_layout = QVBoxLayout()
        left_layout.addWidget(title_lbl)
        left_layout.addWidget(status_lbl)
        layout.addLayout(left_layout)
        
        layout.addStretch()
        
        # Score
        if data["status"] == "completed":
            score_lbl = QLabel(f"{data['score']} баллов")
            score_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['accent']};")
            layout.addWidget(score_lbl)
            
        btn = QPushButton("Открыть")
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: #fff;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS['accent_hover']}; }}
        """)
        # TODO: connect button to open case player
        layout.addWidget(btn)


class StudentDashboard(QWidget):
    def __init__(self, container: Container):
        super().__init__()
        self.container = container
        self.presenter = DashboardPresenter(self, container)
        
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(24)

        # ── Заголовок
        self.welcome_lbl = QLabel("Добро пожаловать!")
        self.welcome_lbl.setStyleSheet(f"font-size: {TYPO['title_large']}px; font-weight: bold; color: {COLORS['text_primary']};")
        self.content_layout.addWidget(self.welcome_lbl)

        # ── Карточки статистики
        stats_layout = QHBoxLayout()
        self.card_cases = StatCard("Пройдено кейсов", "0", "check", "success")
        self.card_score = StatCard("Средний балл", "0%", "star", "warning")
        self.card_time = StatCard("Время обучения", "0 ч", "clock", "accent")
        
        stats_layout.addWidget(self.card_cases)
        stats_layout.addWidget(self.card_score)
        stats_layout.addWidget(self.card_time)
        self.content_layout.addLayout(stats_layout)

        # ── Последние кейсы
        recent_lbl = QLabel("Последняя активность")
        recent_lbl.setStyleSheet(f"font-size: {TYPO['title']}px; font-weight: 600; color: {COLORS['text_primary']}; margin-top: 20px;")
        self.content_layout.addWidget(recent_lbl)

        self.recent_container = QVBoxLayout()
        self.recent_container.setSpacing(12)
        self.content_layout.addLayout(self.recent_container)

        self.content_layout.addStretch()
        
        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll)

    def showEvent(self, event):
        super().showEvent(event)
        if app.current_user:
            self.welcome_lbl.setText(f"Добро пожаловать, {app.current_user.full_name}!")
        self.presenter.load_data()

    def show_stats(self, stats: Dict[str, Any]):
        self.card_cases.set_value(str(stats.get("completed_cases", 0)))
        self.card_score.set_value(f"{stats.get('avg_score_percent', 0)}%")
        
        total_seconds = stats.get("total_time_seconds", 0)
        hours = total_seconds // 3600
        mins = (total_seconds % 3600) // 60
        time_str = f"{hours}ч {mins}м" if hours > 0 else f"{mins}м"
        self.card_time.set_value(time_str)

    def show_recent_cases(self, cases: List[Dict[str, Any]]):
        # Очистить старые
        for i in reversed(range(self.recent_container.count())): 
            widget = self.recent_container.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                
        if not cases:
            empty = QLabel("Нет недавней активности. Пора начать первый кейс!")
            empty.setStyleSheet(f"color: {COLORS['text_secondary']};")
            self.recent_container.addWidget(empty)
            return

        for case_data in cases:
            self.recent_container.addWidget(RecentCaseCard(case_data))

