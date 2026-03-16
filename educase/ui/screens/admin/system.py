# educase/ui/screens/admin/system.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QSpinBox,
    QCheckBox
)

from ui.components.common import CardFrame
from ui.styles.dashboard_theme import COLORS, RADIUS

class SystemSettingsScreen(QWidget):
    """Экран системных настроек"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AdminSystem")
        self.setStyleSheet(f"background-color: {COLORS['bg']};")
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(24)

        lbl_title = QLabel("Системные настройки")
        lbl_title.setStyleSheet(f"color: {COLORS['t1']}; font-size: 20px; font-weight: 800;")
        layout.addWidget(lbl_title)

        # Группа: Общие настройки
        general_group = CardFrame()
        gl = QVBoxLayout(general_group)
        gl.setContentsMargins(24, 24, 24, 24)
        
        form = QFormLayout()
        form.setSpacing(15)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.app_name = QLineEdit("EduCase")
        self.app_version = QLineEdit("1.0.0 (Stage 8)")
        self.app_version.setReadOnly(True)
        
        form.addRow("Название приложения:", self.app_name)
        form.addRow("Версия системы:", self.app_version)
        gl.addLayout(form)

        # Группа: Безопасность и Сессии
        sec_group = CardFrame()
        sl = QVBoxLayout(sec_group)
        sl.setContentsMargins(24, 24, 24, 24)
        
        form_sec = QFormLayout()
        form_sec.setSpacing(15)
        
        self.idle_timeout = QSpinBox()
        self.idle_timeout.setRange(1, 120)
        self.idle_timeout.setValue(15)
        self.idle_timeout.setSuffix(" мин")
        
        self.max_attempts = QSpinBox()
        self.max_attempts.setRange(1, 10)
        self.max_attempts.setValue(5)
        
        form_sec.addRow("Таймаут неактивности:", self.idle_timeout)
        form_sec.addRow("Макс. попыток входа:", self.max_attempts)
        sl.addLayout(form_sec)

        # Группа: Медиа и Хранилище
        media_group = CardFrame()
        ml = QVBoxLayout(media_group)
        ml.setContentsMargins(24, 24, 24, 24)
        
        form_media = QFormLayout()
        self.max_img_size = QSpinBox()
        self.max_img_size.setRange(1, 50)
        self.max_img_size.setValue(5)
        self.max_img_size.setSuffix(" MB")
        
        form_media.addRow("Лимит размера изображений:", self.max_img_size)
        ml.addLayout(form_media)

        layout.addWidget(general_group)
        layout.addWidget(sec_group)
        layout.addWidget(media_group)
        
        # Кнопка сохранения
        btn_save = QPushButton("СОХРАНИТЬ ИЗМЕНЕНИЯ")
        btn_save.setFixedHeight(44)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border-radius: {RADIUS['control']}px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS['accent_hover']}; }}
        """)
        layout.addWidget(btn_save)
        
        layout.addStretch()

    def refresh(self):
        pass
