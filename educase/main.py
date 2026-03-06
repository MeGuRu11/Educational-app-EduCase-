# main.py
"""
Точка входа приложения EduCase.
Последовательность запуска:
1. QApplication → шрифты → SplashScreen
2. run_migrations() + build_container()
3. Гарантированный показ splash ≥ 2500ms
4. splash.finish() → LoginWindow
"""
import sys
import time

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication

from config import _init_dirs
from core.database import run_migrations
from core.db_maintenance import run_maintenance
from core.di_container import build_container
from core.logger import setup_logger
from core.thread_pool import run_async
from ui.styles.stylesheet import generate_stylesheet
from ui.windows.splash_window import SplashScreen
import app


def main() -> None:
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("EduCase")
    qt_app.setApplicationVersion("1.0.0")

    # Иконка приложения (таскбар + Alt+Tab)
    qt_app.setWindowIcon(QIcon("assets/icon.ico"))

    # Imports moved here because QWidgets require QApplication to exist first
    from ui.components.toast import ToastManager
    from ui.windows.login_window import LoginWindow
    from ui.windows.main_window import MainWindow

    # 0. Директории данных
    _init_dirs()

    # Логирование
    setup_logger()

    # 1. Шрифты
    QFontDatabase.addApplicationFont("assets/fonts/SegoeUIVariable.ttf")

    # Глобальный стиль
    qt_app.setStyleSheet(generate_stylesheet())

    # 2. Splash — показываем НЕМЕДЛЕННО
    splash = SplashScreen()
    splash.start()
    t0 = time.monotonic()
    qt_app.processEvents()

    # 3. Миграции (sync, обычно < 200ms)
    try:
        run_migrations()
    except Exception:
        pass  # Первый запуск без alembic.ini — OK, БД будет создана позже
    qt_app.processEvents()

    # 4. DI-контейнер
    container = build_container()
    app.container = container
    qt_app.processEvents()

    # 5. Фоновое обслуживание — после старта
    QTimer.singleShot(3000, lambda: run_async(run_maintenance))

    # 6. Global Managers
    toast_manager = ToastManager(main_window=None)

    # 7. Инициализация окон
    login_window = LoginWindow(container)
    main_window = MainWindow(container)
    
    toast_manager.main_window = login_window

    def _on_login_success() -> None:
        login_window.hide()
        toast_manager.main_window = main_window
        main_window.show()

    login_window.login_successful.connect(_on_login_success)

    # 8. Гарантируем минимум 2500ms показа splash
    elapsed = int((time.monotonic() - t0) * 1000)
    delay = max(0, 2500 - elapsed)
    QTimer.singleShot(delay, lambda: splash.finish(login_window))

    sys.exit(qt_app.exec())


if __name__ == "__main__":
    from PySide6.QtCore import Qt

    main()
