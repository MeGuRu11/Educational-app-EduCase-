# tools/make_ico.py
"""
Генерирует assets/icon.ico (256/128/64/32/16 px) из assets/icon_master.svg.
Использует PySide6 (QSvgRenderer) + Pillow — без cairosvg.
Запуск: python tools/make_ico.py
"""
import io
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent  # корень проекта educase/


def make_ico() -> None:
    # PySide6 требует QApplication даже для оффскрин-рендера
    from PySide6.QtCore import QRectF, Qt
    from PySide6.QtGui import QGuiApplication, QImage, QPainter
    from PySide6.QtSvg import QSvgRenderer

    app = QGuiApplication.instance() or QGuiApplication(sys.argv)

    src = ROOT / "assets" / "icon_master.svg"
    dst = ROOT / "assets" / "icon.ico"

    if not src.exists():
        print(f"Файл не найден: {src}")
        sys.exit(1)

    renderer = QSvgRenderer(str(src))
    if not renderer.isValid():
        print(f"Невалидный SVG: {src}")
        sys.exit(1)

    try:
        from PIL import Image
    except ImportError:
        print("Установи Pillow: pip install Pillow")
        sys.exit(1)

    sizes = [256, 128, 64, 32, 16]
    images = []
    for s in sizes:
        qimg = QImage(s, s, QImage.Format.Format_ARGB32_Premultiplied)
        qimg.fill(Qt.GlobalColor.transparent)
        painter = QPainter(qimg)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        renderer.render(painter, QRectF(0, 0, s, s))
        painter.end()

        # QImage → bytes → PIL Image
        raw = qimg.bits()
        buf = bytes(raw) if raw is not None else b""
        pil_img = Image.frombytes("RGBA", (s, s), buf, "raw", "BGRA")
        images.append(pil_img)
        print(f"  rendered {s}x{s}")

    images[0].save(
        dst,
        format="ICO",
        append_images=images[1:],
        sizes=[(s, s) for s in sizes],
    )
    print(f"✅ {dst} создан ({dst.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    make_ico()
