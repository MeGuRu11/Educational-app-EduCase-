# ui/windows/main_window.py
"""
Главное окно приложения (после авторизации).
Содержит Sidebar, Topbar и QStackedWidget для переключения экранов.
Управляется через EventBus (bus.navigate_to).
"""
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, 
    QApplication, QLabel
)

import app
from core.di_container import Container
from core.event_bus import bus
from ui.components.sidebar import Sidebar
from ui.components.topbar import Topbar
from ui.windows.sandbox_view import SandboxView
from ui.styles.theme import COLORS, RADIUS


class MainWindow(QWidget):
    def __init__(self, container: Container):
        super().__init__()
        self.container = container
        
        self.W, self.H = 1280, 800
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(1024, 768)
        self.resize(self.W, self.H)

        self._is_maximized = False
        self._normal_geometry = self.geometry()

        self._setup_ui()
        self._center()
        
        # Подписки на события
        bus.navigate_to.connect(self._on_navigate)
        bus.user_logged_in.connect(self._on_user_login)

    def _center(self) -> None:
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Рисуем подложку окна
        p.setBrush(QColor(COLORS["bg_base"]))
        p.setPen(Qt.PenStyle.NoPen)
        r = 0 if self._is_maximized else RADIUS["xlarge"]
        p.drawRoundedRect(0, 0, self.width(), self.height(), r, r)

        # Тонкая внешняя рамка (если не на весь экран)
        if not self._is_maximized:
            p.setPen(QColor(COLORS["stroke_card"]))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, r, r)

    def _setup_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── 1. Левая панель (Sidebar)
        self.sidebar = Sidebar()
        self.sidebar.route_selected.connect(lambda route: bus.navigate_to.emit(route, {}))
        main_layout.addWidget(self.sidebar)

        # ── 2. Правая часть (Topbar + Content)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Верхняя панель
        self.topbar = Topbar(self) # Передаем self для dragging
        self.topbar.minimized.connect(self.showMinimized)
        self.topbar.maximized.connect(self.toggle_maximize)
        self.topbar.closed.connect(self.close)
        right_layout.addWidget(self.topbar)

        # Контентная область
        self.content_stack = QStackedWidget()
        self._init_screens()
        right_layout.addWidget(self.content_stack)

        main_layout.addWidget(right_panel, stretch=1)

    def _init_screens(self) -> None:
        """Инициализация словаря экранов и добавление их в QStackedWidget."""
        self.screens: dict[str, QWidget] = {}
        
        # Заглушки для первого этапа (реализуются детально позже)
        self.screens["home"] = QLabel("Главная страница (Dashboard)")
        self.screens["cases"] = QLabel("Мои кейсы / Управление кейсами")
        self.screens["results"] = QLabel("Результаты")
        self.screens["profile"] = QLabel("Профиль пользователя")
        self.screens["groups"] = QLabel("Управление группами")
        self.screens["analytics"] = QLabel("Аналитика")
        self.screens["users"] = QLabel("Управление пользователями")
        self.screens["system"] = QLabel("Системные настройки")
        self.screens["logs"] = QLabel("Логи системы")
        self.screens["sandbox"] = SandboxView(self)

        for key, widget in self.screens.items():
            if isinstance(widget, QLabel):
                widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                widget.setStyleSheet(f"font-size: 24px; color: {COLORS['text_secondary']};")
            self.content_stack.addWidget(widget)
            
        # Устанавливаем Sandbox по умолчанию при запуске
        self.content_stack.setCurrentWidget(self.screens["sandbox"])

    @Slot(str, dict)
    def _on_navigate(self, route: str, params: dict) -> None:
        if route in self.screens:
            self.content_stack.setCurrentWidget(self.screens[route])
            # Обновление заголовка можно привязать к роуту более умно, здесь просто capitalizing
            titles = {
                "home": "Главная", "cases": "Кейсы", "results": "Результаты", 
                "profile": "Профиль", "groups": "Группы", "analytics": "Аналитика",
                "users": "Пользователи", "system": "Настройки", "logs": "Логи",
                "sandbox": "UI Песочница"
            }
            self.topbar.set_title(titles.get(route, route.capitalize()))

    @Slot()
    def _on_user_login(self) -> None:
        user = app.current_user
        if not user:
            return
            
        # Настройка сайдбара под роль
        self.sidebar.name_lbl.setText(user.full_name)
        self.sidebar.build_navigation(user.role.name)

    @Slot()
    def toggle_maximize(self) -> None:
        if self._is_maximized:
            self._is_maximized = False
            self.setGeometry(self._normal_geometry)
        else:
            self._normal_geometry = self.geometry()
            self._is_maximized = True
            self.setGeometry(QApplication.primaryScreen().availableGeometry())
        self.update() # Вызов paintEvent для перерисовки рамки
