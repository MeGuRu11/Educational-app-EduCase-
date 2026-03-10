from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFrame, QSpinBox)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon
from ..base_editor import AbstractTaskEditor

class TimelineEditor(AbstractTaskEditor):
    """
    Редактор для задания типа "Таймлайн" (timeline).
    Позволяет добавлять карточки событий и года, чтобы студент расставил их в правильном хронологическом порядке.
    """
    def __init__(self, parent=None):
        self.events = [] # Список dict: {"id": str, "widget": QWidget, "text": QLineEdit, "year": QSpinBox}
        self.event_counter = 0
        super().__init__(parent)
        
    def _setup_specific_ui(self, layout: QVBoxLayout):
        self.events_group = QWidget()
        self.events_layout = QVBoxLayout(self.events_group)
        self.events_layout.setContentsMargins(0, 16, 0, 0)
        self.events_layout.setSpacing(8)
        
        title = QLabel("Хронология событий")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']};")
        self.events_layout.addWidget(title)
        
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.events_layout.addWidget(self.list_container)
        
        self.btn_add = QPushButton("+ Добавить событие")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['accent']};
                font-weight: bold;
                border: 2px dashed {COLORS['accent']}40;
                border-radius: 6px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background: {COLORS['state_hover']};
                border-color: {COLORS['accent']};
            }}
        """)
        self.btn_add.clicked.connect(self._add_empty_event)
        self.events_layout.addWidget(self.btn_add)
        
        layout.addWidget(self.events_group)
        
        # Добавим две дефолтных карточки
        self._add_empty_event()
        self._add_empty_event()

    def _add_empty_event(self):
        ev_id = f"evt_{self.event_counter}"
        self.event_counter += 1
        
        row = QFrame()
        row.setStyleSheet(f"background: {COLORS['bg_elevated']}; border: 1px solid {COLORS['stroke_divider']}; border-radius: 6px;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 8, 12, 8)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        spin_year = QSpinBox()
        spin_year.setPrefix("Год: ")
        spin_year.setRange(-5000, 3000) # От до нашей эры до будущего
        spin_year.setValue(2000)
        spin_year.setFixedWidth(120)
        spin_year.setStyleSheet(f"""
            QSpinBox {{
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 4px;
                background: {COLORS['bg_layer']};
                color: {COLORS['text_primary']};
                padding: 4px;
            }}
            QSpinBox:focus {{ border: 1px solid {COLORS['accent']}; }}
        """)
        spin_year.valueChanged.connect(lambda: self.data_changed.emit())
        
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Название события...")
        line_edit.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
            QLineEdit:focus {{ outline: none; }}
        """)
        line_edit.textChanged.connect(lambda: self.data_changed.emit())
        
        btn_del = QPushButton()
        btn_del.setIcon(get_icon("delete", COLORS["error"], 18))
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("border: none; background: transparent; padding: 4px; margin: 0;")
        btn_del.clicked.connect(lambda: self._remove_event(ev_id))
        
        row_layout.addWidget(spin_year, alignment=Qt.AlignmentFlag.AlignVCenter)
        row_layout.addWidget(line_edit, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)
        row_layout.addWidget(btn_del, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        self.list_layout.addWidget(row)
        
        self.events.append({
            "id": ev_id,
            "widget": row,
            "text": line_edit,
            "year": spin_year
        })
        
        self.data_changed.emit()

    def _remove_event(self, ev_id: str):
        if len(self.events) <= 2:
            return  # Нужно минимум 2
            
        target_ev = next((e for e in self.events if e["id"] == ev_id), None)
        if target_ev:
            self.list_layout.removeWidget(target_ev["widget"])
            target_ev["widget"].deleteLater()
            self.events.remove(target_ev)
            self.data_changed.emit()

    def get_specific_data(self) -> dict:
        evt_data = []
        for e in self.events:
            text = e["text"].text().strip()
            if text:
                evt_data.append({
                    "id": e["id"],
                    "year": e["year"].value(),
                    "text": text
                })
        # Сортируем по году перед сохранением, так как это правильный хронологический порядок:
        evt_data.sort(key=lambda x: x["year"])
        return {"events": evt_data}

    def set_specific_data(self, data: dict):
        for e in list(self.events):
            self._remove_event(e["id"])
            
        evt_data = data.get("events", [])
        if not evt_data:
            self._add_empty_event()
            self._add_empty_event()
            return

        self.event_counter = 0
        self.events.clear()
        
        for item in evt_data:
            self._add_empty_event()
            last_ev = self.events[-1]
            last_ev["year"].setValue(item.get("year", 2000))
            last_ev["text"].setText(item.get("text", ""))
