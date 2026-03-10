# ui/screens/student/my_cases.py
"""
Экран "Мои кейсы" для студента со списком доступных кейсов.
Отображает сетку карточек с использованием QGridLayout.
"""
from typing import List

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QScrollArea, QPushButton, QGraphicsOpacityEffect, QGridLayout
)

from core.di_container import Container
from core.event_bus import bus
from models.content import Case
from ui.styles.theme import COLORS, RADIUS, TYPO
from ui.styles.icons import get_icon


class MyCasesPresenter:
    def __init__(self, view: 'MyCasesScreen', container: Container):
        self.view = view
        self.case_service = container.case_service

    def load_cases(self):
        cases = self.case_service.get_available_cases()
        self.view.show_cases(cases)


class CaseCard(QFrame):
    def __init__(self, case: Case):
        super().__init__()
        self.case = case
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: {RADIUS['large']}px;
            }}
            QFrame:hover {{
                border: 1px solid {COLORS['accent']};
            }}
        """)
        self.setFixedSize(300, 220)
        
        # Эффект прозрачности для stagger-анимации
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity_effect)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title_lbl = QLabel(case.title)
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet(f"font-size: {TYPO['subtitle']}px; font-weight: bold; color: {COLORS['text_primary']}; border: none;")
        layout.addWidget(title_lbl)
        
        # Описание
        desc_text = case.short_description or "Нет описания."
        if len(desc_text) > 80:
            desc_text = desc_text[:77] + "..."
        desc_lbl = QLabel(desc_text)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: {TYPO['body']}px; border: none;")
        layout.addWidget(desc_lbl)
        
        layout.addStretch()
        
        # Мета-информация (Сложность, Время)
        meta_layout = QHBoxLayout()
        diff_stars = "★" * case.difficulty + "☆" * (3 - case.difficulty)
        diff_lbl = QLabel(f"Сложность: {diff_stars}")
        diff_lbl.setStyleSheet(f"color: {COLORS['warning']}; font-size: 12px; border: none;")
        
        time_limit = f"{case.time_limit_minutes} мин" if case.time_limit_minutes else "Без лимита"
        time_lbl = QLabel(f"⏱ {time_limit}")
        time_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; border: none;")
        
        meta_layout.addWidget(diff_lbl)
        meta_layout.addStretch()
        meta_layout.addWidget(time_lbl)
        layout.addLayout(meta_layout)
        
        # Кнопка начать
        self.btn_start = QPushButton("Начать кейс")
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_light']}20;
                color: {COLORS['accent']};
                border: none;
                border-radius: {RADIUS['control']}px;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent']};
                color: white;
            }}
        """)
        self.btn_start.clicked.connect(self._on_start_clicked)
        layout.addWidget(self.btn_start)

    def _on_start_clicked(self):
        # Отправляем ивент запуска плеера
        bus.start_case.emit(self.case.id)
        
    def animate_in(self, delay_ms: int):
        # Анимация появления
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(400)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        
        QTimer.singleShot(delay_ms, self.anim.start)


class MyCasesScreen(QWidget):
    def __init__(self, container: Container):
        super().__init__()
        self.container = container
        self.presenter = MyCasesPresenter(self, container)
        
        self.cards: List[CaseCard] = []
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Верхняя панель (фильтры/поиск в будущем)
        top_area = QWidget()
        top_layout = QHBoxLayout(top_area)
        top_layout.setContentsMargins(40, 20, 40, 10)
        lbl = QLabel("Доступные кейсы")
        lbl.setStyleSheet(f"font-size: {TYPO['title_large']}px; font-weight: bold; color: {COLORS['text_primary']};")
        top_layout.addWidget(lbl)
        top_layout.addStretch()
        main_layout.addWidget(top_area)

        # Область со скроллом
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setContentsMargins(40, 20, 40, 40)
        self.grid_layout.setSpacing(24)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll)

    def showEvent(self, event):
        super().showEvent(event)
        self.presenter.load_cases()

    def show_cases(self, cases: List[Case]):
        # Очистить старые
        for i in reversed(range(self.grid_layout.count())): 
            item = self.grid_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        self.cards.clear()

        if not cases:
            empty = QLabel("Нет доступных кейсов.")
            empty.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 16px;")
            self.grid_layout.addWidget(empty, 0, 0)
            return

        # Заполнение сетки (адаптивно)
        # 3 колонки максимум, если окно большое. Пока захардкодим 3 колонки.
        cols = 3
        for i, case in enumerate(cases):
            card = CaseCard(case)
            self.cards.append(card)
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(card, row, col)
            
            # Stagger animation
            card.animate_in(i * 100)

