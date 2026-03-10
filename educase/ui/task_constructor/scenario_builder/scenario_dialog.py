# ui/task_constructor/scenario_builder/scenario_dialog.py
"""
Полноэкранный диалог визуального конструктора сценариев.
Содержит GraphView, панель инструментов и кнопки сохранения.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont, QMouseEvent

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon
from ui.components.window_controls import WindowControls
from .graph_scene import GraphScene
from .graph_view import GraphView
from .node_item import NODE_TYPES


class ScenarioBuilderDialog(QDialog):
    """
    Полноэкранный визуальный редактор сценариев с ветвлениями.
    """

    def __init__(self, parent=None, scenario_data=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setWindowTitle("Конструктор сценариев")
        self.setMinimumSize(900, 600)
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setStyleSheet(f"background: {COLORS['bg_base']}; border: 1px solid {COLORS['stroke_control']};")

        self._dragging = False
        self._drag_start_pos = QPoint()

        self._build_ui()

        # Загружаем данные если есть
        if scenario_data and (scenario_data.get("nodes") or scenario_data.get("edges")):
            self.scene.load_data(scenario_data)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Заголовок ──
        header = QWidget()
        header.setFixedHeight(48)
        header.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['bg_elevated']};
                border-bottom: 1px solid {COLORS['stroke_divider']};
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 0, 0)
        header_layout.setSpacing(12)

        # Иконка + заголовок
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon("branch", COLORS["accent"], 22).pixmap(22, 22))
        header_layout.addWidget(icon_lbl)

        title = QLabel("Конструктор сценариев")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Кнопки действий
        btn_cancel = QPushButton("Отмена")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 4px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{ background: {COLORS['state_hover']}; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        header_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Сохранить сценарий")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: #1565C0; }}
        """)
        btn_save.clicked.connect(self._on_save)
        header_layout.addWidget(btn_save)

        # Разделитель
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedHeight(24)
        sep.setStyleSheet(f"color: {COLORS['stroke_divider']}; border: none;")
        header_layout.addWidget(sep)

        # Контролы окна
        self.window_controls = WindowControls(show_maximize=True)
        self.window_controls.minimized.connect(self.showMinimized)
        self.window_controls.maximized.connect(self._toggle_maximize)
        self.window_controls.closed.connect(self.reject)
        header_layout.addWidget(self.window_controls)

        main_layout.addWidget(header)

        # ── Панель инструментов ──
        toolbar = QWidget()
        toolbar.setFixedHeight(40)
        toolbar.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['bg_layer']};
                border-bottom: 1px solid {COLORS['stroke_divider']};
            }}
        """)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(12, 0, 12, 0)
        tb_layout.setSpacing(4)

        tb_style = f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {COLORS['state_hover']};
                color: {COLORS['text_primary']};
            }}
        """

        # Кнопки добавления узлов
        for type_id, info in NODE_TYPES.items():
            btn = QPushButton(f"+ {info['label']}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(tb_style)
            btn.clicked.connect(lambda checked, t=type_id: self._add_node_center(t))
            tb_layout.addWidget(btn)

        tb_layout.addStretch()

        # Кнопки навигации
        btn_fit = QPushButton("⊞ Уместить всё")
        btn_fit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_fit.setStyleSheet(tb_style)
        btn_fit.clicked.connect(lambda: self.view.fit_all())
        tb_layout.addWidget(btn_fit)

        btn_zin = QPushButton("🔍+")
        btn_zin.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_zin.setStyleSheet(tb_style)
        btn_zin.clicked.connect(lambda: self.view.zoom_in())
        tb_layout.addWidget(btn_zin)

        btn_zout = QPushButton("🔍−")
        btn_zout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_zout.setStyleSheet(tb_style)
        btn_zout.clicked.connect(lambda: self.view.zoom_out())
        tb_layout.addWidget(btn_zout)

        # Счётчик
        self.lbl_stats = QLabel("0 узлов, 0 связей")
        self.lbl_stats.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; padding-left: 12px;")
        tb_layout.addWidget(self.lbl_stats)

        main_layout.addWidget(toolbar)

        # ── Граф ──
        self.scene = GraphScene()
        self.scene.graph_changed.connect(self._update_stats)

        self.view = GraphView()
        self.view.setScene(self.scene)
        main_layout.addWidget(self.view, stretch=1)

        # Подсказка
        hint = QLabel("Двойной клик — редактировать узел   •   Правый клик — добавить   •   Перетащите от ● к узлу — соединить   •   СКМ — пан   •   Колёсико — zoom")
        hint.setStyleSheet(f"""
            color: {COLORS['text_disabled']};
            font-size: 11px;
            padding: 6px 12px;
            background: {COLORS['bg_layer']};
            border-top: 1px solid {COLORS['stroke_divider']};
        """)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(hint)

    def _add_node_center(self, node_type: str):
        """Добавляет узел в центр видимой области."""
        center = self.view.mapToScene(self.view.viewport().rect().center())
        self.scene.add_node(
            node_type=node_type,
            x=center.x() - 90,
            y=center.y() - 35,
        )

    def _update_stats(self):
        n = len(self.scene.nodes)
        e = len(self.scene.edges)
        self.lbl_stats.setText(f"{n} узлов, {e} связей")

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def get_scenario_data(self) -> dict:
        return self.scene.get_data()

    def _on_save(self):
        """Validate graph before saving."""
        warnings = self._validate_graph()
        if warnings:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Предупреждения")
            msg.setText("Обнаружены проблемы в сценарии:")
            msg.setDetailedText("\n".join(warnings))
            msg.setInformativeText("Сохранить всё равно?")
            msg.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel)
            msg.setDefaultButton(QMessageBox.StandardButton.Save)
            if msg.exec() != QMessageBox.StandardButton.Save:
                return
        self.accept()

    def _validate_graph(self) -> list[str]:
        """Validates the graph and returns a list of warnings."""
        warnings: list[str] = []
        nodes = self.scene.nodes
        edges = self.scene.edges

        if not nodes:
            return warnings  # Пустой граф — ok

        # Проверка наличия Старта
        starts = [n for n in nodes if n.node_type == "start"]
        if not starts:
            warnings.append("⚠ Нет узла типа 'Старт'. Сценарий должен начинаться с узла 'Старт'.")

        # Проверка наличия финала
        ends = [n for n in nodes if n.node_type in ("end_success", "end_fail")]
        if not ends:
            warnings.append("⚠ Нет финального узла ('Успех' или 'Провал'). Сценарий должен иметь завершение.")

        # Проверка изолированных узлов
        connected_ids = set()
        for e in edges:
            connected_ids.add(e.source_node.node_id)
            connected_ids.add(e.target_node.node_id)

        isolated = [n for n in nodes if n.node_id not in connected_ids]
        if isolated and len(nodes) > 1:
            names = ", ".join(f'"{n.title}"' for n in isolated)
            warnings.append(f"⚠ Изолированные узлы (не соединены): {names}")

        # Проверка question без задания
        questions_no_task = [n for n in nodes if n.node_type == "question" and not n.task_type]
        if questions_no_task:
            names = ", ".join(f'"{n.title}"' for n in questions_no_task)
            warnings.append(f"ℹ Узлы-вопросы без привязанного задания: {names}")

        return warnings

    # ── Перетаскивание окна за заголовок ──
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() < 48:
            self._dragging = True
            self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_start_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._dragging = False
        super().mouseReleaseEvent(event)
