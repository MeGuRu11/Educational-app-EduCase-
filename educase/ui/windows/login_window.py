# ui/windows/login_window.py
"""
Окно авторизации. FramelessWindowHint, центрирование.
Обработка ввода, валидация, интеграция с AuthService.
"""
from PySide6.QtCore import Qt, QTimer, QPoint, QEasingCurve, QPropertyAnimation, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QApplication
)

from core.di_container import Container
from core.exceptions import AuthError
from ui.styles.animations import fade_in, fade_out
from ui.styles.icons import get_icon
from ui.styles.theme import ANIM, COLORS, RADIUS


class LoginWindow(QWidget):
    # Сигнал испускается при успешной авторизации
    login_successful = Signal()

    def __init__(self, container: Container):
        super().__init__()
        self.container = container
        self.auth_service = self.container.auth_service

        self.W, self.H = 480, 600
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.W, self.H)
        
        # Для перетаскивания окна
        self._dragging = False
        self._drag_start_pos = QPoint()

        # Состояния
        self.lock_seconds_left = 0
        self.lock_timer = QTimer(self)
        self.lock_timer.timeout.connect(self._on_lock_tick)

        self._setup_ui()
        self._center()

    def _center(self) -> None:
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.W) // 2, (screen.height() - self.H) // 2)

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Рисуем подложку карточки
        p.setBrush(QColor(COLORS["bg_elevated"]))
        p.setPen(Qt.PenStyle.NoPen)
        r = RADIUS["xlarge"]
        p.drawRoundedRect(0, 0, self.W, self.H, r, r)

        # Тонкая рамка
        p.setPen(QColor(COLORS["stroke_card"]))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(0, 0, self.W - 1, self.H - 1, r, r)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # Разрешаем тянуть за весь фон (т.к. весь фрейм - карточка)
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_start_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._dragging = False
        event.accept()

    def _setup_ui(self) -> None:
        # Кнопки управления окном (абсолютное позиционирование)
        from ui.components.window_controls import WindowControls
        self.window_controls = WindowControls(self, show_maximize=False)
        # Ширина: 46px * 2 кнопки = 92px
        self.window_controls.setFixedSize(92, 32)
        self.window_controls.move(self.W - 92, 0)
        self.window_controls.minimized.connect(self.showMinimized)
        self.window_controls.closed.connect(self.close)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 60, 40, 40)
        layout.setSpacing(20)

        # === Логотип и заголовки ===
        logo_label = QLabel(self)
        logo_label.setPixmap(get_icon("book", COLORS["accent"], 64).pixmap(64, 64))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        title = QLabel("EduCase")
        title_font = QFont("Segoe UI Variable", 28, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)

        subtitle = QLabel("ВМедА им. С.М. Кирова")
        sub_font = QFont("Segoe UI Variable", 13)
        sub_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        subtitle.setFont(sub_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # === Поля ввода ===
        self.inp_login = QLineEdit()
        self.inp_login.setPlaceholderText("Логин")
        self.inp_login.setFixedHeight(44)
        layout.addWidget(self.inp_login)

        pwd_layout = QHBoxLayout()
        pwd_layout.setSpacing(8)
        
        self.inp_pwd: QLineEdit = QLineEdit()
        self.inp_pwd.setPlaceholderText("Пароль")
        self.inp_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pwd.setFixedHeight(44)
        self.inp_pwd.returnPressed.connect(self._on_login_clicked)
        # Связываем Enter в первом поле со вторым
        self.inp_login.returnPressed.connect(self.inp_pwd.setFocus)
        pwd_layout.addWidget(self.inp_pwd)

        self.btn_eye = QPushButton()
        self.btn_eye.setIcon(get_icon("star", COLORS["text_secondary"])) # Todo real eye icon
        self.btn_eye.setFixedSize(44, 44)
        self.btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eye.clicked.connect(self._toggle_pwd_visibility)
        pwd_layout.addWidget(self.btn_eye)

        layout.addLayout(pwd_layout)

        # === Кнопка Войти ===
        self.btn_login = QPushButton("ВОЙТИ")
        self.btn_login.setFixedHeight(44)
        self.btn_login.clicked.connect(self._on_login_clicked)
        # Style defined in global QSS usually, but we ensure accent class if needed
        self.btn_login.setProperty("class", "primary") 
        layout.addWidget(self.btn_login)

        # === Ошибка ===
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.setStyleSheet(f"color: {COLORS['error']}; font-size: 13px;")
        self.lbl_error.hide()  # Hidden by default
        
        layout.addWidget(self.lbl_error)

        layout.addStretch()

        # === Footer ===
        footer_layout = QHBoxLayout()
        
        contact_admin = QLabel("Забыли пароль? Обратитесь к администратору")
        contact_admin.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        footer_layout.addWidget(contact_admin, alignment=Qt.AlignmentFlag.AlignLeft)
        
        version = QLabel("v1.0.0")
        version.setStyleSheet(f"color: {COLORS['text_disabled']}; font-size: 11px;")
        footer_layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(footer_layout)

    def _toggle_pwd_visibility(self) -> None:
        if self.inp_pwd.echoMode() == QLineEdit.EchoMode.Password:
            self.inp_pwd.setEchoMode(QLineEdit.EchoMode.Normal)
            # self.btn_eye.setIcon(get_icon("eye_off")) # update icon
        else:
            self.inp_pwd.setEchoMode(QLineEdit.EchoMode.Password)
            # self.btn_eye.setIcon(get_icon("eye")) # update icon

    def show_error(self, message: str) -> None:
        self.lbl_error.setText(message)
        self.lbl_error.show()

    def hide_error(self) -> None:
        self.lbl_error.hide()

    def _on_login_clicked(self) -> None:
        if self.lock_seconds_left > 0:
            return

        username = self.inp_login.text().strip()
        password = self.inp_pwd.text()

        if not username or not password:
            self.show_error("Введите логин и пароль")
            return

        self.hide_error()
        self.btn_login.setEnabled(False)
        self.btn_login.setText("ВХОД...")
        QApplication.processEvents() # Force UI update

        try:
            user = self.auth_service.login(username, password)
            self.login_successful.emit()
            
        except AuthError as e:
            self.show_error(str(e))
            self.btn_login.setEnabled(True)
            self.btn_login.setText("ВОЙТИ")
            
            if e.code == "LOCKED_OUT" or e.code == "ACCOUNT_LOCKED":
                # Извлекаем секунды из текста, либо ставим дефолт
                import re
                match = re.search(r"через (\d+) сек", str(e))
                secs = int(match.group(1)) if match else 300
                self._start_lockdown(secs)
                
        except Exception as e:
            self.show_error("Внутренняя ошибка сервера")
            print(f"Login error: {e}")
            self.btn_login.setEnabled(True)
            self.btn_login.setText("ВОЙТИ")

    def _start_lockdown(self, seconds: int) -> None:
        self.lock_seconds_left = seconds
        self.inp_login.setEnabled(False)
        self.inp_pwd.setEnabled(False)
        self.btn_login.setEnabled(False)
        self._update_lock_btn_text()
        self.lock_timer.start(1000)

    def _on_lock_tick(self) -> None:
        self.lock_seconds_left -= 1
        if self.lock_seconds_left <= 0:
            self.lock_timer.stop()
            self.inp_login.setEnabled(True)
            self.inp_pwd.setEnabled(True)
            self.btn_login.setEnabled(True)
            self.btn_login.setText("ВОЙТИ")
            self.hide_error()
        else:
            self._update_lock_btn_text()

    def _update_lock_btn_text(self) -> None:
        m = self.lock_seconds_left // 60
        s = self.lock_seconds_left % 60
        self.btn_login.setText(f"Заблокировано ({m}:{s:02d})")
