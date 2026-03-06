# ui/styles/animations.py
"""
Система анимаций EduCase — 14 анимационных функций.
Все используют токены из theme.py (ANIM dict).
ПРАВИЛО: Все QPropertyAnimation используют DeleteWhenStopped или хранят ссылки.
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    QTimer,
    Qt,
)
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget

from ui.styles.theme import ANIM


# ── 1. fade_in ────────────────────────────────────────────────────────────
def fade_in(widget: QWidget, duration: int = ANIM["normal"]) -> QPropertyAnimation:
    """opacity: 0.0 → 1.0 | OutCubic"""
    eff = _ensure_opacity_effect(widget)
    eff.setOpacity(0.0)
    widget.show()
    anim = QPropertyAnimation(eff, b"opacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    anim.start()
    widget.setProperty("_fade_anim", anim)  # prevent GC
    return anim


# ── 2. fade_out ───────────────────────────────────────────────────────────
def fade_out(
    widget: QWidget,
    duration: int = ANIM["fast"],
    on_done: Callable[[], None] | None = None,
) -> QPropertyAnimation:
    """opacity: 1.0 → 0.0 | InCubic → on_done callback"""
    eff = _ensure_opacity_effect(widget)
    anim = QPropertyAnimation(eff, b"opacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)
    anim.setEasingCurve(QEasingCurve.InCubic)
    if on_done:
        anim.finished.connect(on_done)
    anim.start()
    widget.setProperty("_fade_anim", anim)
    return anim


# ── 3. slide_up ──────────────────────────────────────────────────────────
def slide_up(
    widget: QWidget, offset: int = 20, duration: int = ANIM["medium"]
) -> QParallelAnimationGroup:
    """pos.y: +offset → 0 + opacity: 0 → 1 | OutExpo"""
    eff = _ensure_opacity_effect(widget)
    eff.setOpacity(0.0)
    start_pos = widget.pos()
    widget.move(start_pos.x(), start_pos.y() + offset)
    widget.show()

    group = QParallelAnimationGroup(widget)

    # Position
    anim_pos = QPropertyAnimation(widget, b"pos", widget)
    anim_pos.setDuration(duration)
    anim_pos.setStartValue(QPoint(start_pos.x(), start_pos.y() + offset))
    anim_pos.setEndValue(start_pos)
    anim_pos.setEasingCurve(QEasingCurve.OutExpo)
    group.addAnimation(anim_pos)

    # Opacity
    anim_op = QPropertyAnimation(eff, b"opacity", widget)
    anim_op.setDuration(duration)
    anim_op.setStartValue(0.0)
    anim_op.setEndValue(1.0)
    anim_op.setEasingCurve(QEasingCurve.OutCubic)
    group.addAnimation(anim_op)

    group.start()
    widget.setProperty("_slide_anim", group)
    return group


# ── 4. slide_from_right ──────────────────────────────────────────────────
def slide_from_right(
    widget: QWidget, duration: int = ANIM["normal"]
) -> QParallelAnimationGroup:
    """pos.x: +30 → 0 + opacity: 0 → 1 | OutCubic — переход между страницами"""
    eff = _ensure_opacity_effect(widget)
    eff.setOpacity(0.0)
    start_pos = widget.pos()
    widget.move(start_pos.x() + 30, start_pos.y())
    widget.show()

    group = QParallelAnimationGroup(widget)

    anim_pos = QPropertyAnimation(widget, b"pos", widget)
    anim_pos.setDuration(duration)
    anim_pos.setStartValue(QPoint(start_pos.x() + 30, start_pos.y()))
    anim_pos.setEndValue(start_pos)
    anim_pos.setEasingCurve(QEasingCurve.OutCubic)
    group.addAnimation(anim_pos)

    anim_op = QPropertyAnimation(eff, b"opacity", widget)
    anim_op.setDuration(duration)
    anim_op.setStartValue(0.0)
    anim_op.setEndValue(1.0)
    anim_op.setEasingCurve(QEasingCurve.OutCubic)
    group.addAnimation(anim_op)

    group.start()
    widget.setProperty("_slide_anim", group)
    return group


# ── 5. sidebar_expand / sidebar_collapse ─────────────────────────────────
def sidebar_expand(
    sidebar: QWidget, from_w: int = 60, to_w: int = 240, duration: int = ANIM["normal"]
) -> QPropertyAnimation:
    """Анимация раскрытия сайдбара."""
    anim = QPropertyAnimation(sidebar, b"minimumWidth", sidebar)
    anim.setDuration(duration)
    anim.setStartValue(from_w)
    anim.setEndValue(to_w)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    anim.start()

    anim2 = QPropertyAnimation(sidebar, b"maximumWidth", sidebar)
    anim2.setDuration(duration)
    anim2.setStartValue(from_w)
    anim2.setEndValue(to_w)
    anim2.setEasingCurve(QEasingCurve.OutCubic)
    anim2.start()

    sidebar.setProperty("_expand_anim", anim)
    sidebar.setProperty("_expand_anim2", anim2)
    return anim


def sidebar_collapse(
    sidebar: QWidget, from_w: int = 240, to_w: int = 60, duration: int = ANIM["normal"]
) -> QPropertyAnimation:
    """Анимация сворачивания сайдбара."""
    return sidebar_expand(sidebar, from_w, to_w, duration)


# ── 6. shake ─────────────────────────────────────────────────────────────
def shake(widget: QWidget) -> QSequentialAnimationGroup:
    """pos.x: -4 → +4 → -4 → +4 → -2 → +2 → 0 | 50ms/step — неверный ответ"""
    origin = widget.pos()
    group = QSequentialAnimationGroup(widget)

    offsets = [-4, 4, -4, 4, -2, 2, 0]
    for dx in offsets:
        anim = QPropertyAnimation(widget, b"pos", widget)
        anim.setDuration(50)
        anim.setEndValue(QPoint(origin.x() + dx, origin.y()))
        anim.setEasingCurve(QEasingCurve.OutSine)
        group.addAnimation(anim)

    group.start()
    widget.setProperty("_shake_anim", group)
    return group


# ── 7. stagger_cards ─────────────────────────────────────────────────────
def stagger_cards(cards: list[QWidget], delay_ms: int = 50) -> None:
    """Каскадное появление карточек: QTimer.singleShot(i*delay, fade_in)"""
    for i, card in enumerate(cards):
        card.hide()
        QTimer.singleShot(i * delay_ms, lambda c=card: fade_in(c, ANIM["fast"]))


# ── 8. score_pop ─────────────────────────────────────────────────────────
def score_pop(label: QWidget) -> None:
    """
    Эффект «подпрыгивания» числа баллов.
    step1 (40ms): font +4 → step2 (80ms): font обратно.
    """
    font = label.font()
    original_size = font.pointSize()

    def step1() -> None:
        f = label.font()
        f.setPointSize(original_size + 4)
        label.setFont(f)
        QTimer.singleShot(80, step2)

    def step2() -> None:
        f = label.font()
        f.setPointSize(original_size)
        label.setFont(f)

    QTimer.singleShot(0, step1)


# ── 9. progress_ring_fill ────────────────────────────────────────────────
def progress_ring_fill(
    ring_widget: QWidget,
    from_val: int = 0,
    to_val: int = 100,
    duration: int = 1500,
) -> QPropertyAnimation:
    """QPropertyAnimation на custom property 'value' | OutCubic"""
    anim = QPropertyAnimation(ring_widget, b"value", ring_widget)
    anim.setDuration(duration)
    anim.setStartValue(from_val)
    anim.setEndValue(to_val)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    anim.start()
    ring_widget.setProperty("_ring_anim", anim)
    return anim


# ── 10. feedback_correct ─────────────────────────────────────────────────
def feedback_correct(widget: QWidget) -> None:
    """bg → success_bg + check icon scale 0→1 | 150ms OutBack"""
    widget.setStyleSheet(widget.styleSheet() + " background: #DFF6DD;")
    fade_in(widget, ANIM["fast"])


# ── 11. feedback_wrong ───────────────────────────────────────────────────
def feedback_wrong(widget: QWidget) -> None:
    """bg → error_bg + shake 350ms"""
    widget.setStyleSheet(widget.styleSheet() + " background: #FDE7E9;")
    shake(widget)


# ── 12. toast_show ───────────────────────────────────────────────────────
def toast_show(toast: QWidget) -> QParallelAnimationGroup:
    """slide_up(40px) + fade_in | 300ms OutExpo"""
    return slide_up(toast, offset=40, duration=ANIM["medium"])


def toast_hide(
    toast: QWidget, on_done: Callable[[], None] | None = None
) -> QPropertyAnimation:
    """fade_out | 200ms InCubic → deleteLater"""
    return fade_out(toast, ANIM["normal"], on_done=on_done)


# ── 13. loading_shimmer (для LoadingOverlay) ─────────────────────────────
# Реализуется в loading_overlay.py через кастомный paintEvent + QPropertyAnimation


# ── 14. slide_in_right (для dock panels) ─────────────────────────────────
def slide_in_right(
    panel: QWidget, width: int = 300, duration: int = ANIM["normal"]
) -> QPropertyAnimation:
    """pos.x: parent.width → parent.width - width | OutCubic"""
    parent = panel.parentWidget()
    if parent:
        start_x = parent.width()
        end_x = parent.width() - width
    else:
        start_x = panel.x() + width
        end_x = panel.x()

    panel.move(start_x, panel.y())
    panel.show()

    anim = QPropertyAnimation(panel, b"pos", panel)
    anim.setDuration(duration)
    anim.setStartValue(QPoint(start_x, panel.y()))
    anim.setEndValue(QPoint(end_x, panel.y()))
    anim.setEasingCurve(QEasingCurve.OutCubic)
    anim.start()
    panel.setProperty("_slide_in_anim", anim)
    return anim


# ── Helpers ──────────────────────────────────────────────────────────────
def _ensure_opacity_effect(widget: QWidget) -> QGraphicsOpacityEffect:
    """Получает или создаёт QGraphicsOpacityEffect на виджете."""
    eff = widget.graphicsEffect()
    if not isinstance(eff, QGraphicsOpacityEffect):
        eff = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(eff)
    return eff
