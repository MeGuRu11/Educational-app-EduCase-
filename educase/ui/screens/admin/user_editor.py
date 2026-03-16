# educase/ui/screens/admin/user_editor.py
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QLineEdit, QComboBox, QStackedWidget
)

from ui.styles.dashboard_theme import COLORS, RADIUS

class UserEditorDialog(QDialog):
    """Диалог создания/редактирования пользователя (Stepper)"""
    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактор пользователя")
        self.setFixedSize(450, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.user_data = user_data or {}
        self.current_step = 0
        
        self._setup_ui()

    def _setup_ui(self):
        self.main_frame = QFrame(self)
        self.main_frame.setGeometry(0, 0, 450, 500)
        self.main_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                border-radius: {RADIUS['card']}px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        self.lbl_title = QLabel("Новый пользователь")
        self.lbl_title.setStyleSheet(f"color: {COLORS['t1']}; font-size: 18px; font-weight: 800;")
        layout.addWidget(self.lbl_title)

        # Stepper Indicator (Visual only for now)
        self.step_indicator = QLabel("Шаг 1 из 3: Основная информация")
        self.step_indicator.setStyleSheet(f"color: {COLORS['t3']}; font-size: 11px; font-weight: bold;")
        layout.addWidget(self.step_indicator)

        # Stacked Widget for Steps
        self.stack = QStackedWidget()
        
        # Step 1: Base Info
        step1 = QWidget()
        s1l = QVBoxLayout(step1)
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("ФИО")
        self.inp_login = QLineEdit()
        self.inp_login.setPlaceholderText("Логин")
        s1l.addWidget(QLabel("ФИО:"))
        s1l.addWidget(self.inp_name)
        s1l.addWidget(QLabel("Логин:"))
        s1l.addWidget(self.inp_login)
        s1l.addStretch()
        
        # Step 2: Role & Security
        step2 = QWidget()
        s2l = QVBoxLayout(step2)
        self.combo_role = QComboBox()
        self.combo_role.addItems(["student", "teacher", "admin"])
        s2l.addWidget(QLabel("Роль:"))
        s2l.addWidget(self.combo_role)
        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("Пароль (оставьте пустым для сохранения)")
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        s2l.addWidget(QLabel("Пароль:"))
        s2l.addWidget(self.inp_pass)
        s2l.addStretch()

        # Step 3: Confirmation
        step3 = QWidget()
        s3l = QVBoxLayout(step3)
        self.lbl_conf = QLabel("Проверьте данные перед сохранением.")
        s3l.addWidget(self.lbl_conf)
        s3l.addStretch()

        self.stack.addWidget(step1)
        self.stack.addWidget(step2)
        self.stack.addWidget(step3)
        layout.addWidget(self.stack)

        # Footer Buttons
        footer = QHBoxLayout()
        self.btn_back = QPushButton("Назад")
        self.btn_back.setEnabled(False)
        self.btn_back.clicked.connect(self._prev_step)
        
        self.btn_next = QPushButton("Далее")
        self.btn_next.clicked.connect(self._next_step)
        self.btn_next.setStyleSheet(f"background: {COLORS['accent']}; color: white; font-weight: bold;")
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        
        footer.addWidget(self.btn_cancel)
        footer.addStretch()
        footer.addWidget(self.btn_back)
        footer.addWidget(self.btn_next)
        layout.addLayout(footer)

    def _next_step(self):
        if self.current_step < 2:
            self.current_step += 1
            self.stack.setCurrentIndex(self.current_step)
            self._update_ui()
        else:
            self.accept()

    def _prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.stack.setCurrentIndex(self.current_step)
            self._update_ui()

    def _update_ui(self):
        titles = [
            "Шаг 1 из 3: Основная информация",
            "Шаг 2 из 3: Роль и безопасность",
            "Шаг 3 из 3: Подтверждение"
        ]
        self.step_indicator.setText(titles[self.current_step])
        self.btn_back.setEnabled(self.current_step > 0)
        self.btn_next.setText("Далее" if self.current_step < 2 else "СОХРАНИТЬ")
