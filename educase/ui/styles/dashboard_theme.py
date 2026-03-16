# ui/styles/dashboard_theme.py
"""
Единый источник всех констант дизайна для Dashboard-экранов из макета.
"""

COLORS = {
    # Акцент
    "accent":        "#4F46E5",   # Modern Indigo
    "accent_hover":  "#4338CA",
    "accent_light":  "#818CF8",
    "accent_dark":   "#3730A3",
    # Семантика
    "success":       "#10B981",   # Emerald
    "success_bg":    "#ECFDF5",
    "warning":       "#F59E0B",   # Amber
    "warning_bg":    "#FFFBEB",
    "error":         "#EF4444",   # Rose/Red
    "error_bg":      "#FEF2F2",
    # Фоны
    "bg":            "#F8FAFC",   # Slate 50
    "card":          "#FFFFFF",   
    "sidebar":       "#0F172A",   # Slate 900
    # Текст
    "t1":            "#1E293B",   # Slate 800
    "t2":            "#475569",   # Slate 600
    "t3":            "#94A3B8",   # Slate 400
    # Тени
    "shadow_sm":     "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "shadow_md":     "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    "shadow_lg":     "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    # Граница
    "border":        "#E2E8F0",   # Slate 200
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
