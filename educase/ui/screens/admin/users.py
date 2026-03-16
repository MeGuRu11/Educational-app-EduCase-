# educase/ui/screens/admin/users.py
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)

from ui.components.common import CardFrame
from ui.styles.dashboard_theme import COLORS, FONT, RADIUS
from ui.styles.icons import get_icon

class UsersScreen(QWidget):
    """Экран управления пользователями"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AdminUsers")
        self.setStyleSheet(f"background-color: {COLORS['bg']};")
        
        self.container = getattr(parent, "container", None)
        self.user_repo = self.container.user_repo if self.container else None
        
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)

        # Заголовок и кнопка добавления
        header = QHBoxLayout()
        lbl_title = QLabel("Управление пользователями")
        lbl_title.setStyleSheet(f"color: {COLORS['t1']}; font-size: 20px; font-weight: 800;")
        header.addWidget(lbl_title)
        header.addStretch()
        
        btn_add = QPushButton("+ ДОБАВИТЬ")
        btn_add.setFixedHeight(36)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border-radius: {RADIUS['control']}px;
                padding: 0 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS['accent_hover']}; }}
        """)
        header.addWidget(btn_add)
        layout.addLayout(header)

        # Панель поиска и фильтров
        filter_card = CardFrame()
        fl = QHBoxLayout(filter_card)
        fl.setContentsMargins(12, 10, 12, 10)
        
        self.search_inp = QLineEdit()
        self.search_inp.setPlaceholderText("Поиск по имени или логину...")
        self.search_inp.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['control']}px;
                padding: 8px 12px;
                background: {COLORS['bg']};
            }}
        """)
        fl.addWidget(self.search_inp)
        
        btn_filter = QPushButton("Фильтр")
        btn_filter.setFixedWidth(100)
        fl.addWidget(btn_filter)
        
        layout.addWidget(filter_card)

        # Таблица пользователей
        self.table_card = CardFrame()
        tl = QVBoxLayout(self.table_card)
        tl.setContentsMargins(1, 1, 1, 1) # Тонкий бордер вокруг таблицы
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Логин", "Роль", "Действия"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        
        # Styles
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: none;
                gridline-color: transparent;
                alternate-background-color: {COLORS['bg']};
            }}
            QHeaderView::section {{
                background-color: white;
                padding: 12px;
                border: none;
                border-bottom: 2px solid {COLORS['border']};
                color: {COLORS['t3']};
                font-weight: bold;
                text-align: left;
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {COLORS['border']};
                color: {COLORS['t1']};
            }}
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        tl.addWidget(self.table)
        layout.addWidget(self.table_card)

    def refresh(self):
        if not self.user_repo:
            return
            
        users = self.user_repo.get_all(limit=100)
        self.table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.table.setItem(row, 1, QTableWidgetItem(user.full_name))
            self.table.setItem(row, 2, QTableWidgetItem(user.username))
            self.table.setItem(row, 3, QTableWidgetItem(user.role.name if user.role else "—"))
            
            # Кнопка редактирования
            btn_edit = QPushButton("РЕД.")
            btn_edit.setStyleSheet(f"color: {COLORS['accent']}; border: none; font-weight: bold;")
            self.table.setCellWidget(row, 4, btn_edit)
