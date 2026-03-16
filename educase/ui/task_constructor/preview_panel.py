# ui/task_constructor/preview_panel.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from ui.components.empty_state import EmptyState
from ui.task_constructor.type_selector import TASK_TYPES

class PreviewPanel(QWidget):
    """
    Правая панель для предпросмотра TaskWidget (как увидит студент).
    Принимает данные задания и генерирует или обновляет виджет.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(16)
        
        # Общий фон панели
        self.setStyleSheet(f"background: {COLORS['bg_layer']}; border-radius: 8px;")
        
        # Заголовок
        header = QLabel("Предпросмотр")
        header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_primary']};")
        self.main_layout.addWidget(header)
        
        # Враппер под превью
        self.preview_container = QFrame()
        self.preview_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: 8px;
            }}
        """)
        self.pc_layout = QVBoxLayout(self.preview_container)
        self.pc_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.preview_container, stretch=1)
        
        # Заглушка (EmptyState)
        self.empty_state = EmptyState(
            icon_name="play",
            title="Предпросмотр",
            subtitle="Здесь появится то, что увидит студент",
            parent=self.preview_container
        )
        self.pc_layout.addWidget(self.empty_state)
        
        # Позже здесь будет экземпляр BaseTaskWidget
        self.current_widget = None

    def update_preview(self, task_type: str, data: dict):
        """
        Обновляет превью. Пока нет реальных виджетов - показываем заглушку,
        но перерисовываем её для демонстрации.
        """
        # Пока нет TaskWidget реализаций, просто меняем текст заглушки
        # В будущем здесь будем создавать/обновлять виджет на основе task_type
        
        if self.current_widget:
            self.pc_layout.removeWidget(self.current_widget)
            self.current_widget.deleteLater()
            self.current_widget = None
            
        self.empty_state.show()
        # Временный хак: показываем тип задания и начало текста в заглушке
        # Извлекаем чистый текст из HTML
        from PySide6.QtGui import QTextDocument
        doc = QTextDocument()
        doc.setHtml(data.get("body", ""))
        plain_text = doc.toPlainText()
        
        text_preview = plain_text[:50]
        if len(plain_text) > 50:
            text_preview += "..."
            
        type_name = next((t["name"] for t in TASK_TYPES if t["id"] == task_type), task_type)
        self.empty_state.subtitle_lbl.setText(f"Тип: {type_name}\n{text_preview}")
