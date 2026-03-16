# ui/styles/chart_style.py
"""
Единые стили для графиков matplotlib.
"""

import matplotlib as mpl

def apply_dashboard_style():
    """
    Применяет стили, согласованные с дизайн-системой EduCase:
    цвета шрифтов, отключение рамок (spines), кастомная сетка и т.д.
    Вызывать один раз при инициализации приложения или графиков.
    """
    mpl.rcParams.update({
        "font.family":       "Segoe UI Variable",
        "font.size":         11,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.spines.left":  False,
        "axes.spines.bottom":False,
        "axes.grid":         True,
        "axes.grid.axis":    "y",
        "grid.color":        "#E6E8EA",
        "grid.linewidth":    0.8,
        "axes.facecolor":    "white",
        "figure.facecolor":  "white",
        "xtick.color":       "#9BA3B4",
        "ytick.color":       "#9BA3B4",
        "text.color":        "#5A6478",
        "axes.labelcolor":   "#5A6478",
    })
