# ui/styles/dashboard_theme.py
"""
Единый источник всех констант дизайна для Dashboard-экранов из макета.
"""

COLORS = {
    # Акцент
    "accent":        "#0078D4",
    "accent_hover":  "#006CBD",
    "accent_light":  "#4DA3E8",
    "accent_dark":   "#005A9E",
    # Семантика
    "success":       "#107C10",
    "success_bg":    "#DFF6DD",
    "warning":       "#9D5D00",
    "warning_bg":    "#FFF4CE",
    "error":         "#C42B1C",
    "error_bg":      "#FDE7E9",
    # Фоны
    "bg":            "#F0F2F5",   # основной фон страниц
    "card":          "#FFFFFF",   # фон карточек
    "sidebar":       "#0D1B2E",   # фон сайдбара
    # Текст
    "t1":            "#1A1A2E",   # основной текст
    "t2":            "#5A6478",   # вторичный
    "t3":            "#9BA3B4",   # третичный / метки
    # Тени (передавать как stylesheet box-shadow или рисовать через QGraphicsDropShadow)
    "shadow_sm":     "0 1px 3px rgba(0,0,0,.06)",
    "shadow_md":     "0 4px 16px rgba(0,0,0,.08)",
    "shadow_lg":     "0 12px 40px rgba(0,0,0,.12)",
    # Граница
    "border":        "rgba(0,0,0,0.07)",
}

RADIUS = {
    "card":    12,   # --r: 12px
    "control": 8,
    "pill":    100,
    "badge":   6,
}

SIDEBAR_WIDTH = 240   # px
TOPBAR_HEIGHT = 60    # px
FONT = "Segoe UI Variable"
