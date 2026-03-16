# educase/ui/screens/admin/logs.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QDateEdit
)

from ui.components.common import CardFrame
from ui.styles.dashboard_theme import COLORS

class LogsScreen(QWidget):
    """Экран системных логов"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AdminLogs")
        self.setStyleSheet(f"background-color: {COLORS['bg']};")
        
        self._setup_ui()
        self._load_mock_logs()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)

        lbl_title = QLabel("Системные логи")
        lbl_title.setStyleSheet(f"color: {COLORS['t1']}; font-size: 20px; font-weight: 800;")
        layout.addWidget(lbl_title)

        # Фильтры логов
        filter_card = CardFrame()
        fl = QHBoxLayout(filter_card)
        
        self.level_filter = QComboBox()
        self.level_filter.addItems(["Все уровни", "INFO", "WARNING", "ERROR"])
        fl.addWidget(self.level_filter)
        
        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        fl.addWidget(self.date_filter)
        
        btn_refresh = QPushButton("Обновить")
        fl.addWidget(btn_refresh)
        fl.addStretch()
        
        btn_export = QPushButton("Экспорт в .txt")
        fl.addWidget(btn_export)
        
        layout.addWidget(filter_card)

        # Таблица логов
        self.table_card = CardFrame()
        tl = QVBoxLayout(self.table_card)
        tl.setContentsMargins(1, 1, 1, 1)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Время", "Уровень", "Пользователь", "Сообщение"])
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.table.setStyleSheet(f"""
            QTableWidget {{ background-color: white; border: none; }}
            QHeaderView::section {{
                background-color: white; padding: 12px; border: none;
                border-bottom: 2px solid {COLORS['border']};
                color: {COLORS['t3']}; font-weight: bold;
            }}
            QTableWidget::item {{ padding: 8px; color: {COLORS['t1']}; }}
        """)
        
        tl.addWidget(self.table)
        layout.addWidget(self.table_card)

    def _load_mock_logs(self):
        logs = [
            ("16.03 09:45:12", "INFO", "admin", "Успешный бэкап базы данных"),
            ("16.03 09:42:01", "INFO", "teacher1", "Изменен кейс ID=42"),
            ("16.03 09:30:05", "WARNING", "system", "Превышен лимит попыток входа (user: student2)"),
            ("16.03 08:15:44", "INFO", "system", "Система запущена"),
        ]
        
        self.table.setRowCount(len(logs))
        for row, (time, level, user, msg) in enumerate(logs):
            self.table.setItem(row, 0, QTableWidgetItem(time))
            self.table.setItem(row, 1, QTableWidgetItem(level))
            self.table.setItem(row, 2, QTableWidgetItem(user))
            self.table.setItem(row, 3, QTableWidgetItem(msg))
            
            # Раскраска уровня
            if level == "ERROR": self.table.item(row, 1).setForeground(Qt.GlobalColor.red)
            elif level == "WARNING": self.table.item(row, 1).setForeground(Qt.GlobalColor.darkYellow)

    def refresh(self):
        pass
