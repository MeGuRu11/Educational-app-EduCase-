# ui/components/sidebar.py
"""
Боковая панель навигации (expand/collapse с анимациями).
Role-aware навигация (показывает разный набор кнопок для ролей).
"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal, Slot
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout

from core.event_bus import bus
from ui.styles.icons import get_icon
from ui.styles.theme import ANIM, COLORS


class NavButton(QPushButton):
    """Кастомная кнопка для Sidebar с иконкой и текстом."""

    def __init__(self, icon_name: str, text: str, route: str, is_expanded: bool = True):
        super().__init__()
        self.route = route
        self.icon_name = icon_name
        self.expanded_text = text
        self._is_expanded = is_expanded

        # UI Настройка
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(48)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 12px;
                border: none;
                border-radius: 8px;
                color: #6B6B6B;
                font-family: 'Segoe UI Variable';
                font-size: 14px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0,0,0,0.04);
            }
            QPushButton:checked {
                color: #0078D4;
                font-weight: 600;
                background-color: rgba(0,120,212,0.10);
            }
        """)

        self.update_state(self._is_expanded)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self.isChecked():
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(COLORS["accent"]))

            # Левая синяя полоска-индикатор
            path = QPainterPath()
            path.addRoundedRect(0, 10, 4, self.height() - 20, 2, 2)
            p.drawPath(path)

    def update_state(self, expanded: bool) -> None:
        """Переключатель Expanded/Collapsed (показываем/скрываем текст)."""
        self._is_expanded = expanded
        color = COLORS["accent"] if self.isChecked() else COLORS["text_secondary"]
        self.setIcon(get_icon(self.icon_name, color, 24))

        if expanded:
            self.setText(f"  {self.expanded_text}")
        else:
            self.setText("")


class Sidebar(QFrame):
    route_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.is_expanded = True
        self.w_expanded = 240
        self.w_collapsed = 72

        self.setFixedWidth(self.w_expanded)
        self.setStyleSheet(f"background-color: {COLORS['sidebar_bg']}; border-right: 1px solid {COLORS['stroke_divider']};")

        self.nav_buttons: list[NavButton] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(12, 24, 12, 24)
        self.layout_.setSpacing(8)

        # ── Блок профиля
        self.profile_lbl = QLabel("Аватар")
        self.profile_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profile_lbl.setFixedHeight(40)
        self.layout_.addWidget(self.profile_lbl)

        self.name_lbl = QLabel("ФИО")
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: bold;")
        self.layout_.addWidget(self.name_lbl)

        # Разделитель
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"background-color: {COLORS['stroke_divider']};")
        self.layout_.addWidget(div)
        self.layout_.addSpacing(16)

        # ── Контейнер для кнопок навигации (заполняется динамически)
        self.nav_layout = QVBoxLayout()
        self.nav_layout.setSpacing(4)
        self.layout_.addLayout(self.nav_layout)

        self.layout_.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ── Нижний блок
        self.btn_toggle = NavButton("chevron_right", "Свернуть", "toggle", self.is_expanded)
        self.btn_toggle.setCheckable(False)
        self.btn_toggle.clicked.connect(self.toggle_size)

        self.btn_logout = NavButton("logout", "Выйти", "logout", self.is_expanded)
        self.btn_logout.setCheckable(False)
        self.btn_logout.clicked.connect(lambda: bus.user_logged_out.emit())

        self.layout_.addWidget(self.btn_logout)
        self.layout_.addWidget(self.btn_toggle)

    def build_navigation(self, role: str) -> None:
        """Перестраивает меню в зависимости от роли."""
        # Очистить старое
        for i in reversed(range(self.nav_layout.count())):
            widget = self.nav_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.nav_buttons.clear()

        # Роуты
        routes = []
        if role == "student":
            routes = [
                ("home", "Главная", "home"),
                ("cases", "Мои кейсы", "book"),
                ("results", "Результаты", "star"),
                ("profile", "Профиль", "profile"),
            ]
        elif role == "teacher":
            routes = [
                ("home", "Главная", "home"),
                ("cases", "Управление кейсами", "book"),
                ("groups", "Группы", "users"),
                ("analytics", "Аналитика", "chart"),
                ("profile", "Профиль", "profile"),
            ]
        elif role == "admin":
            routes = [
                ("home", "Дашборд", "home"),
                ("users", "Пользователи", "users"),
                ("system", "Система", "settings"),
                ("logs", "Логи", "document"),
                ("sandbox", "UI Песочница", "document"),
                ("profile", "Профиль", "profile"),
            ]

        for route_id, text, icon in routes:
            btn = NavButton(icon, text, route_id, self.is_expanded)
            btn.clicked.connect(lambda checked, b=btn: self._on_nav_clicked(b))
            self.nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        if self.nav_buttons:
            self._on_nav_clicked(self.nav_buttons[0]) # Select first

    def _on_nav_clicked(self, clicked_btn: NavButton) -> None:
        for btn in self.nav_buttons:
            btn.setChecked(btn == clicked_btn)
            btn.update_state(self.is_expanded) # Update icon color
        self.route_selected.emit(clicked_btn.route)

    @Slot()
    def toggle_size(self) -> None:
        self.is_expanded = not self.is_expanded
        end_w = self.w_expanded if self.is_expanded else self.w_collapsed

        # Анимация ширины (Property: fixedWidth)
        self.anim = QPropertyAnimation(self, b"maximumWidth", self) # Trick: animate maxW and minW
        self.anim.setDuration(ANIM["normal"])
        self.anim.setStartValue(self.width())
        self.anim.setEndValue(end_w)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_min = QPropertyAnimation(self, b"minimumWidth", self)
        self.anim_min.setDuration(ANIM["normal"])
        self.anim_min.setStartValue(self.width())
        self.anim_min.setEndValue(end_w)
        self.anim_min.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim.start()
        self.anim_min.start()

        # Скрываем/показываем текстовые элементы
        self.name_lbl.setVisible(self.is_expanded)
        self.btn_toggle.update_state(self.is_expanded)
        self.btn_logout.update_state(self.is_expanded)
        self.btn_toggle.expanded_text = "Свернуть" if self.is_expanded else "Развернуть"

        for btn in self.nav_buttons:
            btn.update_state(self.is_expanded)
