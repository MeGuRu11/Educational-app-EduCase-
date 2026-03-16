# educase/ui/screens/admin/dashboard.py
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QScrollArea, QGridLayout, QSizePolicy
)
from PySide6.QtWidgets import QPushButton

from core.event_bus import bus
from ui.components.common import CardFrame, SectionLabel, HoverCardFrame
from ui.components.stat_card import StatCard
from ui.styles.dashboard_theme import COLORS, FONT, RADIUS
from .dashboard_presenter import AdminDashboardPresenter, AdminDashboardStats, SystemLogEntry

class AdminDashboard(QWidget):
    """Экран: Дашборд администратора"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AdminDashboard")
        self.setStyleSheet(f"background-color: {COLORS['bg']};")
        
        self.container = getattr(parent, "container", None)
        self.presenter = AdminDashboardPresenter(self, self.container)
        
        self._setup_ui()
        self.presenter.load_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. TopBar (Header)
        topbar = QFrame()
        topbar.setFixedHeight(80)
        topbar.setStyleSheet(f"""
            background-color: {COLORS['card']};
            border-bottom: 1px solid {COLORS['border']};
        """)
        top_l = QHBoxLayout(topbar)
        top_l.setContentsMargins(32, 0, 32, 0)

        header_text = QVBoxLayout()
        lbl_welcome = QLabel("Обзор системы")
        lbl_welcome.setStyleSheet(
            f"color: {COLORS['t1']}; font-family: '{FONT}'; "
            "font-size: 22px; font-weight: 800; letter-spacing: -0.5px;"
        )
        lbl_sub = QLabel("Добро пожаловать в панель управления EduCase")
        lbl_sub.setStyleSheet(f"color: {COLORS['t2']}; font-size: 13px;")
        header_text.addWidget(lbl_welcome)
        header_text.addWidget(lbl_sub)
        top_l.addLayout(header_text)
        
        top_l.addStretch()
        
        lbl_status = QLabel("● Система активна")
        lbl_status.setStyleSheet(f"""
            color: {COLORS['success']};
            background: {COLORS['success_bg']};
            padding: 6px 14px;
            border-radius: 14px;
            font-weight: 700;
            font-size: 12px;
        """)
        top_l.addWidget(lbl_status)
        main_layout.addWidget(topbar)

        # 2. Scrollable Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        self.clayout = QVBoxLayout(content)
        self.clayout.setContentsMargins(28, 24, 28, 40)
        self.clayout.setSpacing(24)
        self.clayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Статистика (StatCards)
        self.stat_row = QHBoxLayout()
        self.stat_row.setSpacing(16)
        self.clayout.addLayout(self.stat_row)

        # Секция: Состояние системы + Последние логи
        mid_grid = QHBoxLayout()
        mid_grid.setSpacing(20)

        # Карточка состояния
        self.health_card = CardFrame()
        self.health_card.setMinimumHeight(240)
        hl = QVBoxLayout(self.health_card)
        hl.setContentsMargins(24, 24, 24, 24)
        hl.addWidget(SectionLabel("Состояние системы"))
        
        self.lbl_db_info = QLabel("База данных: 0.0 MB")
        self.lbl_db_info.setStyleSheet(f"color: {COLORS['t2']}; font-size: 14px;")
        hl.addWidget(self.lbl_db_info)
        
        self.lbl_backup_info = QLabel("Последний бэкап: —")
        self.lbl_backup_info.setStyleSheet(f"color: {COLORS['t2']}; font-size: 14px;")
        hl.addWidget(self.lbl_backup_info)
        hl.addStretch()
        
        # Лента логов
        self.log_card = CardFrame()
        self.log_card.setMinimumHeight(240)
        ll = QVBoxLayout(self.log_card)
        ll.setContentsMargins(24, 24, 24, 24)
        ll.addWidget(SectionLabel("Последние системные логи"))
        
        self.log_container = QVBoxLayout()
        self.log_container.setSpacing(10)
        ll.addLayout(self.log_container)
        ll.addStretch()

        mid_grid.addWidget(self.health_card, 1)
        mid_grid.addWidget(self.log_card, 1)
        self.clayout.addLayout(mid_grid)

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

    def display_stats(self, stats: AdminDashboardStats):
        # Очистка предыдущих
        for i in reversed(range(self.stat_row.count())): 
            item = self.stat_row.itemAt(i).widget()
            if item: item.setParent(None)

        s1 = StatCard(
            "Пользователи", str(stats.total_users), "+2 сегодня", "up",
            '<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><path d="M20 8v6M23 11h-6"/>',
            COLORS["accent"]
        )
        s2 = StatCard(
            "Сессии", str(stats.active_sessions), "Online", "neutral",
            '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
            COLORS["success"]
        )
        db_label = f"{stats.db_size_mb:.1f} MB"
        s3 = StatCard(
            "База данных", db_label, "SQLite", "neutral",
            '<path d="M12 21c-4.4 0-8-1.8-8-4V7c0-2.2 3.6-4 8-4s8 1.8 8 4v10c0 2.2-3.6 4-8 4z"/><path d="M4 7c0 2.2 3.6 4 8 4s8-1.8 8-4"/><path d="M4 12c0 2.2 3.6 4 8 4s8-1.8 8-4"/>',
            COLORS["warning"]
        )

        self.stat_row.addWidget(s1, 1)
        self.stat_row.addWidget(s2, 1)
        self.stat_row.addWidget(s3, 1)

        self.lbl_db_info.setText(f"Размер SQLite: {stats.db_size_mb:.2f} MB")
        self.lbl_backup_info.setText(f"Последний бэкап: {stats.last_backup}")

        # Добавим кнопки быстрых действий
        if not hasattr(self, "quick_actions_added"):
            self.clayout.addSpacing(10)
            actions_l = QHBoxLayout()
            actions_l.setSpacing(16)
            
            btn_manage = QPushButton("Управление пользователями")
            btn_manage.setStyleSheet(f"""
                background: {COLORS['accent']}; color: white; border-radius: 8px; 
                padding: 10px 20px; font-weight: bold;
            """)
            btn_manage.clicked.connect(lambda: bus.navigate_to.emit("users", {}))
            
            btn_sys = QPushButton("Настройки системы")
            btn_sys.setStyleSheet(f"""
                background: white; border: 1px solid {COLORS['border']}; 
                border-radius: 8px; padding: 10px 20px; color: {COLORS['t1']};
            """)
            btn_sys.clicked.connect(lambda: bus.navigate_to.emit("system", {}))
            
            actions_l.addWidget(btn_manage)
            actions_l.addWidget(btn_sys)
            actions_l.addStretch()
            self.clayout.insertLayout(1, actions_l)
            self.quick_actions_added = True

    def display_recent_logs(self, logs: list[SystemLogEntry]):
        # Очистка
        for i in reversed(range(self.log_container.count())):
            item = self.log_container.itemAt(i).widget()
            if item: item.setParent(None)

        for log in logs:
            row = QFrame()
            row.setStyleSheet(f"background: {COLORS['bg']}; border-radius: 6px;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 8, 12, 8)
            
            lbl_time = QLabel(log.timestamp)
            lbl_time.setFixedWidth(60)
            lbl_time.setStyleSheet(f"color: {COLORS['t3']}; font-weight: bold;")
            
            lbl_msg = QLabel(log.message)
            lbl_msg.setStyleSheet(f"color: {COLORS['t1']};")
            lbl_msg.setWordWrap(True)
            
            rl.addWidget(lbl_time)
            rl.addWidget(lbl_msg, 1)
            self.log_container.addWidget(row)
