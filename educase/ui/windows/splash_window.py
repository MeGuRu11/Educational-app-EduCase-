# ui/windows/splash_window.py
"""
Загрузочный экран EduCase.
Показывается до LoginWindow, пока выполняются run_migrations() и build_container().
Гарантированное время показа: минимум 2500ms.

Полная продакшн-реализация из §16 PROJECT_DESIGN_v2.md:
- Phase 1: окно fade-in (300ms)
- Phase 2: иконка scale(0.42→1.0) OutBack «пружина» (650ms)
- Phase 3: буквы «EduCase» stagger по одной (50ms/letter)
- Phase 4: subtitle fade-in (400ms)
- Phase 5: прогресс-бар fill (2300ms)
- Phase 7: finish() → fade-out → показ LoginWindow
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    QTimer,
    Property as QtProperty,
    Qt,
)
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
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QLabel,
    QProgressBar,
    QWidget,
)

BASE_DIR = Path(__file__).parent.parent.parent  # educase/


class SplashScreen(QWidget):
    """
    Анимированный splash-экран.

    Использование:
        splash = SplashScreen()
        splash.start()
        app.processEvents()
        # ... тяжёлые операции ...
        splash.finish(login_window)
    """

    # ── тайминги (ms) — соответствуют CSS из educase_brand_preview.html
    T_WINDOW_FADE_IN = 300  # Phase 1
    T_ICON_START = 200  # Phase 2: задержка до начала анимации иконки
    T_ICON_DURATION = 650  # Phase 2: длительность «пружины»
    T_TITLE_START = 700  # Phase 3: первая буква
    T_LETTER_STAGGER = 50  # Phase 3: задержка между буквами
    T_SUBTITLE_START = 1160  # Phase 4
    T_SUBTITLE_FADE = 400  # Phase 4
    T_PROGRESS_START = 1400  # Phase 5
    T_PROGRESS_DURATION = 2300  # Phase 5
    T_FINISH_FADE = 400  # Phase 7

    W, H = 540, 330  # размер окна

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.W, self.H)
        self._center()

        # Состояние иконки (анимируется через paintEvent)
        self._icon_scale: float = 0.42
        self._icon_opacity: float = 0.0
        self._icon_step: int = 0
        self._icon_total_steps: int = 22
        self._icon_pixmap = self._load_icon_pixmap()

        # Opacity effect на весь виджет
        self._eff = QGraphicsOpacityEffect(self)
        self._eff.setOpacity(0.0)
        self.setGraphicsEffect(self._eff)

        # Subtitle opacity (рисуется в paintEvent, НЕ QLabel — избегаем конфликт вложенных effect)
        self._subtitle_opacity: float = 0.0
        self._subtitle_visible: bool = False

        # Буквы заголовка
        self._letters: list[_LetterLabel] = []

        # Прогресс-бар
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

        # Ссылки на анимации (prevent GC)
        self._anim_window: QPropertyAnimation | None = None
        self._anim_finish: QPropertyAnimation | None = None
        self._anim_progress: QPropertyAnimation | None = None
        self._icon_timer: QTimer | None = None
        self._anim_subtitle: QPropertyAnimation | None = None

    # ─────────────────────────────────────────
    def _center(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.geometry()
            self.move(
                (geo.width() - self.W) // 2,
                (geo.height() - self.H) // 2,
            )

    def _load_icon_pixmap(self) -> QPixmap | None:
        """Загружает icon_master.svg и рендерит в QPixmap 72×72."""
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

    # ─────────────────────────────────────────
    def start(self) -> None:
        """Показывает окно и запускает все анимации. Вызывать вместо show()."""
        self.show()

        # Phase 1: окно fade-in
        self._anim_window = QPropertyAnimation(self._eff, b"opacity", self)
        self._anim_window.setDuration(self.T_WINDOW_FADE_IN)
        self._anim_window.setStartValue(0.0)
        self._anim_window.setEndValue(1.0)
        self._anim_window.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_window.start()

        # Phase 2: иконка (OutBack через ручной таймер)
        QTimer.singleShot(self.T_ICON_START, self._start_icon_anim)

        # Phase 3: буквы «EduCase» по одной
        self._build_letters()
        for i, letter in enumerate(self._letters):
            delay = self.T_TITLE_START + i * self.T_LETTER_STAGGER
            QTimer.singleShot(delay, letter.appear)

        # Phase 4: subtitle
        QTimer.singleShot(self.T_SUBTITLE_START, self._show_subtitle)

        # Phase 5: прогресс-бар
        QTimer.singleShot(self.T_PROGRESS_START, self._start_progress)

    def finish(self, login_window: QWidget) -> None:
        """Phase 7: fade out, затем показываем login."""
        anim = QPropertyAnimation(self._eff, b"opacity", self)
        anim.setDuration(self.T_FINISH_FADE)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.finished.connect(lambda: self._on_finish(login_window))
        anim.start()
        self._anim_finish = anim

    def _on_finish(self, login_window: QWidget) -> None:
        self.close()
        login_window.show()
        # Fade-in LoginWindow
        eff = QGraphicsOpacityEffect(login_window)
        login_window.setGraphicsEffect(eff)
        eff.setOpacity(0.0)
        a = QPropertyAnimation(eff, b"opacity", login_window)
        a.setDuration(300)
        a.setStartValue(0.0)
        a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.start()
        login_window.setProperty("_splash_fade", a)

    # ─────────────────────────────────────────
    def _start_icon_anim(self) -> None:
        interval_ms = self.T_ICON_DURATION // self._icon_total_steps
        t = QTimer(self)
        t.setInterval(interval_ms)
        t.timeout.connect(self._tick_icon)
        t.start()
        self._icon_timer = t

    def _tick_icon(self) -> None:
        self._icon_step += 1
        t = min(1.0, self._icon_step / self._icon_total_steps)
        # OutBack easing
        c1, c3 = 1.70158, 2.70158
        ease = 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
        self._icon_scale = max(0.0, 0.42 + 0.58 * ease)
        self._icon_opacity = min(1.0, t * 1.8)
        self.update()
        if self._icon_step >= self._icon_total_steps:
            if self._icon_timer:
                self._icon_timer.stop()
            self._icon_scale, self._icon_opacity = 1.0, 1.0
            self.update()

    # ─────────────────────────────────────────
    def _build_letters(self) -> None:
        """Создаёт QWidget-метки для каждой буквы 'EduCase'."""
        text = "EduCase"
        bold_chars = "Edu"
        font_b = QFont("Segoe UI Variable", 26, QFont.Weight.DemiBold)
        font_n = QFont("Segoe UI Variable", 26, QFont.Weight.Light)

        total_w = 0
        widths: list[int] = []
        for ch in text:
            f = font_b if ch in bold_chars else font_n
            w = QFontMetrics(f).horizontalAdvance(ch) + 1
            widths.append(w)
            total_w += w

        x = (self.W - total_w) // 2
        y = 172

        for i, ch in enumerate(text):
            f = font_b if ch in bold_chars else font_n
            col = QColor("#4DA3E8") if ch in bold_chars else QColor(255, 255, 255, 220)
            lbl = _LetterLabel(ch, f, col, self)
            lbl.move(x, y)
            lbl.resize(widths[i], 52)
            lbl.hide()
            self._letters.append(lbl)
            x += widths[i]

    def _show_subtitle(self) -> None:
        self._subtitle_visible = True
        a = QPropertyAnimation(self, b"subtitle_opacity", self)
        a.setDuration(self.T_SUBTITLE_FADE)
        a.setStartValue(0.0)
        a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.start()
        self._anim_subtitle = a

    # Qt Property for subtitle animation
    def _get_subtitle_opacity(self) -> float:
        return self._subtitle_opacity

    def _set_subtitle_opacity(self, v: float) -> None:
        self._subtitle_opacity = v
        self.update()

    subtitle_opacity = QtProperty(float, _get_subtitle_opacity, _set_subtitle_opacity)

    def _start_progress(self) -> None:
        self._pbar.show()
        a = QPropertyAnimation(self._pbar, b"value", self)
        a.setDuration(self.T_PROGRESS_DURATION)
        a.setStartValue(0)
        a.setEndValue(100)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.start()
        self._anim_progress = a

    # ─────────────────────────────────────────
    def paintEvent(self, _event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        r = self.rect()
        rr = 18  # corner radius

        # ── Фон: тёмно-синий градиент
        grad = QLinearGradient(0, 0, r.width() * 0.6, r.height())
        grad.setColorAt(0.0, QColor("#00122b"))
        grad.setColorAt(0.5, QColor("#001e45"))
        grad.setColorAt(1.0, QColor("#001535"))
        p.setBrush(grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(r, rr, rr)

        # ── Scanlines (лёгкая текстура)
        p.setPen(QPen(QColor(255, 255, 255, 2), 1))
        for y in range(0, self.H, 4):
            p.drawLine(0, y, self.W, y)

        # ── Радиальный ореол за иконкой
        halo = QRadialGradient(self.W / 2, self.H / 2 - 20, 150)
        halo.setColorAt(0.0, QColor(0, 115, 212, 46))
        halo.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(halo)
        p.drawEllipse(self.W // 2 - 150, self.H // 2 - 170, 300, 300)

        # ── Corner brackets (декоративные уголки)
        cp = QPen(QColor(77, 163, 232, 46), 1.5)
        p.setPen(cp)
        p.setBrush(Qt.BrushStyle.NoBrush)
        d, sz = 16, 18
        # TL
        p.drawLine(d, d, d + sz, d)
        p.drawLine(d, d, d, d + sz)
        # TR
        p.drawLine(self.W - d, d, self.W - d - sz, d)
        p.drawLine(self.W - d, d, self.W - d, d + sz)
        # BL
        p.drawLine(d, self.H - d, d + sz, self.H - d)
        p.drawLine(d, self.H - d, d, self.H - d - sz)
        # BR
        p.drawLine(self.W - d, self.H - d, self.W - d - sz, self.H - d)
        p.drawLine(self.W - d, self.H - d, self.W - d, self.H - d - sz)

        # ── Иконка (SVG pixmap с анимируемым scale и opacity)
        if self._icon_pixmap and self._icon_opacity > 0.01:
            p.save()
            p.setOpacity(self._icon_opacity)
            cx = (self.W - 72) // 2 + 36
            cy = 88 + 36
            p.translate(cx, cy)
            p.scale(self._icon_scale, self._icon_scale)
            p.translate(-36, -36)
            p.drawPixmap(0, 0, self._icon_pixmap)
            p.restore()

        # ── Субтитл (рисуется в paintEvent — без вложенного QGraphicsOpacityEffect)
        if self._subtitle_visible and self._subtitle_opacity > 0.01:
            p.save()
            p.setOpacity(self._subtitle_opacity)
            sub_font = QFont("Segoe UI Variable", 9)
            sub_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 3.0)
            p.setFont(sub_font)
            p.setPen(QColor(255, 255, 255, 160))
            text_sub = "ВМедА им. С.М. Кирова"
            tw = QFontMetrics(sub_font).horizontalAdvance(text_sub)
            p.drawText((self.W - tw) // 2, 238, text_sub)
            p.restore()

        # ── Рамка (тонкая, поверх всего)
        p.setPen(QPen(QColor(255, 255, 255, 18), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(0, 0, self.W - 1, self.H - 1, rr, rr)


class _LetterLabel(QWidget):
    """Одна буква заголовка с анимацией появления снизу."""

    def __init__(self, char: str, font: QFont, color: QColor, parent: QWidget) -> None:
        super().__init__(parent)
        self._char = char
        self._font = font
        self._color = color
        self._y_offset: float = 22.0
        self._opacity: float = 0.0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Ссылки на анимации
        self._anim_y: QPropertyAnimation | None = None
        self._anim_o: QPropertyAnimation | None = None

    def appear(self) -> None:
        self.show()
        self._anim_y = QPropertyAnimation(self, b"y_offset", self)
        self._anim_y.setDuration(380)
        self._anim_y.setStartValue(22.0)
        self._anim_y.setEndValue(0.0)
        self._anim_y.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_y.start()

        self._anim_o = QPropertyAnimation(self, b"letter_opacity", self)
        self._anim_o.setDuration(380)
        self._anim_o.setStartValue(0.0)
        self._anim_o.setEndValue(1.0)
        self._anim_o.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_o.start()

    # Qt Properties for QPropertyAnimation
    def _get_y_offset(self) -> float:
        return self._y_offset

    def _set_y_offset(self, v: float) -> None:
        self._y_offset = v
        self.update()

    y_offset = QtProperty(float, _get_y_offset, _set_y_offset)

    def _get_opacity(self) -> float:
        return self._opacity

    def _set_opacity(self, v: float) -> None:
        self._opacity = v
        self.update()

    letter_opacity = QtProperty(float, _get_opacity, _set_opacity)

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        p.setOpacity(self._opacity)
        p.setFont(self._font)
        p.setPen(self._color)
        p.drawText(0, int(self._y_offset) + 34, self._char)
