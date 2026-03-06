# ui/styles/stylesheet.py
"""
Глобальный QSS (Qt Style Sheet) для приложения EduCase.
Генерируется из токенов theme.py. Применяется через app.setStyleSheet().
"""
from ui.styles.theme import COLORS, RADIUS, SPACING, TYPO


def generate_stylesheet(accent: str | None = None) -> str:
    """
    Генерирует полный QSS для приложения.
    accent: переопределяет COLORS['accent'] (пользовательская настройка).
    """
    c = COLORS.copy()
    if accent:
        c["accent"] = accent

    return f"""
    /* ══ GLOBAL ══ */
    QWidget {{
        font-family: {TYPO['font']};
        font-size: {TYPO['body']}px;
        color: {c['text_primary']};
    }}

    QMainWindow, QDialog {{
        background: {c['bg_base']};
    }}

    /* ══ BUTTONS ══ */
    QPushButton {{
        background: {c['bg_elevated']};
        border: 1px solid {c['stroke_control']};
        border-radius: {RADIUS['control']}px;
        padding: {SPACING['sm']}px {SPACING['lg']}px;
        font-size: {TYPO['body']}px;
        min-height: 32px;
    }}
    QPushButton:hover {{
        background: {c['state_hover']};
        border-color: {c['stroke_control']};
    }}
    QPushButton:pressed {{
        background: {c['state_pressed']};
    }}
    QPushButton:disabled {{
        color: {c['text_disabled']};
        background: {c['bg_layer']};
        border-color: {c['stroke_divider']};
    }}

    /* Accent Button */
    QPushButton[class="accent"] {{
        background: {c['accent']};
        color: {c['text_on_accent']};
        border: none;
        font-weight: 600;
    }}
    QPushButton[class="accent"]:hover {{
        background: {c['accent_hover']};
    }}
    QPushButton[class="accent"]:pressed {{
        background: {c['accent_pressed']};
    }}

    /* ══ LINE EDIT ══ */
    QLineEdit {{
        background: {c['bg_elevated']};
        border: 1px solid {c['stroke_control']};
        border-radius: {RADIUS['control']}px;
        padding: {SPACING['sm']}px {SPACING['md']}px;
        font-size: {TYPO['body']}px;
        min-height: 34px;
        selection-background-color: {c['accent_light']};
    }}
    QLineEdit:focus {{
        border: 2px solid {c['accent']};
        padding: {SPACING['sm'] - 1}px {SPACING['md'] - 1}px;
    }}
    QLineEdit:disabled {{
        background: {c['bg_layer']};
        color: {c['text_disabled']};
    }}

    /* ══ TEXT EDIT ══ */
    QTextEdit, QTextBrowser {{
        background: {c['bg_elevated']};
        border: 1px solid {c['stroke_control']};
        border-radius: {RADIUS['control']}px;
        padding: {SPACING['sm']}px;
        selection-background-color: {c['accent_light']};
    }}
    QTextEdit:focus {{
        border: 2px solid {c['accent']};
    }}

    /* ══ COMBO BOX ══ */
    QComboBox {{
        background: {c['bg_elevated']};
        border: 1px solid {c['stroke_control']};
        border-radius: {RADIUS['control']}px;
        padding: {SPACING['sm']}px {SPACING['md']}px;
        min-height: 34px;
    }}
    QComboBox:hover {{
        border-color: {c['accent']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background: {c['bg_elevated']};
        border: 1px solid {c['stroke_control']};
        border-radius: {RADIUS['control']}px;
        selection-background-color: {c['state_selected']};
    }}

    /* ══ CHECK BOX / RADIO ══ */
    QCheckBox, QRadioButton {{
        spacing: {SPACING['sm']}px;
    }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 18px;
        height: 18px;
    }}

    /* ══ SCROLL AREA ══ */
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(0, 0, 0, 0.15);
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: rgba(0, 0, 0, 0.25);
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 8px;
    }}
    QScrollBar::handle:horizontal {{
        background: rgba(0, 0, 0, 0.15);
        border-radius: 4px;
        min-width: 30px;
    }}

    /* ══ TAB WIDGET ══ */
    QTabWidget::pane {{
        border: none;
        background: transparent;
    }}
    QTabBar::tab {{
        background: transparent;
        padding: {SPACING['sm']}px {SPACING['lg']}px;
        margin-right: {SPACING['xs']}px;
        border-bottom: 2px solid transparent;
        color: {c['text_secondary']};
        font-size: {TYPO['body']}px;
    }}
    QTabBar::tab:selected {{
        color: {c['accent']};
        border-bottom: 2px solid {c['accent']};
        font-weight: 600;
    }}
    QTabBar::tab:hover {{
        color: {c['text_primary']};
        background: {c['state_hover']};
    }}

    /* ══ TABLE VIEW ══ */
    QTableView, QTreeView {{
        background: {c['bg_elevated']};
        border: 1px solid {c['stroke_card']};
        border-radius: {RADIUS['card']}px;
        gridline-color: {c['stroke_divider']};
        selection-background-color: {c['state_selected']};
        alternate-background-color: {c['bg_layer']};
    }}
    QHeaderView::section {{
        background: {c['bg_layer']};
        border: none;
        border-bottom: 1px solid {c['stroke_divider']};
        padding: {SPACING['sm']}px {SPACING['md']}px;
        font-weight: 600;
        font-size: {TYPO['caption']}px;
        color: {c['text_secondary']};
    }}

    /* ══ GROUP BOX ══ */
    QGroupBox {{
        border: 1px solid {c['stroke_card']};
        border-radius: {RADIUS['card']}px;
        margin-top: 16px;
        padding-top: 16px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: {SPACING['md']}px;
        padding: 0 {SPACING['sm']}px;
    }}

    /* ══ PROGRESS BAR ══ */
    QProgressBar {{
        background: {c['bg_layer']};
        border: none;
        border-radius: 3px;
        height: 6px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background: {c['accent']};
        border-radius: 3px;
    }}

    /* ══ TOOLTIP ══ */
    QToolTip {{
        background: {c['text_primary']};
        color: {c['text_on_accent']};
        border: none;
        border-radius: {RADIUS['control']}px;
        padding: {SPACING['xs']}px {SPACING['sm']}px;
        font-size: {TYPO['caption']}px;
    }}

    /* ══ LABEL ══ */
    QLabel {{
        background: transparent;
    }}
    QLabel[class="title"] {{
        font-size: {TYPO['title']}px;
        font-weight: 600;
        color: {c['text_primary']};
    }}
    QLabel[class="subtitle"] {{
        font-size: {TYPO['subtitle']}px;
        color: {c['text_secondary']};
    }}
    QLabel[class="caption"] {{
        font-size: {TYPO['caption']}px;
        color: {c['text_secondary']};
    }}

    /* ══ SPLITTER ══ */
    QSplitter::handle {{
        background: {c['stroke_divider']};
    }}
    QSplitter::handle:horizontal {{
        width: 1px;
    }}
    QSplitter::handle:vertical {{
        height: 1px;
    }}

    /* ══ MENU ══ */
    QMenu {{
        background: {c['bg_elevated']};
        border: 1px solid {c['stroke_control']};
        border-radius: {RADIUS['overlay']}px;
        padding: {SPACING['xs']}px;
    }}
    QMenu::item {{
        padding: {SPACING['sm']}px {SPACING['lg']}px;
        border-radius: {RADIUS['control']}px;
    }}
    QMenu::item:selected {{
        background: {c['state_selected']};
    }}
    """
