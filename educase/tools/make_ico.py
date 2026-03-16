"""
tools/make_ico.py
=================
Генерирует assets/icon.ico (256/128/64/32/16 px) из assets/icon_master.svg.

Запуск из корня проекта:
    python tools/make_ico.py

Dev-зависимости (только для этого скрипта):
    pip install cairosvg Pillow
    (уже включены в requirements-dev.txt)
"""
import io
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent   # корень проекта educase/


def make_ico() -> None:
    try:
        import cairosvg
        from PIL import Image
    except ImportError:
        print("Ошибка: установи зависимости:")
        print("  pip install cairosvg Pillow")
        sys.exit(1)

    src = ROOT / "assets" / "icon_master.svg"
    dst = ROOT / "assets" / "icon.ico"

    if not src.exists():
        print(f"Файл не найден: {src}")
        print("Убедись что assets/icon_master.svg присутствует в корне проекта.")
        sys.exit(1)

    sizes = [256, 128, 64, 32, 16]
    images = []

    print(f"Источник: {src}")
    for s in sizes:
        png_bytes = cairosvg.svg2png(
            url=str(src),
            output_width=s,
            output_height=s,
        )
        img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        images.append(img)
        print(f"  rendered {s}×{s}")

    images[0].save(
        dst,
        format="ICO",
        append_images=images[1:],
        sizes=[(s, s) for s in sizes],
    )
    size_kb = dst.stat().st_size // 1024
    print(f"\n✅ {dst} создан ({size_kb} KB, размеры: {sizes})")


if __name__ == "__main__":
    make_ico()
