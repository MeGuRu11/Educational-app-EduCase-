# ui/task_constructor/constructor_dialog.py
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QWidget, QStackedWidget,
    QPushButton, QSplitter, QLabel, QFrame
)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QIcon, QMouseEvent

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon
from ui.components.dialog import ConfirmDialog
from .type_selector import TypeSelector
from .preview_panel import PreviewPanel
from .editors.single_choice import SingleChoiceEditor
from .editors.multi_choice import MultiChoiceEditor
from .editors.text_input import TextInputEditor
from .editors.ordering import OrderingEditor
from .editors.matching import MatchingEditor
from .editors.form_fill import FormFillEditor
from .editors.calculation import CalculationEditor
from .editors.image_annotation import ImageAnnotationEditor
from .editors.timeline import TimelineEditor
from .editors.table_input import TableInputEditor
from .editors.document_editor import DocumentEditor
from .editors.branching import BranchingEditor
from .base_editor import AbstractTaskEditor

class ConstructorDialog(QDialog):
    """
    Главный 3-панельный диалог конструктора заданий.
    """
    def __init__(self, parent=None, task_data=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setWindowTitle("Конструктор заданий EduCase")
        self.setMinimumSize(900, 600)
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setStyleSheet(f"background: {COLORS['bg_base']}; border: 1px solid {COLORS['stroke_control']};")
        
        self._dragging = False
        self._drag_start_pos = QPoint()

        self.task_data = task_data or {}
        
        # Debounce timer для предпросмотра
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(300)
        self.preview_timer.timeout.connect(self._do_update_preview)
        
        self._build_ui()
        self._connect_signals()
        
        # Инициализация
        initial_type = self.task_data.get("task_type", "single_choice")
        self.type_selector.set_active_type(initial_type)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ── Топбар / Header ──
        header = QWidget()
        header.setStyleSheet(f"background: {COLORS['bg_elevated']}; border-bottom: 1px solid {COLORS['stroke_divider']};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        
        title_lbl = QLabel("🛠 Редактор задания")
        title_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['text_primary']};")
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; padding: 6px 16px;")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save = QPushButton("Сохранить задание")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']}; color: white;
                border-radius: 6px; padding: 6px 16px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {COLORS['accent_hover']}; }}
        """)
        
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_cancel)
        header_layout.addWidget(self.btn_save)
        
        # Разделитель
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"color: {COLORS['stroke_divider']}; margin: 0 8px;")
        header_layout.addWidget(sep)
        
        # Контролы окна
        from ui.components.window_controls import WindowControls
        self.window_controls = WindowControls(show_maximize=True)
        self.window_controls.minimized.connect(self.showMinimized)
        self.window_controls.maximized.connect(self._toggle_maximize)
        self.window_controls.closed.connect(self.reject)
        header_layout.addWidget(self.window_controls)
        
        main_layout.addWidget(header)
        
        # ── Основное пространство ──
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {COLORS['stroke_divider']};
                width: 1px;
            }}
        """)
        
        # 1. Левая панель: Типы
        self.type_selector = TypeSelector()
        self.splitter.addWidget(self.type_selector)
        
        # 2. Центральная панель: Редакторы
        self.editor_stack = QStackedWidget()
        self.editor_stack.setStyleSheet(f"background: {COLORS['bg_base']};")
        
        # Словарь редакторов
        self.editors = {
            "single_choice": SingleChoiceEditor(),
            "multi_choice": MultiChoiceEditor(),
            "text_input": TextInputEditor(),
            "ordering": OrderingEditor(),
            "matching": MatchingEditor(),
            "form_fill": FormFillEditor(),
            "calculation": CalculationEditor(),
            "image_annotation": ImageAnnotationEditor(),
            "timeline": TimelineEditor(),
            "table_input": TableInputEditor(),
            "document_editor": DocumentEditor(),
            "branching": BranchingEditor(),
        }
        
        # Dummy для нереализованных типов
        self.dummy_editor = AbstractTaskEditor()
        
        # Заполняем стэк
        for editor in self.editors.values():
            self.editor_stack.addWidget(editor)
        self.editor_stack.addWidget(self.dummy_editor)
        
        self.splitter.addWidget(self.editor_stack)
        
        # 3. Правая панель: Предпросмотр
        self.preview_panel = PreviewPanel()
        self.splitter.addWidget(self.preview_panel)
        
        # Размеры панелей (пропорции ~ 20% / 50% / 30%)
        self.splitter.setSizes([200, 550, 350])
        self.splitter.setStretchFactor(0, 0) # type selector fixed
        self.splitter.setStretchFactor(1, 1) # editor grows
        self.splitter.setStretchFactor(2, 0) # preview fixed width ish
        
        main_layout.addWidget(self.splitter)
        
        # Сохранение текущего типа
        self.current_type = None

    def _connect_signals(self):
        self.type_selector.type_selected.connect(self._on_type_selected)
        
        for editor in self.editors.values():
            editor.data_changed.connect(self._schedule_preview_update)
        self.dummy_editor.data_changed.connect(self._schedule_preview_update)
        
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.btn_save.clicked.connect(self._on_save)

    def _on_type_selected(self, task_type_id: str):
        self.current_type = task_type_id
        
        if task_type_id in self.editors:
            # Переключаемся на нужный редактор
            self.editor_stack.setCurrentWidget(self.editors[task_type_id])
        else:
            # Показываем пустую заглушку для нереализованных типов
            self.editor_stack.setCurrentWidget(self.dummy_editor)
            
        self._schedule_preview_update()

    def _schedule_preview_update(self):
        self.preview_timer.start()

    def _do_update_preview(self):
        if not self.current_type:
            return
        
        # Получаем данные из активного редактора
        active_editor = self.editor_stack.currentWidget()
        data = active_editor.get_data()
        
        self.preview_panel.update_preview(self.current_type, data)

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() < 60: # Только за шапку
                self._dragging = True
                self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_start_pos)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._dragging = False
        super().mouseReleaseEvent(event)     

    def _on_cancel(self):
        dlg = ConfirmDialog(
            title="Отмена",
            text="Вы уверены, что хотите закрыть редактор? Все несохранённые изменения будут потеряны.",
            parent=self
        )
        if dlg.exec():
            self.reject()

    def _on_save(self):
        # Валидация + сбор данных + return
        active_editor = self.editor_stack.currentWidget()
        data = active_editor.get_data()
        data["task_type"] = self.current_type
        
        self.task_data = data
        self.accept()
