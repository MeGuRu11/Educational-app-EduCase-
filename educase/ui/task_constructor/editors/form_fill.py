import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QFrame)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon
from ..base_editor import AbstractTaskEditor

class FormFillEditor(AbstractTaskEditor):
    """
    Редактор для задания типа "Заполнение формы" (form_fill).
    Ищет в тексте токены вида [1], [2] и предлагает задать правильные ответы.
    """
    def __init__(self, parent=None):
        self.tokens = []
        self.token_widgets = {}
        super().__init__(parent)
        
        # Подключаемся к сигналу изменения текста
        self.body_editor.text_changed.connect(self._parse_tokens)
        
    def _setup_specific_ui(self, layout: QVBoxLayout):
        self.options_group = QWidget()
        self.options_layout = QVBoxLayout(self.options_group)
        self.options_layout.setContentsMargins(0, 16, 0, 0)
        self.options_layout.setSpacing(8)
        
        title = QLabel("Ответы для пропусков (используйте [1], [2] в условии)")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']};")
        self.options_layout.addWidget(title)
        
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.options_layout.addWidget(self.list_container)
        
        layout.addWidget(self.options_group)
        self._rebuild_token_inputs()

    def _parse_tokens(self):
        # Извлекаем plain text из редактора (чтобы не парсить HTML-сущности)
        html = self.body_editor.get_html()
        
        from PySide6.QtGui import QTextDocument
        doc = QTextDocument()
        doc.setHtml(html)
        plain_text = doc.toPlainText()
        
        # Простой поиск токенов вида [число] или [слово]
        tokens = list(set(re.findall(r'\[(\w+)\]', plain_text)))
        tokens.sort()
        
        if sorted(self.tokens) == tokens:
            return  # Нет изменений в списке токенов
            
        self.tokens = tokens
        self._rebuild_token_inputs()
        
    def _rebuild_token_inputs(self):
        # Если список токенов пуст, покажем подсказку
        if not self.tokens:
            # Очищаем все
            self._clear_layout()
            self.token_widgets.clear()
            
            lbl = QLabel("Добавьте в текст условия пропуски в формате [1], [word] и т.д.")
            lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-style: italic;")
            lbl.setWordWrap(True)
            self.list_layout.addWidget(lbl)
            return

        # Удаляем виджеты токенов, которые исчезли из текста
        to_remove = [t for t in self.token_widgets if t not in self.tokens]
        for t in to_remove:
            widget_row = self.token_widgets[t]["row"]
            self.list_layout.removeWidget(widget_row)
            widget_row.deleteLater()
            del self.token_widgets[t]
            
        # Удаляем подсказку, если она есть
        for i in reversed(range(self.list_layout.count())):
            item = self.list_layout.itemAt(i)
            if item is None:
                continue
            w = item.widget()
            if w and isinstance(w, QLabel) and "Добавьте в текст" in w.text():
                self.list_layout.removeWidget(w)
                w.deleteLater()

        # Добавляем новые токены
        for token in self.tokens:
            if token in self.token_widgets:
                continue # Уже есть, не трогаруем
                
            row = QFrame()
            row.setStyleSheet(f"background: {COLORS['bg_elevated']}; border: 1px solid {COLORS['stroke_divider']}; border-radius: 6px;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 8, 12, 8)
            row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            
            lbl_token = QLabel(f"[{token}]")
            lbl_token.setStyleSheet(f"font-weight: bold; color: {COLORS['accent']};")
            
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Правильный ответ для [{token}]")
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
            
            row_layout.addWidget(lbl_token, alignment=Qt.AlignmentFlag.AlignVCenter)
            row_layout.addWidget(line_edit, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)
            
            self.list_layout.addWidget(row)
            self.token_widgets[token] = {"row": row, "input": line_edit}
            
        self.data_changed.emit()

    def _clear_layout(self):
        for i in reversed(range(self.list_layout.count())): 
            w = self.list_layout.itemAt(i).widget()
            if w:
                self.list_layout.removeWidget(w)
                w.deleteLater()

    def get_specific_data(self) -> dict:
        answers = {}
        for token, wdg in self.token_widgets.items():
            text = wdg["input"].text().strip()
            if text:
                answers[token] = text
        return {"answers": answers}

    def set_specific_data(self, data: dict):
        answers = data.get("answers", {})
        for token, text in answers.items():
            if token in self.token_widgets:
                self.token_widgets[token]["input"].setText(text)
