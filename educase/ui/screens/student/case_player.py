# ui/screens/student/case_player.py
"""
Экран прохождения кейса студентом.
Показывает задания последовательно с прогрессом, таймером,
автосохранением и обратной связью.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QStackedWidget, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QFont, QMouseEvent

from ui.styles.theme import COLORS
from ui.components.window_controls import WindowControls


# Реестр виджетов заданий
WIDGET_REGISTRY: dict[str, type] = {}


def _lazy_load_registry():
    """Ленивая загрузка виджетов — чтобы не было циклических импортов."""
    if WIDGET_REGISTRY:
        return
    from ui.task_widgets.single_choice_widget import SingleChoiceWidget
    from ui.task_widgets.multi_choice_widget import MultiChoiceWidget
    from ui.task_widgets.text_input_widget import TextInputWidget
    from ui.task_widgets.form_fill_widget import FormFillWidget
    from ui.task_widgets.ordering_widget import OrderingWidget
    from ui.task_widgets.matching_widget import MatchingWidget
    from ui.task_widgets.calculation_widget import CalculationWidget
    from ui.task_widgets.image_annotation_widget import ImageAnnotationWidget
    from ui.task_widgets.timeline_widget import TimelineWidget
    from ui.task_widgets.table_input_widget import TableInputWidget
    from ui.task_widgets.document_widget import DocumentWidget
    from ui.task_widgets.branching_widget import BranchingWidget

    WIDGET_REGISTRY.update({
        "single_choice": SingleChoiceWidget,
        "multi_choice": MultiChoiceWidget,
        "text_input": TextInputWidget,
        "form_fill": FormFillWidget,
        "ordering": OrderingWidget,
        "matching": MatchingWidget,
        "calculation": CalculationWidget,
        "image_annotation": ImageAnnotationWidget,
        "timeline": TimelineWidget,
        "table_input": TableInputWidget,
        "document_editor": DocumentWidget,
        "branching": BranchingWidget,
    })


class CasePlayer(QDialog):
    """
    Полноэкранный плеер прохождения кейса.

    Принимает:
        case_data: dict с ключами name, tasks (список заданий), time_limit_min
        attempt_service: AttemptService для сохранения ответов
        attempt_id: ID текущей попытки
    """

    def __init__(self, case_data: dict, attempt_service=None,
                 attempt_id: int = 0, parent=None):
        super().__init__(parent)
        _lazy_load_registry()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setWindowTitle(case_data.get("name", "Прохождение кейса"))
        self.setMinimumSize(900, 600)
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setStyleSheet(f"background: {COLORS['bg_base']};")

        self._case = case_data
        self._attempt_service = attempt_service
        self._attempt_id = attempt_id
        self._tasks = case_data.get("tasks", [])
        self._current_idx = 0
        self._elapsed_seconds = 0
        self._paused = False

        self._dragging = False
        self._drag_start_pos = QPoint()

        self._build_ui()
        self._setup_timers()

        if self._tasks:
            self._show_task(0)

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Header ──
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['bg_elevated']};
                border-bottom: 1px solid {COLORS['stroke_divider']};
            }}
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 4, 0)
        h_layout.setSpacing(16)

        # Название кейса
        self.lbl_case_name = QLabel(self._case.get("name", "Кейс"))
        self.lbl_case_name.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.lbl_case_name.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        h_layout.addWidget(self.lbl_case_name)

        h_layout.addStretch()

        # Прогресс X / N
        self.lbl_progress = QLabel("1 / 1")
        self.lbl_progress.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px; border: none;
        """)
        h_layout.addWidget(self.lbl_progress)

        # Таймер
        self.lbl_timer = QLabel("00:00")
        self.lbl_timer.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px; font-family: 'Consolas';
            border: none;
        """)
        h_layout.addWidget(self.lbl_timer)

        # Пауза
        btn_pause = QPushButton("⏸")
        btn_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pause.setFixedSize(32, 32)
        btn_pause.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 4px;
                color: {COLORS['text_secondary']};
                font-size: 16px;
            }}
            QPushButton:hover {{ background: {COLORS['state_hover']}; }}
        """)
        btn_pause.clicked.connect(self._toggle_pause)
        h_layout.addWidget(btn_pause)

        # Window controls
        wc = WindowControls(show_maximize=True)
        wc.minimized.connect(self.showMinimized)
        wc.maximized.connect(self._toggle_maximize)
        wc.closed.connect(self._on_close)
        h_layout.addWidget(wc)

        main.addWidget(header)

        # ── Progress bar ──
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background: {COLORS['stroke_divider']};
            }}
            QProgressBar::chunk {{
                background: {COLORS['accent']};
                border-radius: 2px;
            }}
        """)
        main.addWidget(self.progress_bar)

        # ── Task content area ──
        self.task_stack = QStackedWidget()
        main.addWidget(self.task_stack, stretch=1)

        # Feedback panel не используется — результаты только в конце

        # ── Bottom bar ──
        bottom = QWidget()
        bottom.setFixedHeight(64)
        bottom.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['bg_elevated']};
                border-top: 1px solid {COLORS['stroke_divider']};
            }}
        """)
        b_layout = QHBoxLayout(bottom)
        b_layout.setContentsMargins(20, 0, 20, 0)
        b_layout.setSpacing(12)

        btn_style_secondary = f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['stroke_control']};
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background: {COLORS['state_hover']}; }}
        """
        btn_style_primary = f"""
            QPushButton {{
                background: {COLORS['accent']};
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background: #1565C0; }}
            QPushButton:disabled {{
                background: {COLORS['stroke_control']};
                color: {COLORS['text_disabled']};
            }}
        """

        self.btn_prev = QPushButton("← Назад")
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setStyleSheet(btn_style_secondary)
        self.btn_prev.clicked.connect(self._go_prev)
        b_layout.addWidget(self.btn_prev)

        self.btn_hint = QPushButton("💡 Подсказка")
        self.btn_hint.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hint.setStyleSheet(btn_style_secondary)
        self.btn_hint.clicked.connect(self._show_hint)
        b_layout.addWidget(self.btn_hint)

        b_layout.addStretch()

        # Кнопка "Проверить" убрана — результаты раскрываются только после завершения

        self.btn_next = QPushButton("Далее →")
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setStyleSheet(btn_style_primary)
        self.btn_next.clicked.connect(self._go_next)
        b_layout.addWidget(self.btn_next)

        main.addWidget(bottom)

        # ── Pause overlay ──
        self.pause_overlay = QWidget(self)
        self.pause_overlay.setStyleSheet(f"""
            QWidget {{
                background: rgba(0, 0, 0, 180);
            }}
        """)
        self.pause_overlay.hide()

        pause_inner = QVBoxLayout(self.pause_overlay)
        pause_inner.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pause_label = QLabel("⏸ Пауза")
        pause_label.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
        pause_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pause_inner.addWidget(pause_label)

        btn_resume = QPushButton("Продолжить")
        btn_resume.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_resume.setFixedSize(200, 48)
        btn_resume.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{ background: #1565C0; }}
        """)
        btn_resume.clicked.connect(self._toggle_pause)
        pause_inner.addWidget(btn_resume, alignment=Qt.AlignmentFlag.AlignCenter)

    def _setup_timers(self):
        # Таймер обновления UI
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(1000)
        self._tick_timer.timeout.connect(self._on_tick)
        self._tick_timer.start()

        # Автосохранение каждые 30 сек
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(30000)
        self._autosave_timer.timeout.connect(self._autosave)
        self._autosave_timer.start()

    def _on_tick(self):
        if not self._paused:
            self._elapsed_seconds += 1
            mins = self._elapsed_seconds // 60
            secs = self._elapsed_seconds % 60
            self.lbl_timer.setText(f"{mins:02d}:{secs:02d}")

            # Проверка лимита времени
            time_limit = self._case.get("time_limit_min", 0)
            if time_limit and self._elapsed_seconds >= time_limit * 60:
                self._finish_case()

    def _show_task(self, idx: int):
        """Показывает задание по индексу."""
        if idx < 0 or idx >= len(self._tasks):
            return

        self._current_idx = idx
        task = self._tasks[idx]
        task_type = task.get("task_type", "")

        # Создаём виджет если его ещё нет в стеке
        while self.task_stack.count() <= idx:
            self.task_stack.addWidget(QWidget())

        # Проверяем, нужно ли заменить widget
        current_widget = self.task_stack.widget(idx)
        if not hasattr(current_widget, 'get_answer'):
            widget_cls = WIDGET_REGISTRY.get(task_type)
            if widget_cls:
                widget = widget_cls()
                widget.set_task(task)
                self.task_stack.removeWidget(current_widget)
                current_widget.deleteLater()
                self.task_stack.insertWidget(idx, widget)

        self.task_stack.setCurrentIndex(idx)
        self._update_navigation()

    def _update_navigation(self):
        total = len(self._tasks)
        idx = self._current_idx

        self.lbl_progress.setText(f"{idx + 1} / {total}")
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(idx + 1)

        self.btn_prev.setEnabled(idx > 0)
        self.btn_next.setText("Завершить ✓" if idx == total - 1 else "Далее →")

        # Подсказка
        task = self._tasks[idx]
        self.btn_hint.setVisible(bool(task.get("hint")))

    def _go_prev(self):
        self._save_current_answer()
        self._show_task(self._current_idx - 1)

    def _go_next(self):
        self._save_current_answer()
        if self._current_idx >= len(self._tasks) - 1:
            self._finish_case()
        else:
            self._show_task(self._current_idx + 1)

    def _save_current_answer(self):
        """Сохраняет текущий ответ (без проверки — проверка только в конце)."""
        widget = self.task_stack.currentWidget()
        if not hasattr(widget, 'get_answer'):
            return
        answer = widget.get_answer()
        if answer and self._attempt_service and self._attempt_id:
            task = self._tasks[self._current_idx]
            self._attempt_service.save_answer(
                self._attempt_id, task.get("id", 0), answer
            )



    def _show_hint(self):
        task = self._tasks[self._current_idx]
        hint = task.get("hint", "")
        if hint:
            from ui.components.dialog import ConfirmDialog
            dlg = ConfirmDialog(self, "Подсказка", hint)
            dlg.btn_cancel.hide()
            dlg.btn_ok.setText("Понятно")
            dlg.exec()

    def _toggle_pause(self):
        self._paused = not self._paused
        self.pause_overlay.setVisible(self._paused)
        if self._paused:
            self.pause_overlay.setGeometry(self.rect())
            self.pause_overlay.raise_()

    def _autosave(self):
        """Автосохранение текущего ответа."""
        if self._paused or not self._attempt_service:
            return

        widget = self.task_stack.currentWidget()
        if hasattr(widget, 'get_answer'):
            answer = widget.get_answer()
            if answer:
                task = self._tasks[self._current_idx]
                self._attempt_service.save_answer(
                    self._attempt_id, task.get("id", 0), answer
                )

    def _finish_case(self):
        """Завершает прохождение кейса."""
        self._tick_timer.stop()
        self._autosave_timer.stop()

        if self._attempt_service and self._attempt_id:
            self._attempt_service.finish(self._attempt_id)

        self.accept()

    def _on_close(self):
        if self._attempt_service and self._attempt_id:
            self._attempt_service.pause(self._attempt_id, self._elapsed_seconds)
        self.reject()

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._paused:
            self.pause_overlay.setGeometry(self.rect())

    # ── Перетаскивание окна ──
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() < 56:
            self._dragging = True
            self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_start_pos)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        super().mouseReleaseEvent(event)
