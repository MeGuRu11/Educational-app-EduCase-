# ui/task_constructor/scenario_builder/node_edit_dialog.py
"""
Диалог редактирования содержимого узла сценария.
Позволяет настроить описание, и для узлов типа «question» — привязать тип задания.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QComboBox,
    QGroupBox, QFormLayout, QFrame, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon


# Типы заданий доступные для привязки к узлу «Вопрос»
ATTACHABLE_TASKS = [
    {"id": "", "name": "— Без задания —", "icon": "close"},
    {"id": "single_choice", "name": "Один ответ", "icon": "check_circle"},
    {"id": "multi_choice", "name": "Несколько ответов", "icon": "check"},
    {"id": "text_input", "name": "Ввод текста", "icon": "edit"},
    {"id": "form_fill", "name": "Заполнение формы", "icon": "document"},
    {"id": "ordering", "name": "Сортировка", "icon": "sort"},
    {"id": "matching", "name": "Соответствия", "icon": "module"},
    {"id": "calculation", "name": "Вычисление", "icon": "formula"},
    {"id": "image_annotation", "name": "Зоны на изображении", "icon": "image"},
    {"id": "timeline", "name": "Таймлайн", "icon": "timeline"},
    {"id": "table_input", "name": "Таблица", "icon": "table"},
    {"id": "document_editor", "name": "Анализ документа", "icon": "book"},
]


class NodeEditDialog(QDialog):
    """
    Диалог редактирования узла.
    Для всех типов: заголовок + описание.
    Для «question»: дополнительно выбор типа задания + настройка вариантов.
    """

    def __init__(self, node_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование узла")
        self.setMinimumSize(500, 400)
        self.setMaximumSize(600, 550)
        self.setStyleSheet(f"""
            QDialog {{
                background: {COLORS['bg_base']};
            }}
        """)

        self._node_data = dict(node_data)  # копия
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ── Заголовок ──
        lbl_title = QLabel("Заголовок узла")
        lbl_title.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']};")
        layout.addWidget(lbl_title)

        self.edit_title = QLineEdit()
        self.edit_title.setPlaceholderText("Название узла...")
        self.edit_title.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 6px;
                padding: 8px 12px;
                background: {COLORS['bg_layer']};
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
            QLineEdit:focus {{ border-color: {COLORS['accent']}; }}
        """)
        layout.addWidget(self.edit_title)

        # ── Описание ──
        lbl_desc = QLabel("Описание ситуации")
        lbl_desc.setStyleSheet(f"font-weight: bold; color: {COLORS['text_primary']};")
        layout.addWidget(lbl_desc)

        self.edit_desc = QTextEdit()
        self.edit_desc.setPlaceholderText(
            "Опишите клиническую ситуацию, которую увидит студент...\n\n"
            "Например:\n"
            "«Пациент 45 лет поступил с жалобами на боль в правом подреберье, "
            "тошноту. Температура 38.2°C, живот болезненный при пальпации.»"
        )
        self.edit_desc.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 6px;
                padding: 8px;
                background: {COLORS['bg_layer']};
                color: {COLORS['text_primary']};
                font-size: 13px;
            }}
            QTextEdit:focus {{ border-color: {COLORS['accent']}; }}
        """)
        self.edit_desc.setMinimumHeight(100)
        layout.addWidget(self.edit_desc, stretch=1)

        # ── Привязка задания (только для question) ──
        self.task_group = QGroupBox("Привязанное задание")
        self.task_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }}
        """)
        tg_layout = QVBoxLayout(self.task_group)
        tg_layout.setSpacing(8)

        hint = QLabel("Выберите тип задания, которое студент должен решить в этом узле:")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: normal;")
        tg_layout.addWidget(hint)

        self.combo_task = QComboBox()
        self.combo_task.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 4px;
                padding: 6px 12px;
                background: {COLORS['bg_layer']};
                color: {COLORS['text_primary']};
            }}
            QComboBox:focus {{ border-color: {COLORS['accent']}; }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
        """)
        for t in ATTACHABLE_TASKS:
            self.combo_task.addItem(t["name"], t["id"])
        tg_layout.addWidget(self.combo_task)

        # Подсказка для вариантов (ребра = варианты ответа)
        edge_hint = QLabel(
            "💡 Варианты ответа — это рёбра (стрелки), выходящие из этого узла.\n"
            "Каждое ребро = один вариант ответа. Подпишите рёбра текстом вариантов."
        )
        edge_hint.setWordWrap(True)
        edge_hint.setStyleSheet(f"""
            color: {COLORS['accent']};
            font-size: 12px;
            font-weight: normal;
            background: {COLORS['accent']}10;
            border: 1px solid {COLORS['accent']}30;
            border-radius: 4px;
            padding: 8px;
        """)
        tg_layout.addWidget(edge_hint)

        layout.addWidget(self.task_group)

        # Скрываем блок задания для не-question типов
        node_type = self._node_data.get("type", "scene")
        self.task_group.setVisible(node_type == "question")

        # ── Кнопки ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("Отмена")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 4px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{ background: {COLORS['state_hover']}; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_save = QPushButton("Сохранить")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{ background: #1565C0; }}
        """)
        btn_save.clicked.connect(self.accept)
        btn_row.addWidget(btn_save)

        layout.addLayout(btn_row)

    def _load_data(self):
        """Заполняет поля данными узла."""
        self.edit_title.setText(self._node_data.get("title", ""))
        self.edit_desc.setPlainText(self._node_data.get("description", ""))

        # Задание
        task_type = self._node_data.get("task_type", "")
        idx = self.combo_task.findData(task_type)
        if idx >= 0:
            self.combo_task.setCurrentIndex(idx)

    def get_data(self) -> dict:
        """Возвращает обновлённые данные узла."""
        self._node_data["title"] = self.edit_title.text().strip()
        self._node_data["description"] = self.edit_desc.toPlainText().strip()
        self._node_data["task_type"] = self.combo_task.currentData() or ""
        return self._node_data
