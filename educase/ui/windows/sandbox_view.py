# ui/windows/sandbox_view.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QGridLayout, QPushButton
from PySide6.QtCore import Qt

# Импортируем все наши компоненты
from ui.components.card import Card
from ui.components.badge import Badge
from ui.components.score_badge import ScoreBadge
from ui.components.avatar import Avatar
from ui.components.progress_bar import ProgressBar
from ui.components.progress_ring import ProgressRing
from ui.components.case_card import CaseCard
from ui.components.stat_card import StatCard
from ui.components.search_bar import SearchBar
from ui.components.empty_state import EmptyState
from ui.components.loading_overlay import LoadingOverlay
from ui.components.dialog import ConfirmDialog
from ui.components.table_view import TableView
from ui.components.accordion import Accordion
from ui.components.stepper import Stepper
from ui.components.rich_text_editor import RichTextEditor
from ui.components.image_picker import ImagePicker

from ui.styles.theme import COLORS

class SandboxView(QWidget):
    """
    Песочница для тестирования UI компонентов.
    Это временный экран, чтобы оценить дизайн перед сборкой настоящих страниц.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _create_section(self, title: str, widget_func):
        group = QWidget()
        l = QVBoxLayout(group)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(12)
        
        lbl = QLabel(title)
        lbl.setStyleSheet(f"background: transparent; font-size: 18px; font-weight: bold; color: {COLORS['text_primary']};")
        l.addWidget(lbl)
        
        container = QWidget()
        container.setObjectName("sandboxContainer")
        container.setStyleSheet(f"#sandboxContainer {{ background: {COLORS['bg_layer']}; border: 1px dashed {COLORS['stroke_card']}; border-radius: 8px; }}")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(16, 16, 16, 16)
        
        # Call the passed function to generate the content for this section
        widget_func(cl)
        
        l.addWidget(container)
        return group

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        content.setStyleSheet(f"background: {COLORS['bg_base']};")
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(32)
        
        title = QLabel("UI Sandbox (Песочница Компонентов)")
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLORS['accent']};")
        main_layout.addWidget(title)
        
        grid = QGridLayout()
        grid.setSpacing(24)
        
        # 1. Cards & Badges
        def build_cards(layout):
            hl = QHBoxLayout()
            hl.addWidget(Card(hover_effect=True))
            hl.addWidget(StatCard("142", "Пройдено кейсов", "check-circle", "success"))
            hl.addWidget(CaseCard("Острый Аппендицит", "Пациент 45 лет жалуется на сильные боли в животе...", 2))
            layout.addLayout(hl)
            
            bl = QHBoxLayout()
            bl.addWidget(Badge("Новое", "accent"))
            bl.addWidget(Badge("В процессе", "warning"))
            bl.addWidget(Badge("Ошибка", "error"))
            bl.addWidget(Badge("Завершено", "success"))
            bl.addWidget(ScoreBadge(8.5, 10))
            bl.addStretch()
            layout.addLayout(bl)
            
        # 2. Progress & Avatars
        def build_progress(layout):
            hl = QHBoxLayout()
            
            pb1 = ProgressBar()
            pb1.set_value(0.4, animated=False)
            pb2 = ProgressBar()
            pb2.set_value(1.0, animated=False)
            
            pbl = QVBoxLayout()
            progress_lbl = QLabel("Прогресс бар (40% и 100%)")
            progress_lbl.setStyleSheet("background: transparent;")
            pbl.addWidget(progress_lbl)
            pbl.addWidget(pb1)
            pbl.addWidget(pb2)
            
            hl.addLayout(pbl)
            
            pr1 = ProgressRing(60)
            pr1.set_value(0.75, animated=False)
            hl.addWidget(pr1)
            
            hl.addWidget(Avatar(40, "Иван Иванов"))
            hl.addWidget(Avatar(60, "Анна Смирнова"))
            layout.addLayout(hl)
            
        # 3. Interactive (Search, Empty, Image)
        def build_interactive(layout):
            hl = QHBoxLayout()
            hl.addWidget(SearchBar("Искать задания..."))
            hl.addWidget(ImagePicker())
            layout.addLayout(hl)
            
            layout.addWidget(EmptyState("Ничего не найдено", "Попробуйте изменить запрос", "document"))

        # 4. Stepper & Accordion
        def build_stepper(layout):
            layout.addWidget(Stepper(["Подготовка", "Осмотр", "Лечение", "Итоги"], current_step=1))
            
            acc = Accordion()
            acc.add_section("Модуль 1: Введение", QLabel("Описание первого модуля."))
            acc.add_section("Модуль 2: Практика", QLabel("Здесь будут практические задания."))
            layout.addWidget(acc)
            
        # 5. Dialog test
        def build_dialogs(layout):
            btn = QPushButton("Открыть диалог")
            btn.setStyleSheet(f"background: {COLORS['accent']}; color: white; padding: 12px; border-radius: 6px;")
            
            def show_dialog():
                dlg = ConfirmDialog(self.window())
                dlg.exec()
                
            btn.clicked.connect(show_dialog)
            layout.addWidget(btn)
            
            btn_constructor = QPushButton("Открыть Конструктор (Этап 4)")
            btn_constructor.setStyleSheet(f"background: {COLORS['accent']}; color: white; padding: 12px; border-radius: 6px;")
            
            def show_constructor():
                from ui.task_constructor.constructor_dialog import ConstructorDialog
                dlg = ConstructorDialog(parent=self.window())
                dlg.exec()
                
            btn_constructor.clicked.connect(show_constructor)
            layout.addWidget(btn_constructor)

        # 6. RichText
        def build_richtext(layout):
            rt = RichTextEditor()
            rt.set_html("<h1>Тестовый текст</h1><p>Это пример <b>RichTextEditor</b> в действии.</p>")
            layout.addWidget(rt)

        # Add to grid
        grid.addWidget(self._create_section("1. Карточки и Бейджи", build_cards), 0, 0)
        grid.addWidget(self._create_section("2. Индикаторы и Аватары", build_progress), 0, 1)
        grid.addWidget(self._create_section("3. Поиск, Empty State и Загрузка", build_interactive), 1, 0)
        grid.addWidget(self._create_section("4. Аккордеон и Степер", build_stepper), 1, 1)
        grid.addWidget(self._create_section("5. Всплывающие окна", build_dialogs), 2, 0)
        grid.addWidget(self._create_section("6. Текстовый Редактор", build_richtext), 2, 1)

        main_layout.addLayout(grid)
        scroll.setWidget(content)
        
        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.addWidget(scroll)
