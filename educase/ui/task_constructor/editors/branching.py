# ui/task_constructor/editors/branching.py
"""
Редактор для задания типа «Ветвление сценария».
Заглушка-интерфейс, которая позволяет открыть визуальный конструктор сценариев.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon
from ..base_editor import AbstractTaskEditor


class BranchingEditor(AbstractTaskEditor):
    """
    Редактор «Ветвление сценария».
    Показывает описание и кнопку для запуска ScenarioBuilder.
    """

    def __init__(self, parent=None):
        self.scenario_data = {"nodes": [], "edges": []}
        super().__init__(parent)

    def _setup_specific_ui(self, layout: QVBoxLayout):
        group = QWidget()
        g_layout = QVBoxLayout(group)
        g_layout.setContentsMargins(0, 16, 0, 0)
        g_layout.setSpacing(16)

        # ── Описание ──
        desc_card = QWidget()
        desc_card.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: 8px;
            }}
        """)
        desc_layout = QVBoxLayout(desc_card)
        desc_layout.setContentsMargins(20, 20, 20, 20)
        desc_layout.setSpacing(12)

        icon_label = QLabel()
        icon_label.setPixmap(
            get_icon("branch", COLORS["accent"], 48).pixmap(48, 48)
        )
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_layout.addWidget(icon_label)

        title = QLabel("Конструктор сценариев")
        title.setStyleSheet(f"""
            font-size: 18px; font-weight: bold;
            color: {COLORS['text_primary']};
            border: none;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_layout.addWidget(title)

        desc = QLabel(
            "Создайте интерактивный медицинский сценарий с ветвлениями.\n"
            "Каждый узел — это ситуация или вопрос, а рёбра — возможные\n"
            "варианты действий студента. Стройте нелинейные кейсы!"
        )
        desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; border: none;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc_layout.addWidget(desc)

        g_layout.addWidget(desc_card)

        # ── Кнопка открытия ──
        self.btn_open = QPushButton("  Открыть визуальный редактор")
        self.btn_open.setIcon(get_icon("play", "#FFFFFF", 20))
        self.btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open.setFixedHeight(44)
        self.btn_open.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 6px;
                padding: 0 24px;
            }}
            QPushButton:hover {{
                background: #1565C0;
            }}
            QPushButton:pressed {{
                background: #0D47A1;
            }}
        """)
        self.btn_open.clicked.connect(self._open_scenario_builder)
        g_layout.addWidget(self.btn_open, alignment=Qt.AlignmentFlag.AlignCenter)

        # ── Мета-информация ──
        self.lbl_info = QLabel("Сценарий пуст: 0 узлов, 0 связей")
        self.lbl_info.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        g_layout.addWidget(self.lbl_info)

        g_layout.addStretch()
        layout.addWidget(group)

    def _open_scenario_builder(self):
        """
        Открывает диалог конструктора сценариев.
        Пока что — заглушка (ScenarioBuilder будет реализован позже).
        """
        try:
            from ui.task_constructor.scenario_builder.scenario_dialog import ScenarioBuilderDialog
            dlg = ScenarioBuilderDialog(
                parent=self.window(),
                scenario_data=self.scenario_data
            )
            if dlg.exec():
                self.scenario_data = dlg.get_scenario_data()
                self._update_info()
                self.data_changed.emit()
        except ImportError:
            # ScenarioBuilder ещё не реализован
            from ui.components.dialog import ConfirmDialog
            ConfirmDialog.info(
                self, "В разработке",
                "Визуальный конструктор сценариев будет доступен в следующем обновлении."
            )

    def _update_info(self):
        nodes = len(self.scenario_data.get("nodes", []))
        edges = len(self.scenario_data.get("edges", []))
        self.lbl_info.setText(f"Сценарий: {nodes} узлов, {edges} связей")

    def get_specific_data(self) -> dict:
        return {"scenario": self.scenario_data}

    def set_specific_data(self, data: dict):
        self.scenario_data = data.get("scenario", {"nodes": [], "edges": []})
        self._update_info()
