# ui/components/activity_feed.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from ui.components.common import ScorePill
from ui.styles.dashboard_theme import COLORS, FONT


class ActivityItem(QWidget):
    """Один элемент ленты активности."""
    def __init__(self, event_data: dict, parent=None):
        super().__init__(parent)
        # event: {"name": str, "action": str, "score": int|None, "time": str, "type": "success"|"fail"|"start"}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 11, 0, 11)
        layout.setSpacing(12)

        # Разделитель снизу
        self.setStyleSheet("""
            ActivityItem {
                border-bottom: 1px solid rgba(0,0,0,0.04);
            }
        """)

        # Точка статуса
        dot = QFrame()
        dot.setFixedSize(8, 8)

        ev_type = event_data.get("type", "start")
        dot_color = COLORS["accent"]
        if ev_type == "success":
            dot_color = COLORS["success"]
        elif ev_type == "fail":
            dot_color = "#F59E0B" # orange

        dot.setStyleSheet(f"""
            background-color: {dot_color};
            border-radius: 4px;
        """)
        layout.addWidget(dot, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Текстовый блок
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        # Собираем rich text
        name = event_data.get("name", "Студент")
        action = event_data.get("action", "начал выполнение")
        score = event_data.get("score")

        lbl_text = QLabel()
        lbl_text.setWordWrap(True)
        # Установка шрифтов через QSS
        lbl_text.setStyleSheet(f"""
            color: {COLORS["t1"]};
            font-family: "{FONT}";
            font-size: 12px;
            line-height: 1.4;
        """)

        # Используем HTML для bold
        html_text = f"<b>{name}</b> {action}"
        lbl_text.setText(html_text)

        row_txt = QHBoxLayout()
        row_txt.addWidget(lbl_text)

        if score is not None:
            pill = ScorePill(score)
            # В ленте pill должен быть inline, уменьшим его
            pill.setStyleSheet(pill.styleSheet() + " padding: 1px 7px;")
            row_txt.addWidget(pill)

        row_txt.addStretch()
        text_layout.addLayout(row_txt)
        layout.addLayout(text_layout, 1)

        # Время
        lbl_time = QLabel(event_data.get("time", ""))
        lbl_time.setStyleSheet(f"""
            color: {COLORS["t3"]};
            font-family: "{FONT}";
            font-size: 11px;
        """)
        layout.addWidget(lbl_time, 0, Qt.AlignmentFlag.AlignTop)


class ActivityFeed(QScrollArea):
    """
    Лента событий (кто начал, завершил), обновляется в реальном времени.
    """
    def __init__(self, events: list[dict] = None, parent=None):
        super().__init__(parent)
        self.setObjectName("ActivityFeed")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("background-color: transparent;")

        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setWidget(self.container)

        if events:
            for ev in events:
                self.append_event(ev)

    def prepend_event(self, event: dict) -> None:
        """Добавляет новое событие сверху (из bus.attempt_finished)."""
        item = ActivityItem(event)
        self.layout.insertWidget(0, item)

    def append_event(self, event: dict) -> None:
        """Добавляет в конец (при инициализации истории)."""
        item = ActivityItem(event)
        self.layout.addWidget(item)
