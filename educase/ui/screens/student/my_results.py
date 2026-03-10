# ui/screens/student/my_results.py
"""
Экран "Результаты" (История прохождений).
Включает таблицу/список попыток и график успеваемости (Matplotlib).
"""
import matplotlib
matplotlib.use('QtAgg')

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt

import app
from core.di_container import Container
from models.attempt import Attempt
from ui.styles.theme import COLORS, TYPO


class MyResultsPresenter:
    def __init__(self, view: 'MyResultsScreen', container: Container):
        self.view = view
        self.attempt_service = container.attempt_service
        self.case_service = container.case_service

    def load_results(self):
        user = app.current_user
        if not user:
            return
            
        attempts = self.attempt_service.get_recent_attempts(user.id, limit=999)
        # Отфильтруем только завершенные
        completed = [a for a in attempts if a.status == "completed"]
        
        data = []
        for a in completed:
            case = self.case_service.get_case(a.case_id)
            title = case.title if case else f"Кейс #{a.case_id}"
            percent = (a.score_earned / float(a.score_max)) * 100 if a.score_max else 0
            
            data.append({
                "date": a.finished_at.strftime("%d.%m.%Y %H:%M") if a.finished_at else "",
                "title": title,
                "score": f"{a.score_earned} / {a.score_max}",
                "percent": percent
            })
            
        data.reverse() # Хронологический порядок для графика
        self.view.show_data(data)


class MyResultsScreen(QWidget):
    def __init__(self, container: Container):
        super().__init__()
        self.presenter = MyResultsPresenter(self, container)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(24)
        
        lbl = QLabel("История прохождений")
        lbl.setStyleSheet(f"font-size: {TYPO['title_large']}px; font-weight: bold; color: {COLORS['text_primary']};")
        main_layout.addWidget(lbl)
        
        # ── График прогресса (Matplotlib)
        self.figure = Figure(figsize=(6, 3), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        chart_frame = QFrame()
        chart_frame.setStyleSheet(f"background: {COLORS['bg_elevated']}; border: 1px solid {COLORS['stroke_divider']}; border-radius: 8px;")
        cl = QVBoxLayout(chart_frame)
        cl.setContentsMargins(10, 10, 10, 10)
        cl.addWidget(self.canvas)
        chart_frame.setFixedHeight(300)
        
        main_layout.addWidget(chart_frame)
        
        # ── Таблица результатов
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Дата", "Название кейса", "Баллы"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: 8px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_layer']};
                padding: 8px;
                border: none;
                border-bottom: 1px solid {COLORS['stroke_divider']};
                font-weight: bold;
                color: {COLORS['text_secondary']};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS['stroke_divider']};
                color: {COLORS['text_primary']};
            }}
        """)
        
        main_layout.addWidget(self.table)

    def showEvent(self, event):
        super().showEvent(event)
        self.presenter.load_results()

    def show_data(self, data: List[dict]):
        self.table.setRowCount(0)
        
        dates = []
        percents = []
        
        for i, row_data in enumerate(reversed(data)): # Таблица: новые сверху
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(row_data["date"]))
            self.table.setItem(i, 1, QTableWidgetItem(row_data["title"]))
            self.table.setItem(i, 2, QTableWidgetItem(row_data["score"]))
            
        for d in data: # График: старые слева, новые справа
            dates.append(d["date"].split()[0]) # Только дата
            percents.append(d["percent"])
            
        # Отрисовка графика
        self.ax.clear()
        
        # Стайлинг под тему
        self.figure.patch.set_facecolor(COLORS['bg_elevated'])
        self.ax.set_facecolor(COLORS['bg_elevated'])
        self.ax.tick_params(colors=COLORS['text_secondary'])
        # Заменяем rgba() на hex для Matplotlib, так как он не понимает формат Qt rgba(r,g,b,a)
        stroke_color = "#E0E0E0"  # Примерно соответствует rgba(0,0,0,0.05) на белом фоне
        
        self.ax.spines['bottom'].set_color(stroke_color)
        self.ax.spines['top'].set_color('none') 
        self.ax.spines['right'].set_color('none')
        self.ax.spines['left'].set_color(stroke_color)
        
        if percents:
            self.ax.plot(dates, percents, marker='o', linestyle='-', color=COLORS['accent'], linewidth=2)
            self.ax.set_ylim(0, 105)
            self.ax.set_title("Успеваемость (%)", color=COLORS['text_primary'], fontsize=12)
            self.ax.grid(True, linestyle='--', alpha=0.5, color=stroke_color)
            self.figure.tight_layout()
        else:
            self.ax.text(0.5, 0.5, "Нет данных\nПройдите хотя бы один кейс", 
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, color=COLORS['text_disabled'])
            
        self.canvas.draw()
