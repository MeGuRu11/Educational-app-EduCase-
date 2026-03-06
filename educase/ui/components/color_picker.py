# ui/components/color_picker.py
from PySide6.QtWidgets import QColorDialog

def open_color_picker(parent=None, initial_color="#0078D4"):
    """
    Открывает стандартный диалог выбора цвета.
    Здесь можно сделать полностью кастомный QDialog (или взять QColorDialog), 
    но для простоты обернем стандартный.
    """
    dialog = QColorDialog(parent)
    dialog.setStyleSheet("background-color: white;")
    color = dialog.getColor(initial=initial_color, parent=parent, title="Выберите цвет")
    if color.isValid():
        return color.name()
    return None
