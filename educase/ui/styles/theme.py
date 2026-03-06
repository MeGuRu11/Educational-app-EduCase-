# ui/styles/theme.py
"""
Дизайн-токены приложения EduCase.
Цвета, радиусы, отступы, типографика, тайминги анимаций.
Все компоненты используют эти токены — нет ad-hoc значений.
"""

COLORS = {
    # Акцент
    "accent": "#0078D4",
    "accent_hover": "#006CBD",
    "accent_pressed": "#005BA5",
    "accent_light": "#4DA3E8",
    "accent_dark": "#005A9E",
    # Семантические
    "success": "#107C10",
    "success_bg": "#DFF6DD",
    "warning": "#9D5D00",
    "warning_bg": "#FFF4CE",
    "error": "#C42B1C",
    "error_bg": "#FDE7E9",
    "info": "#0078D4",
    "info_bg": "#EFF6FC",
    # Фоны
    "bg_base": "#F3F3F3",
    "bg_elevated": "#FFFFFF",
    "bg_layer": "#FAFAFA",
    "sidebar_bg": "#EEEEEE",
    # Текст
    "text_primary": "#1A1A1A",
    "text_secondary": "#6B6B6B",
    "text_disabled": "#ABABAB",
    "text_on_accent": "#FFFFFF",
    "text_link": "#0078D4",
    # Состояния
    "state_hover": "rgba(0,0,0,0.04)",
    "state_pressed": "rgba(0,0,0,0.08)",
    "state_selected": "rgba(0,120,212,0.10)",
    # Обводки
    "stroke_card": "rgba(0,0,0,0.08)",
    "stroke_control": "rgba(0,0,0,0.14)",
    "stroke_divider": "rgba(0,0,0,0.05)",
}

RADIUS = {
    "control": 4,
    "card": 8,
    "overlay": 8,
    "large": 12,
    "xlarge": 16,
}

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "xxl": 32,
}

TYPO = {
    "font": "Segoe UI Variable, Segoe UI, DejaVu Sans, Arial",
    "display": 40,
    "title_large": 28,
    "title": 20,
    "subtitle": 16,
    "body_large": 14,
    "body": 13,
    "caption": 11,
}

ANIM = {
    "instant": 80,  # hover press, immediate feedback
    "fast": 150,  # hover enter/leave, badge
    "normal": 220,  # page transitions, sidebar item
    "medium": 300,  # toast, dialogs, progress
    "slow": 500,  # progress ring fill, score counter
}
