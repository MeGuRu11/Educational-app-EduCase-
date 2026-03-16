# ui/windows/student_results.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.components.common import CardFrame, GradeBadge, ScorePill
from ui.components.score_chart import ScoreChart
from ui.components.stat_card import StatCard
from ui.styles.dashboard_theme import COLORS, FONT


class StudentResults(QWidget):
    """Экран S-5: My Results"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StudentResults")
        self.setStyleSheet(f"background-color: {COLORS['bg']};")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 40)
        main_layout.setSpacing(24)

        # Top Header (без TopBar, просто заголовок внутри ScrollArea/Layout)
        title = QLabel("Мои результаты")
        title.setStyleSheet(
            f"color: {COLORS['t1']}; font-family: '{FONT}'; "
            "font-size: 24px; font-weight: 800;"
        )
        main_layout.addWidget(title)

        # 1. Filters
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        date_picker = QComboBox()
        date_picker.addItems(["За всё время", "За 30 дней", "За 7 дней"])
        date_picker.setStyleSheet(self._combo_style())

        disc_picker = QComboBox()
        disc_picker.addItems(["Все дисциплины", "Терапия", "Хирургия"])
        disc_picker.setStyleSheet(self._combo_style())

        filter_row.addWidget(date_picker)
        filter_row.addWidget(disc_picker)
        filter_row.addStretch()
        main_layout.addLayout(filter_row)

        # 2. Stat Row
        stat_row = QHBoxLayout()
        stat_row.setSpacing(16)
        stat_row.addWidget(StatCard("Всего попыток", "34", "", "neutral"))
        stat_row.addWidget(StatCard("Средний балл", "84%", "+2%", "up", accent_color=COLORS["success"]))
        stat_row.addWidget(StatCard("Ср. время", "14 мин", "-1 мин", "up", accent_color="#F59E0B"))
        stat_row.addWidget(StatCard("Лучший рез-т", "100%", "Вчера", "neutral", accent_color=COLORS["accent_light"]))
        main_layout.addLayout(stat_row)

        # 3. График успеваемости
        chart_card = CardFrame()
        chart_card.setFixedHeight(280)
        chart_l = QVBoxLayout(chart_card)
        chart_lbl = QLabel("График успеваемости")
        chart_lbl.setStyleSheet(
            f"color: {COLORS['t1']}; font-family: '{FONT}'; "
            "font-size: 16px; font-weight: 800;"
        )
        chart_l.addWidget(chart_lbl)

        # Данные из history
        dates = ["01.03", "03.03", "05.03", "07.03", "10.03", "11.03"]
        scores = [60, 45, 75, 82, 90, 88]
        chart = ScoreChart(dates, scores)
        chart_l.addWidget(chart, 1)
        main_layout.addWidget(chart_card)

        # 4. История попыток (Таблица)
        table_card = CardFrame()
        tl = QVBoxLayout(table_card)
        tl.setContentsMargins(24, 20, 24, 20)

        t_title = QLabel("История попыток")
        t_title.setStyleSheet(
            f"color: {COLORS['t1']}; font-family: '{FONT}'; "
            "font-size: 16px; font-weight: 800;"
        )
        tl.addWidget(t_title)

        # Заголовки
        h_row = QHBoxLayout()
        for t, s in [("Кейс", 3), ("Дисциплина", 2), ("Дата", 1), ("Время", 1), ("Балл", 1), ("Оценка", 1), ("", 1)]:
            lbl = QLabel(t)
            lbl.setStyleSheet(
                f"color: {COLORS['t3']}; font-family: '{FONT}'; "
                "font-size: 11px;"
            )
            h_row.addWidget(lbl, s)
        tl.addLayout(h_row)

        # Данные
        mock = [
            ("Острый коронарный синдром", "Кардиология", "11.03.2026", "12 мин", 88, 5),
            ("Пневмония", "Терапия", "10.03.2026", "15 мин", 90, 5),
            ("Аппендицит", "Хирургия", "07.03.2026", "18 мин", 82, 4),
            ("Анемия", "Терапия", "03.03.2026", "10 мин", 45, 2),
        ]

        for name, disc, date, time, score, grade in mock:
            r = QHBoxLayout()
            r.setContentsMargins(0, 8, 0, 8)

            n = QLabel(name)
            n.setStyleSheet(f"color: {COLORS['t1']}; font-weight: 600; font-size: 13px;")
            r.addWidget(n, 3)

            d = QLabel(disc)
            d.setStyleSheet(f"color: {COLORS['t2']}; font-size: 12px;")
            r.addWidget(d, 2)

            dt = QLabel(date)
            dt.setStyleSheet(f"color: {COLORS['t2']}; font-size: 12px;")
            r.addWidget(dt, 1)

            tm = QLabel(time)
            tm.setStyleSheet(f"color: {COLORS['t2']}; font-size: 12px;")
            r.addWidget(tm, 1)

            pw = QWidget()
            pl = QHBoxLayout(pw)
            pl.setContentsMargins(0,0,0,0)
            pl.addWidget(ScorePill(score))
            r.addWidget(pw, 1)

            gw = QWidget()
            gl = QHBoxLayout(gw)
            gl.setContentsMargins(0,0,0,0)
            gl.addWidget(GradeBadge(grade))
            r.addWidget(gw, 1)

            btn = QPushButton("Детали")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self._btn_ghost_style())
            r.addWidget(btn, 1)

            tl.addLayout(r)

            # Разделитель
            div = QFrame()
            div.setFrameShape(QFrame.Shape.HLine)
            div.setStyleSheet("color: rgba(0,0,0,0.04);")
            tl.addWidget(div)

        tl.addStretch()
        main_layout.addWidget(table_card, 1) # table card expands

    def _combo_style(self):
        return f"""
            QComboBox {{
                background-color: {COLORS["card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 6px;
                padding: 6px 14px;
                color: {COLORS["t1"]};
                font-family: "{FONT}";
                font-size: 13px;
                min-width: 150px;
            }}
            QComboBox::drop-down {{ border: none; }}
        """

    def _btn_ghost_style(self):
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS["accent"]};
                border: 1px solid {COLORS["accent"]};
                border-radius: 6px;
                padding: 4px 10px;
                font-family: "{FONT}";
                font-size: 11px;
                font-weight: 700;
            }}
            QPushButton:hover {{ background-color: #F0F8FF; }}
        """
