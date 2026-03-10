# ui/screens/student/profile.py
"""
Экран "Профиль": информация о пользователе и смена пароля.
"""
import bcrypt

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt

import app
from core.di_container import Container
from core.event_bus import bus
from ui.styles.theme import COLORS, RADIUS, TYPO
from ui.styles.icons import get_icon


class ProfilePresenter:
    def __init__(self, view: 'StudentProfileScreen', container: Container):
        self.view = view
        self.user_service = container.user_service

    def change_password(self, old_pwd: str, new_pwd: str, confirm_pwd: str):
        user = app.current_user
        if not user:
            return

        if not old_pwd or not new_pwd or not confirm_pwd:
            self.view.show_error("Все поля формы обязательны для заполнения.")
            return
            
        if new_pwd != confirm_pwd:
            self.view.show_error("Новые пароли не совпадают.")
            return
            
        if len(new_pwd) < 6:
            self.view.show_error("Новый пароль должен содержать не менее 6 символов.")
            return

        # Проверка старого пароля
        if not bcrypt.checkpw(old_pwd.encode("utf-8"), user.password_hash.encode("utf-8")):
            self.view.show_error("Неверный текущий пароль.")
            return

        try:
            self.user_service.change_password(user.id, new_pwd)
            self.view.show_success("Пароль успешно изменён!")
        except Exception as e:
            self.view.show_error(f"Ошибка при смене пароля: {e}")


class LabeledInput(QWidget):
    def __init__(self, label_text: str, is_password: bool = False, read_only: bool = False):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel(label_text)
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: bold;")
        layout.addWidget(lbl)
        
        self.input = QLineEdit()
        self.input.setFixedHeight(40)
        self.input.setReadOnly(read_only)
        if read_only:
            self.input.setStyleSheet(f"""
                QLineEdit {{
                    border: 1px solid {COLORS['stroke_control']};
                    border-radius: 6px;
                    padding: 0 12px;
                    background-color: {COLORS['bg_layer']};
                    color: {COLORS['text_disabled']};
                }}
            """)
        else:
            self.input.setStyleSheet(f"""
                QLineEdit {{
                    border: 1px solid {COLORS['stroke_control']};
                    border-radius: 6px;
                    padding: 0 12px;
                    background-color: {COLORS['bg_elevated']};
                    color: {COLORS['text_primary']};
                }}
                QLineEdit:focus {{
                    border: 2px solid {COLORS['accent']};
                }}
            """)
            
        if is_password:
            self.input.setEchoMode(QLineEdit.EchoMode.Password)
            
        layout.addWidget(self.input)

    def text(self) -> str:
        return self.input.text()

    def set_text(self, text: str):
        self.input.setText(text)
        
    def clear(self):
        self.input.clear()


class StudentProfileScreen(QWidget):
    def __init__(self, container: Container):
        super().__init__()
        self.presenter = ProfilePresenter(self, container)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(32)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl = QLabel("Мой профиль")
        lbl.setStyleSheet(f"font-size: {TYPO['title_large']}px; font-weight: bold; color: {COLORS['text_primary']};")
        main_layout.addWidget(lbl)

        # ── Блок информации о пользователе
        info_frame = QFrame()
        info_frame.setStyleSheet(f"background: {COLORS['bg_elevated']}; border: 1px solid {COLORS['stroke_divider']}; border-radius: {RADIUS['large']}px;")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(24, 24, 24, 24)
        info_layout.setSpacing(16)
        
        title_info = QLabel("Личные данные")
        title_info.setStyleSheet(f"font-size: {TYPO['title']}px; font-weight: bold; color: {COLORS['text_primary']}; border: none;")
        info_layout.addWidget(title_info)
        
        row_1 = QHBoxLayout()
        self.fio_input = LabeledInput("ФИО", read_only=True)
        self.group_input = LabeledInput("Группа", read_only=True)
        row_1.addWidget(self.fio_input)
        row_1.addWidget(self.group_input)
        info_layout.addLayout(row_1)
        
        row_2 = QHBoxLayout()
        self.username_input = LabeledInput("Логин", read_only=True)
        self.role_input = LabeledInput("Роль", read_only=True)
        row_2.addWidget(self.username_input)
        row_2.addWidget(self.role_input)
        info_layout.addLayout(row_2)
        
        main_layout.addWidget(info_frame)

        # ── Блок смены пароля
        pwd_frame = QFrame()
        pwd_frame.setStyleSheet(f"background: {COLORS['bg_elevated']}; border: 1px solid {COLORS['stroke_divider']}; border-radius: {RADIUS['large']}px;")
        pwd_layout = QVBoxLayout(pwd_frame)
        pwd_layout.setContentsMargins(24, 24, 24, 24)
        pwd_layout.setSpacing(16)

        title_pwd = QLabel("Безопасность")
        title_pwd.setStyleSheet(f"font-size: {TYPO['title']}px; font-weight: bold; color: {COLORS['text_primary']}; border: none;")
        pwd_layout.addWidget(title_pwd)

        self.old_pwd = LabeledInput("Текущий пароль", is_password=True)
        self.new_pwd = LabeledInput("Новый пароль", is_password=True)
        self.confirm_pwd = LabeledInput("Повторите новый пароль", is_password=True)
        
        pwd_layout.addWidget(self.old_pwd)
        pwd_layout.addWidget(self.new_pwd)
        pwd_layout.addWidget(self.confirm_pwd)
        
        self.btn_change_pwd = QPushButton("Сменить пароль")
        self.btn_change_pwd.setFixedHeight(40)
        self.btn_change_pwd.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_change_pwd.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{ background-color: {COLORS['accent_hover']}; }}
        """)
        self.btn_change_pwd.clicked.connect(self._on_change_password)
        
        pwd_btn_row = QHBoxLayout()
        pwd_btn_row.addStretch()
        pwd_btn_row.addWidget(self.btn_change_pwd)
        pwd_layout.addLayout(pwd_btn_row)

        main_layout.addWidget(pwd_frame)
        main_layout.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        self._load_user_data()

    def _load_user_data(self):
        user = app.current_user
        if user:
            self.fio_input.set_text(user.full_name)
            self.username_input.set_text(user.username)
            self.role_input.set_text(user.role.display_name)
            self.group_input.set_text(user.group.name if user.group else "Нет группы")

    def _on_change_password(self):
        self.presenter.change_password(
            self.old_pwd.text(),
            self.new_pwd.text(),
            self.confirm_pwd.text()
        )

    def show_error(self, message: str):
        QMessageBox.warning(self, "Ошибка", message)

    def show_success(self, message: str):
        QMessageBox.information(self, "Успех", message)
        self.old_pwd.clear()
        self.new_pwd.clear()
        self.confirm_pwd.clear()
