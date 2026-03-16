# ui/components/score_chart.py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ui.styles.chart_style import apply_dashboard_style
from ui.styles.dashboard_theme import COLORS


class ScoreChart(QWidget):
    """
    Линейный график успеваемости на базе matplotlib.
    """
    def __init__(self, dates: list[str], scores: list[int],
                 show_threshold: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("ScoreChart")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Применяем глобальные стили Matplotlib для Dashboards
        apply_dashboard_style()

        # Создаем фигуру
        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.fig)
        layout.addWidget(self.canvas)

        self.ax = self.fig.add_subplot(111)
        self.show_threshold = show_threshold

        self.update_data(dates, scores)

    def update_data(self, dates: list[str], scores: list[int]) -> None:
        self.ax.clear()

        if not dates or not scores:
            self.ax.text(0.5, 0.5, "Нет данных для отображения",
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, color=COLORS["t3"])
            self.canvas.draw()
            return

        x = np.arange(len(dates))
        y = np.array(scores)

        # Линия
        self.ax.plot(x, y, color=COLORS["accent"], linewidth=2.5, zorder=3)

        # Точки с цветом в зависимости от балла
        colors = []
        for s in y:
            if s >= 75: colors.append(COLORS["success"])
            elif s >= 60: colors.append(COLORS["warning"])
            else: colors.append(COLORS["error"])

        self.ax.scatter(x, y, c=colors, s=60, zorder=4,
                       edgecolors='white', linewidths=1.5)

        # Заливка под графиком (имитация градиента)
        self.ax.fill_between(x, y, 40, color=COLORS["accent"], alpha=0.1, zorder=2)

        # Линия порога
        if self.show_threshold:
            self.ax.axhline(60, color='#C42B1C66', linestyle='--',
                           linewidth=1.5, zorder=1)
            # Добавим подпись к порогу справа
            if len(x) > 0:
                self.ax.text(x[-1], 62, "60% порог", color='#C42B1CB2',
                             fontsize=9, ha='right')

        # Настройка осей
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(dates)
        self.ax.set_ylim(40, 105) # Небольшой отступ сверху

        # Кастомный форматер Y оси (добавляем %)
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: f"{int(val)}%"))

        # Отключаем деления (ticks) на осях, оставляем только подписи и сетку
        self.ax.tick_params(axis='both', length=0, pad=8)

        self.fig.tight_layout(pad=1.5)
        self.canvas.draw()
