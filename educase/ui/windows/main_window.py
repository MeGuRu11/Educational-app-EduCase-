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
        bus.start_case.connect(self._on_start_case)

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
            # Простая анимация появления экрана
            import PySide6.QtWidgets as QtWidgets
            from PySide6.QtCore import QPropertyAnimation, QEasingCurve
            
            effect = QtWidgets.QGraphicsOpacityEffect(self.screens[route])
            self.screens[route].setGraphicsEffect(effect)
            self.anim = QPropertyAnimation(effect, b"opacity")
            self.anim.setDuration(250)
            self.anim.setStartValue(0.0)
            self.anim.setEndValue(1.0)
            self.anim.setEasingCurve(QEasingCurve.Type.InOutSine)
            self.anim.start()

            # Обновление заголовка
            titles = {
                "home": "Главная", "cases": "Мои кейсы", "results": "Мои результаты", 
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
            
        role = user.role.name
        
        # Подгрузка реальных экранов в зависимости от роли
        if role == "student":
            from ui.screens.student.dashboard import StudentDashboard
            from ui.screens.student.my_cases import MyCasesScreen
            from ui.screens.student.my_results import MyResultsScreen
            from ui.screens.student.profile import StudentProfileScreen
            
            # Удаляем заглушки
            for key in ["home", "cases", "results", "profile"]:
                if key in self.screens:
                    self.content_stack.removeWidget(self.screens[key])
                    self.screens[key].deleteLater()
                    
            self.screens["home"] = StudentDashboard(self.container)
            self.screens["cases"] = MyCasesScreen(self.container)
            self.screens["results"] = MyResultsScreen(self.container)
            self.screens["profile"] = StudentProfileScreen(self.container)
            
            for key in ["home", "cases", "results", "profile"]:
                self.content_stack.addWidget(self.screens[key])
            
        # Настройка сайдбара под роль
        self.sidebar.name_lbl.setText(user.full_name)
        self.sidebar.build_navigation(role)

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

    @Slot(int)
    def _on_start_case(self, case_id: int) -> None:
        from ui.screens.student.case_player import CasePlayer
        import app
        
        # 1. Загружаем данные кейса
        case = self.container.case_service.get_case(case_id)
        if not case:
            return
            
        # 2. Формируем структуру данных (mock) так как пока нет полноценного редактора заданий
        case_data = {
            "name": case.title,
            "time_limit_min": case.time_limit_minutes or 0,
            "tasks": [
                {
                    "id": 1,
                    "task_type": "single_choice",
                    "title": "Тестовое задание",
                    "body": f"Это тестовое задание для кейса '{case.title}'",
                    "max_score": 10,
                    "topic": "Общая проверка",
                    "configuration": {
                        "options": [
                            {"id": 1, "text": "Вариант 1", "is_correct": True},
                            {"id": 2, "text": "Вариант 2", "is_correct": False},
                        ]
                    }
                }
            ]
        }
        
        # CasePlayer modal window (передаём case_data и attempt_service)
        player = CasePlayer(case_data, self.container.attempt_service, attempt_id=1, parent=self)
        player.exec()
        
        # Обновить дашборд / результаты после закрытия плеера
        if "home" in self.screens and hasattr(self.screens["home"], "presenter"):
            self.screens["home"].presenter.load_data()
        if "results" in self.screens and hasattr(self.screens["results"], "presenter"):
            self.screens["results"].presenter.load_results()
