# ui/components/image_picker.py
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PySide6.QtGui import QPixmap, QColor, QPainter, QPainterPath
from PySide6.QtCore import Qt, Signal

from ui.styles.theme import COLORS
from ui.styles.icons import get_icon

class ImagePicker(QWidget):
    """
    Виджет выбора изображения. Поддерживает Drag & Drop.
    Отображает превью выбранного изображения или область для загрузки.
    """
    image_selected = Signal(str) # Эмитит путь к файлу
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedSize(200, 200)
        
        self.file_path = None
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon
        self.icon_lbl = QLabel()
        self.icon_lbl.setStyleSheet("background: transparent;")
        self.icon_lbl.setPixmap(get_icon("image", COLORS["text_secondary"]).pixmap(48, 48))
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Text
        self.text_lbl = QLabel("Перетащите\nили кликните")
        self.text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_lbl.setStyleSheet(f"background: transparent; color: {COLORS['text_secondary']};")
        
        # Preview
        self.preview_lbl = QLabel()
        self.preview_lbl.setStyleSheet("background: transparent;")
        self.preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_lbl.hide()
        
        # Remove btn
        self.btn_remove = QPushButton("X")
        self.btn_remove.setFixedSize(24, 24)
        self.btn_remove.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['error_bg']};
                color: {COLORS['error']};
                border-radius: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['error']};
                color: white;
            }}
        """)
        self.btn_remove.clicked.connect(self.clear_image)
        self.btn_remove.hide()
        self.btn_remove.setParent(self)
        self.btn_remove.move(self.width() - 30, 6)
        
        self.layout.addWidget(self.icon_lbl)
        self.layout.addWidget(self.text_lbl)
        self.layout.addWidget(self.preview_lbl)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        rect = self.rect().adjusted(1, 1, -1, -1)
        path.addRoundedRect(rect, 8, 8)
        
        # Draw dashed border
        p.setPen(Qt.PenStyle.DashLine)
        
        if self.file_path:
            p.setPen(QColor(0, 0, 0, 20)) # stroke_card
            p.fillPath(path, QColor(COLORS["bg_elevated"]))
        else:
            p.setPen(QColor(COLORS["accent"]))
            p.fillPath(path, QColor(COLORS["info_bg"]))
            
        p.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.file_path:
            self._open_file_dialog()

    def _open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Выбрать изображение", "",
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_name:
            self.set_image(file_name)

    def set_image(self, path: str):
        if os.path.exists(path):
            self.file_path = path
            pixmap = QPixmap(path)
            
            # Scale to fit
            scaled = pixmap.scaled(
                self.width() - 8, self.height() - 8, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_lbl.setPixmap(scaled)
            
            self.icon_lbl.hide()
            self.text_lbl.hide()
            self.preview_lbl.show()
            self.btn_remove.show()
            
            self.image_selected.emit(path)
            self.update()

    def clear_image(self):
        self.file_path = None
        self.preview_lbl.clear()
        
        self.preview_lbl.hide()
        self.btn_remove.hide()
        self.icon_lbl.show()
        self.text_lbl.show()
        
        self.image_selected.emit("")
        self.update()
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].isLocalFile():
                ext = urls[0].toLocalFile().lower().split('.')[-1]
                if ext in ['png', 'jpg', 'jpeg', 'webp']:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            self.set_image(urls[0].toLocalFile())
