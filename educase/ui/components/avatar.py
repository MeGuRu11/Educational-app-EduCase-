# ui/components/avatar.py
from typing import Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPainterPath, QColor, QFont, QPixmap
from PySide6.QtCore import Qt, QRectF

from ui.styles.theme import COLORS

class Avatar(QWidget):
    """
    Круглый аватар. Если изображения нет, генерирует кружок с инициалами.
    """
    def __init__(self, size: int = 40, name: str = "", pixmap: Optional[QPixmap] = None, parent=None):
        super().__init__(parent)
        self._size = size
        self.name = name
        self.pixmap = pixmap
        
        self.setFixedSize(size, size)

    def _get_initials(self) -> str:
        if not self.name:
            return "?"
        parts = self.name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        return self.name[:2].upper()

    def _get_color_for_name(self) -> QColor:
        # Generate a consistent color based on the name string
        if not self.name:
            return QColor(COLORS["bg_layer"])
            
        colors = [
            COLORS["accent"], COLORS["success"], 
            COLORS["warning"], COLORS["error"], 
            "#8b5cf6", "#ec4899", "#14b8a6"
        ]
        index = sum(ord(c) for c in self.name) % len(colors)
        return QColor(colors[index])

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        rect = QRectF(0, 0, self._size, self._size)
        path = QPainterPath()
        path.addEllipse(rect)
        p.setClipPath(path)
        
        if self.pixmap and not self.pixmap.isNull():
            # Рисуем загруженную картинку
            scaled_pixmap = self.pixmap.scaled(
                self._size, self._size, 
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            # Высчитываем отступ для центрирования
            x = (self._size - scaled_pixmap.width()) / 2
            y = (self._size - scaled_pixmap.height()) / 2
            p.drawPixmap(x, y, scaled_pixmap)
        else:
            # Рисуем кружок с инициалами
            bg_color = self._get_color_for_name()
            p.fillPath(path, bg_color)
            
            p.setPen(QColor("#ffffff")) # White text for better contrast
            # calculate font size based on widget size
            font = QFont("Segoe UI Variable", max(8, self._size // 2.5))
            font.setBold(True)
            p.setFont(font)
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._get_initials())
