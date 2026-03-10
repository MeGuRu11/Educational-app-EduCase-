# ui/screens/student/case_result.py
"""
Экран результатов прохождения кейса.
Показывает итоговый балл (ProgressRing), время, и список заданий.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QFont

from ui.styles.theme import COLORS


class CaseResultDialog(QDialog):
    """Экран результатов после завершения кейса."""

    def __init__(self, result_data: dict, parent=None):
        """
        result_data: {
            case_name: str,
            score_earned: float,
            score_max: float,
            time_spent_seconds: int,
            tasks: [{task_id, title, answered, is_correct, score}, ...]
        }
        """
        super().__init__(parent)
        self.setWindowTitle("Результаты")
        self.setMinimumSize(600, 500)
        self.setMaximumSize(700, 650)
        self.setStyleSheet(f"QDialog {{ background: {COLORS['bg_base']}; }}")

        self._data = result_data
        self._build_ui()

        # Анимация после 300мс
        QTimer.singleShot(300, self._animate_score)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 24)
        layout.setSpacing(20)

        # ── Заголовок ──
        title = QLabel(self._data.get("case_name", "Кейс завершён"))
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # ── Результат (центральный блок) ──
        score_earned = self._data.get("score_earned", 0)
        score_max = self._data.get("score_max", 1)
        pct = (score_earned / score_max * 100) if score_max > 0 else 0

        # Цвет по результату
        if pct >= 80:
            color = "#4CAF50"
            grade_text = "Отлично!"
        elif pct >= 60:
            color = "#FF9800"
            grade_text = "Хорошо"
        elif pct >= 40:
            color = "#FF5722"
            grade_text = "Удовлетворительно"
        else:
            color = "#F44336"
            grade_text = "Не сдано"

        score_block = QWidget()
        score_block.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: 16px;
            }}
        """)
        sb_layout = QVBoxLayout(score_block)
        sb_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb_layout.setSpacing(8)

        # Крупный процент
        self.lbl_percent = QLabel(f"0%")
        self.lbl_percent.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        self.lbl_percent.setStyleSheet(f"color: {color}; border: none;")
        self.lbl_percent.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb_layout.addWidget(self.lbl_percent)

        # Оценка
        grade_lbl = QLabel(grade_text)
        grade_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        grade_lbl.setStyleSheet(f"color: {color}; border: none;")
        grade_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb_layout.addWidget(grade_lbl)

        # Баллы
        score_lbl = QLabel(f"{score_earned:.1f} / {score_max:.1f} баллов")
        score_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px; border: none;")
        score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb_layout.addWidget(score_lbl)

        # Время
        time_s = self._data.get("time_spent_seconds", 0)
        mins, secs = divmod(time_s, 60)
        time_lbl = QLabel(f"⏱ Время: {mins}мин {secs}сек")
        time_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; border: none;")
        time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb_layout.addWidget(time_lbl)

        layout.addWidget(score_block)

        # ── Список тем ──
        tasks = self._data.get("tasks", [])
        if tasks:
            tasks_label = QLabel("Темы заданий:")
            tasks_label.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']}; font-size: 14px;")
            layout.addWidget(tasks_label)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setMaximumHeight(200)
            scroll.setStyleSheet(f"""
                QScrollArea {{ border: none; }}
                QScrollBar:vertical {{
                    width: 4px; background: transparent;
                }}
                QScrollBar::handle:vertical {{
                    background: {COLORS['stroke_control']}; border-radius: 2px;
                }}
            """)

            tasks_w = QWidget()
            tw_layout = QVBoxLayout(tasks_w)
            tw_layout.setContentsMargins(0, 0, 0, 0)
            tw_layout.setSpacing(6)

            for i, t in enumerate(tasks, 1):
                row = QWidget()
                row.setStyleSheet(f"""
                    QWidget {{
                        background: {COLORS['bg_elevated']};
                        border: 1px solid {COLORS['stroke_divider']};
                        border-radius: 6px;
                    }}
                """)
                rl = QHBoxLayout(row)
                rl.setContentsMargins(14, 10, 14, 10)

                num_lbl = QLabel(f"{i}.")
                num_lbl.setFixedWidth(24)
                num_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: bold; border: none;")
                rl.addWidget(num_lbl)

                name = QLabel(t.get("topic", t.get("title", "Задание")))
                name.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px; border: none;")
                rl.addWidget(name, stretch=1)

                tw_layout.addWidget(row)

            scroll.setWidget(tasks_w)
            layout.addWidget(scroll)

        # ── Кнопка закрытия ──
        btn_close = QPushButton("Готово")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFixedHeight(44)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                color: white;
                font-weight: bold;
                font-size: 15px;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{ background: #1565C0; }}
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _animate_score(self):
        """Анимирует счётчик процентов 0% → N%."""
        score_earned = self._data.get("score_earned", 0)
        score_max = self._data.get("score_max", 1)
        target_pct = int((score_earned / score_max * 100) if score_max > 0 else 0)

        self._anim_val = 0
        self._anim_target = target_pct

        timer = QTimer(self)
        timer.setInterval(20)  # ~50fps

        def step():
            if self._anim_val < self._anim_target:
                self._anim_val += 1
                self.lbl_percent.setText(f"{self._anim_val}%")
            else:
                timer.stop()

        timer.timeout.connect(step)
        timer.start()
