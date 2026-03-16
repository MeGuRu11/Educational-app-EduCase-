# run_constructor.py
"""
Standalone entry point for Task Constructor.
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QIcon

import app
from config import _init_dirs
from core.database import run_migrations
from core.di_container import build_container
from core.logger import setup_logger
from ui.styles.stylesheet import generate_stylesheet
from ui.task_constructor.constructor_dialog import ConstructorDialog

def main():
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("EduCase Constructor")
    
    # 0. Dirs
    _init_dirs()
    setup_logger()
    
    # 1. Fonts & Styles
    QFontDatabase.addApplicationFont("assets/fonts/SegoeUIVariable.ttf")
    qt_app.setStyleSheet(generate_stylesheet())
    
    # 2. DI
    try:
        run_migrations()
    except:
        pass
    container = build_container()
    app.container = container
    
    # 3. Dialog
    dialog = ConstructorDialog()
    dialog.show()
    
    sys.exit(qt_app.exec())

if __name__ == "__main__":
    main()
