# ui/task_constructor/editors/document_editor.py
"""
Редактор для задания типа «Анализ документа».
Преподаватель загружает документ и добавляет вопросы по нему.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFileDialog, QFrame
)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon
from ..base_editor import AbstractTaskEditor


class DocumentEditor(AbstractTaskEditor):
    """
    Редактор «Анализ документа»: загрузка файла + список вопросов с ответами.
    """

    def __init__(self, parent=None):
        self.document_path = ""
        self.questions = []  # [{id, widget, q_edit, a_edit}]
        self.q_counter = 0
        super().__init__(parent)

    def _setup_specific_ui(self, layout: QVBoxLayout):
        group = QWidget()
        g_layout = QVBoxLayout(group)
        g_layout.setContentsMargins(0, 16, 0, 0)
        g_layout.setSpacing(12)

        # ── Заголовок + кнопка загрузки ──
        top_row = QHBoxLayout()
        title = QLabel("Документ для анализа")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']};")
        top_row.addWidget(title)
        top_row.addStretch()

        self.btn_load = QPushButton("Загрузить документ")
        self.btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg_layer']};
                color: {COLORS['accent']};
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{ background: {COLORS['state_hover']}; border-color: {COLORS['accent']}; }}
        """)
        self.btn_load.clicked.connect(self._load_document)
        top_row.addWidget(self.btn_load)

        g_layout.addLayout(top_row)

        # ── Инфо о загруженном файле ──
        self.file_row = QWidget()
        file_row_layout = QHBoxLayout(self.file_row)
        file_row_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_file = QLabel("Файл не загружен")
        self.lbl_file.setStyleSheet(f"color: {COLORS['text_secondary']};")
        file_row_layout.addWidget(self.lbl_file, stretch=1)

        self.btn_remove_file = QPushButton()
        self.btn_remove_file.setIcon(get_icon("delete", COLORS["error"], 18))
        self.btn_remove_file.setFixedSize(28, 28)
        self.btn_remove_file.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_remove_file.setStyleSheet("border: none; background: transparent;")
        self.btn_remove_file.clicked.connect(self._remove_document)
        self.btn_remove_file.hide()
        file_row_layout.addWidget(self.btn_remove_file)

        g_layout.addWidget(self.file_row)

        # ── Вопросы ──
        q_title = QLabel("Вопросы к документу")
        q_title.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']}; margin-top: 8px;")
        g_layout.addWidget(q_title)

        self.q_container = QWidget()
        self.q_layout = QVBoxLayout(self.q_container)
        self.q_layout.setContentsMargins(0, 0, 0, 0)
        self.q_layout.setSpacing(8)
        g_layout.addWidget(self.q_container)

        self.btn_add_q = QPushButton("+ Добавить вопрос")
        self.btn_add_q.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_q.setStyleSheet(f"""
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
        self.btn_add_q.clicked.connect(self._add_question)
        g_layout.addWidget(self.btn_add_q)

        layout.addWidget(group)

        # Начальные вопросы
        self._add_question()

    def _load_document(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Выберите документ", "",
            "Documents (*.pdf *.docx *.txt *.jpg *.jpeg *.png *.bmp)"
        )
        if file_name:
            self.document_path = file_name
            short = file_name.split("/")[-1].split("\\")[-1]
            self.lbl_file.setText(f"📄 {short}")
            self.lbl_file.setStyleSheet(f"color: {COLORS['text_primary']};")
            self.btn_remove_file.show()
            self.data_changed.emit()

    def _remove_document(self):
        self.document_path = ""
        self.lbl_file.setText("Файл не загружен")
        self.lbl_file.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.btn_remove_file.hide()
        self.data_changed.emit()

    def _add_question(self):
        q_id = f"q_{self.q_counter}"
        self.q_counter += 1

        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: 6px;
            }}
        """)
        r_layout = QVBoxLayout(row)
        r_layout.setContentsMargins(12, 8, 12, 8)
        r_layout.setSpacing(6)

        # Верхняя строка: номер + удаление
        top = QHBoxLayout()
        lbl_num = QLabel(f"Вопрос {len(self.questions) + 1}")
        lbl_num.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: bold; border: none;")
        top.addWidget(lbl_num)
        top.addStretch()

        btn_del = QPushButton()
        btn_del.setIcon(get_icon("delete", COLORS["error"], 18))
        btn_del.setFixedSize(28, 28)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("border: none; background: transparent;")
        btn_del.clicked.connect(lambda: self._remove_question(q_id))
        top.addWidget(btn_del)
        r_layout.addLayout(top)

        q_edit = QLineEdit()
        q_edit.setPlaceholderText("Текст вопроса...")
        q_edit.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 4px;
                padding: 6px;
                background: {COLORS['bg_layer']};
                color: {COLORS['text_primary']};
            }}
        """)
        q_edit.textChanged.connect(lambda: self.data_changed.emit())
        r_layout.addWidget(q_edit)

        a_edit = QLineEdit()
        a_edit.setPlaceholderText("Ожидаемый ответ...")
        a_edit.setStyleSheet(q_edit.styleSheet())
        a_edit.textChanged.connect(lambda: self.data_changed.emit())
        r_layout.addWidget(a_edit)

        self.q_layout.addWidget(row)
        self.questions.append({
            "id": q_id, "widget": row,
            "q_edit": q_edit, "a_edit": a_edit
        })
        self.data_changed.emit()

    def _remove_question(self, q_id: str):
        if len(self.questions) <= 1:
            return
        target = next((q for q in self.questions if q["id"] == q_id), None)
        if target:
            self.q_layout.removeWidget(target["widget"])
            target["widget"].deleteLater()
            self.questions.remove(target)
            self.data_changed.emit()

    def get_specific_data(self) -> dict:
        q_data = []
        for q in self.questions:
            text = q["q_edit"].text().strip()
            if text:
                q_data.append({
                    "question": text,
                    "answer": q["a_edit"].text().strip()
                })
        return {
            "document_path": self.document_path,
            "questions": q_data
        }

    def set_specific_data(self, data: dict):
        self.document_path = data.get("document_path", "")
        if self.document_path:
            short = self.document_path.split("/")[-1].split("\\")[-1]
            self.lbl_file.setText(f"📄 {short}")
            self.lbl_file.setStyleSheet(f"color: {COLORS['text_primary']};")
            self.btn_remove_file.show()

        # Очищаем все вопросы (обходим ограничение min-1)
        for q in list(self.questions):
            self.q_layout.removeWidget(q["widget"])
            q["widget"].deleteLater()

        self.q_counter = 0
        self.questions.clear()

        for item in data.get("questions", []):
            self._add_question()
            last = self.questions[-1]
            last["q_edit"].setText(item.get("question", ""))
            last["a_edit"].setText(item.get("answer", ""))
