# ui/windows/splash_window.py
"""
Загрузочный экран EduCase.
Показывается до LoginWindow, пока выполняются run_migrations() и build_container().
Гарантированное время показа: минимум 2500ms (см. main.py).

Тайминги согласованы с HTML-превью: educase_brand_preview.html
Все анимации воспроизводят CSS-анимации из превью через Qt-аналоги.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Property as _QtProp
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt, QTimer
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QGuiApplication,
    QLinearGradient,
    QPainter,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import QGraphicsOpacityEffect, QProgressBar, QWidget

BASE_DIR = Path(__file__).parent.parent.parent   # корень проекта (educase/)


class SplashScreen(QWidget):
    """
    Анимированный splash-экран EduCase.

    Использование в main.py:
        splash = SplashScreen()
        splash.start()
        t_start = time.monotonic()
        app.processEvents()
        # ... run_migrations(), build_container() ...
        elapsed_ms = int((time.monotonic() - t_start) * 1000)
        delay_ms   = max(0, 2500 - elapsed_ms)
        QTimer.singleShot(delay_ms, lambda: splash.finish(login_window))
    """

    # ── Тайминги (ms) — соответствуют CSS-анимациям из educase_brand_preview.html
    T_WINDOW_FADE_IN    = 300    # Phase 1: fade-in всего окна
    T_ICON_START        = 200    # Phase 2: задержка до анимации иконки
    T_ICON_DURATION     = 650    # Phase 2: длительность "пружины" OutBack
    T_TITLE_START       = 700    # Phase 3: первая буква поднимается
    T_LETTER_STAGGER    = 50     # Phase 3: задержка между буквами (7 букв = +350ms)
    T_SUBTITLE_START    = 1160   # Phase 4: subtitle fade-in
    T_SUBTITLE_FADE     = 400    # Phase 4: длительность fade-in subtitle
    T_PROGRESS_START    = 1400   # Phase 5: появление прогресс-бара
    T_PROGRESS_DURATION = 2300   # Phase 5: заполнение 0→100% (OutCubic)
    T_FINISH_FADE       = 400    # Phase 7: fade-out перед показом LoginWindow

    W, H = 540, 330              # размер окна (px)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint  |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SplashScreen          # не попадает в таскбар / Alt+Tab
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.W, self.H)
        self._center()

        # ── состояние иконки (анимируется через paintEvent)
        self._icon_scale        = 0.42    # начальный масштаб (CSS: transform:scale(0.42))
        self._icon_opacity      = 0.0
        self._icon_step         = 0
        self._icon_total_steps  = 22
        self._icon_pixmap       = self._load_icon_pixmap()

        # ── окно начинает с 0 непрозрачности
        self.setWindowOpacity(0.0)

        # ── буквы заголовка "EduCase" (создаются в _build_letters)
        self._letters: list[_LetterLabel] = []

        # ── subtitle QLabel (создаётся в _show_subtitle)
        self._subtitle_widget: QWidget | None = None

        # ── прогресс-бар (Phase 5)
        self._pbar = QProgressBar(self)
        self._pbar.setGeometry((self.W - 200) // 2, self.H - 42, 200, 3)
        self._pbar.setTextVisible(False)
        self._pbar.setRange(0, 100)
        self._pbar.setValue(0)
        self._pbar.setStyleSheet("""
            QProgressBar {
                background: rgba(255,255,255,20);
                border: none;
                border-radius: 1px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #005eb0, stop:1 #4DA3E8);
                border-radius: 1px;
            }
        """)
        self._pbar.hide()

    # ─────────────────────────────────────────────────────
    # Инициализация
    # ─────────────────────────────────────────────────────

    def _center(self) -> None:
        """Центрирует окно на основном экране."""
        screen = QGuiApplication.primaryScreen().geometry()
        self.move(
            (screen.width()  - self.W) // 2,
            (screen.height() - self.H) // 2,
        )

    def _load_icon_pixmap(self) -> QPixmap | None:
        """
        Рендерит assets/icon_master.svg в QPixmap 72×72 через QSvgRenderer.
        Возвращает None если файл не найден (иконка просто не показывается).
        """
        svg_path = BASE_DIR / "assets" / "icon_master.svg"
        if not svg_path.exists():
            return None
        try:
            from PySide6.QtSvg import QSvgRenderer
            pix = QPixmap(72, 72)
            pix.fill(Qt.GlobalColor.transparent)
            renderer = QSvgRenderer(str(svg_path))
            painter = QPainter(pix)
            renderer.render(painter, QRectF(0, 0, 72, 72))
            painter.end()
            return pix
        except Exception:
            return None

    # ─────────────────────────────────────────────────────
    # Публичный API
    # ─────────────────────────────────────────────────────

    def start(self) -> None:
        """
        Показывает окно и запускает все анимации.
        Вызывать вместо show(). После вызова — app.processEvents().
        """
        self.show()

        # Phase 1: окно fade-in 0.0→1.0
        self._anim_window = QPropertyAnimation(self, b"windowOpacity", self)
        self._anim_window.setDuration(self.T_WINDOW_FADE_IN)
        self._anim_window.setStartValue(0.0)
        self._anim_window.setEndValue(1.0)
        self._anim_window.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_window.start()

        # Phase 2: иконка — OutBack через ручной QTimer (QPropertyAnimation не даёт OutBack)
        QTimer.singleShot(self.T_ICON_START, self._start_icon_anim)

        # Phase 3: буквы "EduCase" по одной снизу вверх
        self._build_letters()
        for i, letter in enumerate(self._letters):
            delay = self.T_TITLE_START + i * self.T_LETTER_STAGGER
            QTimer.singleShot(delay, letter.appear)

        # Phase 4: subtitle fade-in
        QTimer.singleShot(self.T_SUBTITLE_START, self._show_subtitle)

        # Phase 5: прогресс-бар
        QTimer.singleShot(self.T_PROGRESS_START, self._start_progress)

    def finish(self, login_window: QWidget) -> None:
        """
        Phase 7: fade-out splash → show login_window с fade-in.
        Вызывается из QTimer.singleShot после гарантированного минимума показа.
        """
        anim = QPropertyAnimation(self, b"windowOpacity", self)
        anim.setDuration(self.T_FINISH_FADE)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.finished.connect(lambda: self._on_finish(login_window))
        anim.start()
        self._anim_finish = anim   # держим ссылку

    def _on_finish(self, login_window: QWidget) -> None:
        self.close()
        login_window.show()
        # fade-in LoginWindow
        login_window.setWindowOpacity(0.0)
        a = QPropertyAnimation(login_window, b"windowOpacity", login_window)
        a.setDuration(300)
        a.setStartValue(0.0)
        a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.start()
        login_window._splash_fade = a   # type: ignore

    # ─────────────────────────────────────────────────────
    # Phase 2: иконка (OutBack через ручной таймер)
    # ─────────────────────────────────────────────────────

    def _start_icon_anim(self) -> None:
        interval_ms = max(1, self.T_ICON_DURATION // self._icon_total_steps)
        t = QTimer(self)
        t.setInterval(interval_ms)
        t.timeout.connect(self._tick_icon)
        t.start()
        self._icon_timer = t

    def _tick_icon(self) -> None:
        self._icon_step += 1
        t = min(1.0, self._icon_step / self._icon_total_steps)

        # OutBack easing: воспроизводит cubic-bezier(.34,1.56,.64,1) из CSS
        c1, c3 = 1.70158, 2.70158
        ease = 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

        self._icon_scale   = max(0.0, 0.42 + 0.58 * ease)
        self._icon_opacity = min(1.0, t * 1.8)
        self.update()   # trigger paintEvent

        if self._icon_step >= self._icon_total_steps:
            self._icon_timer.stop()
            self._icon_scale, self._icon_opacity = 1.0, 1.0
            self.update()

    # ─────────────────────────────────────────────────────
    # Phase 3: буквы заголовка
    # ─────────────────────────────────────────────────────

    def _build_letters(self) -> None:
        """Создаёт _LetterLabel для каждой буквы 'EduCase' и расставляет их по центру."""
        text   = "EduCase"
        bold   = "Edu"          # жирный + синий #4DA3E8
        font_b = QFont("Segoe UI Variable", 26, QFont.Weight.DemiBold)
        font_n = QFont("Segoe UI Variable", 26, QFont.Weight.Light)

        # Суммарная ширина для центрирования
        widths: list[int] = []
        total_w = 0
        for ch in text:
            f = font_b if ch in bold else font_n
            w = QFontMetrics(f).horizontalAdvance(ch) + 1
            widths.append(w)
            total_w += w

        x = (self.W - total_w) // 2
        y = 172   # иконка 72px (cy=124) + 12px margin + ~36 baseline

        for i, ch in enumerate(text):
            f   = font_b if ch in bold else font_n
            col = QColor("#4DA3E8") if ch in bold else QColor(255, 255, 255, 220)
            lbl = _LetterLabel(ch, f, col, self)
            lbl.move(x, y)
            lbl.resize(widths[i], 52)   # 52px: baseline + y_offset=22 не вылезает
            lbl.hide()
            self._letters.append(lbl)
            x += widths[i]

    # ─────────────────────────────────────────────────────
    # Phase 4: subtitle
    # ─────────────────────────────────────────────────────

    def _show_subtitle(self) -> None:
        from PySide6.QtWidgets import QLabel
        sub = QLabel("ВМедА им. С.М. Кирова", self)
        sub.setStyleSheet("""
            color: rgba(255,255,255,72);
            background: transparent;
            font-size: 9px;
            letter-spacing: 3px;
        """)
        sub.adjustSize()
        sub.move((self.W - sub.width()) // 2, 222)

        eff = QGraphicsOpacityEffect(sub)
        sub.setGraphicsEffect(eff)
        eff.setOpacity(0.0)
        sub.show()

        a = QPropertyAnimation(eff, b"opacity", sub)
        a.setDuration(self.T_SUBTITLE_FADE)
        a.setStartValue(0.0)
        a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.start()
        sub._anim = a   # type: ignore
        self._subtitle_widget = sub

    # ─────────────────────────────────────────────────────
    # Phase 5: прогресс-бар
    # ─────────────────────────────────────────────────────

    def _start_progress(self) -> None:
        self._pbar.show()
        a = QPropertyAnimation(self._pbar, b"value", self)
        a.setDuration(self.T_PROGRESS_DURATION)
        a.setStartValue(0)
        a.setEndValue(100)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.start()
        self._anim_progress = a   # держим ссылку

    # ─────────────────────────────────────────────────────
    # paintEvent — фон, иконка, декор
    # ─────────────────────────────────────────────────────

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        r  = self.rect()
        rr = 18   # border-radius

        # ── Фон: linear-gradient(162deg, #00122b → #001e45 → #001535)
        grad = QLinearGradient(0, 0, r.width() * 0.6, r.height())
        grad.setColorAt(0.0, QColor("#00122b"))
        grad.setColorAt(0.5, QColor("#001e45"))
        grad.setColorAt(1.0, QColor("#001535"))
        p.setBrush(grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(r, rr, rr)

        # ── Scanlines (воспроизводит CSS repeating-linear-gradient на фоне)
        p.setPen(QPen(QColor(255, 255, 255, 2), 1))
        for y in range(0, self.H, 4):
            p.drawLine(0, y, self.W, y)

        # ── Радиальный ореол за иконкой (CSS .sp-halo)
        halo = QRadialGradient(self.W / 2, self.H / 2 - 20, 150)
        halo.setColorAt(0.0, QColor(0, 115, 212, 44))
        halo.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(halo)
        p.drawEllipse(self.W // 2 - 150, self.H // 2 - 170, 300, 300)

        # ── Corner brackets (CSS .corner-tl/tr/bl/br, opacity:0.18)
        cp = QPen(QColor(77, 163, 232, 46), 1.5)
        p.setPen(cp)
        p.setBrush(Qt.BrushStyle.NoBrush)
        d, sz = 16, 18
        # top-left
        p.drawLine(d,          d,          d + sz,        d         )
        p.drawLine(d,          d,          d,             d + sz    )
        # top-right
        p.drawLine(self.W - d, d,          self.W - d - sz, d       )
        p.drawLine(self.W - d, d,          self.W - d,    d + sz    )
        # bottom-left
        p.drawLine(d,          self.H - d, d + sz,        self.H - d)
        p.drawLine(d,          self.H - d, d,             self.H - d - sz)
        # bottom-right
        p.drawLine(self.W - d, self.H - d, self.W - d - sz, self.H - d)
        p.drawLine(self.W - d, self.H - d, self.W - d,    self.H - d - sz)

        # ── Иконка: SVG pixmap с анимируемым scale и opacity
        if self._icon_pixmap and self._icon_opacity > 0.01:
            p.save()
            p.setOpacity(self._icon_opacity)
            # Центр иконки 72×72: cx=270, cy=124
            cx = (self.W - 72) // 2 + 36   # = 270
            cy = 88 + 36                    # = 124
            p.translate(cx, cy)
            p.scale(self._icon_scale, self._icon_scale)
            p.translate(-36, -36)
            p.drawPixmap(0, 0, self._icon_pixmap)
            p.restore()

        # ── Тонкая граница поверх всего (CSS border: 1px solid rgba(255,255,255,0.07))
        p.setPen(QPen(QColor(255, 255, 255, 18), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(QRectF(0.5, 0.5, self.W - 1, self.H - 1), rr, rr)


# ─────────────────────────────────────────────────────────────────────────────
# _LetterLabel — одна буква заголовка с анимацией translateY + opacity
# ─────────────────────────────────────────────────────────────────────────────

# Property вынесен на уровень модуля в начале файла (PySide6 требует это для QPropertyAnimation)


class _LetterLabel(QWidget):
    """
    Один символ заголовка 'EduCase'.
    Анимируется через QPropertyAnimation: y_offset (22→0) + letter_opacity (0→1).
    Воспроизводит CSS @keyframes letterUp из HTML-превью.
    """

    def __init__(self, char: str, font: QFont, color: QColor, parent: QWidget):
        super().__init__(parent)
        self._char    = char
        self._font    = font
        self._color   = color
        self._y_offset = 22.0   # начальный сдвиг вниз (px) — как translateY(18px) в CSS
        self._opacity  = 0.0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def appear(self) -> None:
        """Запускает анимацию появления (translateY + fade). Вызывается из QTimer."""
        self.show()

        # y_offset: 22 → 0 (translateY)
        self._anim_y = QPropertyAnimation(self, b"y_offset", self)
        self._anim_y.setDuration(380)
        self._anim_y.setStartValue(22.0)
        self._anim_y.setEndValue(0.0)
        self._anim_y.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_y.start()

        # letter_opacity: 0 → 1
        self._anim_o = QPropertyAnimation(self, b"letter_opacity", self)
        self._anim_o.setDuration(380)
        self._anim_o.setStartValue(0.0)
        self._anim_o.setEndValue(1.0)
        self._anim_o.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_o.start()

    # ── Qt Properties (имена должны совпадать с b"..." в QPropertyAnimation)

    def _get_y_offset(self) -> float:
        return self._y_offset
    def _set_y_offset(self, v: float):
        self._y_offset = v
        self.update()
    y_offset = _QtProp(float, _get_y_offset, _set_y_offset)   # → b"y_offset"

    def _get_opacity(self) -> float:
        return self._opacity
    def _set_opacity(self, v: float):
        self._opacity = v
        self.update()
    letter_opacity = _QtProp(float, _get_opacity, _set_opacity)  # → b"letter_opacity"

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        p.setOpacity(self._opacity)
        p.setFont(self._font)
        p.setPen(self._color)
        # +34: вертикальный baseline относительно верха виджета (52px высота)
        p.drawText(0, int(self._y_offset) + 34, self._char)
