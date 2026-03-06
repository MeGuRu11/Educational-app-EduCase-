# core/thread_pool.py
"""
Threading-модель для фоновых задач.
Worker (QRunnable) + run_async() — запуск в отдельном потоке.
Сигналы result/error/progress доставляют результат в main-поток.
ПРАВИЛО: НИКОГДА не обращаться к GUI-виджетам из worker-потоков.
"""
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


class _Signals(QObject):
    """Сигналы Worker'а — thread-safe доставка из потока в main-thread."""

    result = Signal(object)
    error = Signal(str)
    progress = Signal(int)


class Worker(QRunnable):
    """Фоновая задача. Создаётся через run_async()."""

    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = _Signals()
        self.setAutoDelete(True)

    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))


# Отдельный пул (не globalInstance): не конфликтует с внутренними задачами Qt
_pool = QThreadPool()
_pool.setMaxThreadCount(4)


def run_async(
    fn: Callable[..., Any],
    *args: Any,
    on_result: Callable[[Any], None] | None = None,
    on_error: Callable[[str], None] | None = None,
    on_progress: Callable[[int], None] | None = None,
    **kwargs: Any,
) -> Worker:
    """
    Запускает fn в фоновом потоке.

    Пример:
        run_async(heavy_db_query, case_id=5, on_result=update_ui, on_error=show_toast)

    Для progress: fn должна принимать progress_cb и вызывать его явно:
        def my_task(progress_cb=None):
            ...
            if progress_cb: progress_cb(50)
        run_async(my_task, progress_cb=w.signals.progress.emit, on_progress=update_ui)
    """
    w = Worker(fn, *args, **kwargs)
    if on_result:
        w.signals.result.connect(on_result)
    if on_error:
        w.signals.error.connect(on_error)
    if on_progress:
        w.signals.progress.connect(on_progress)
    _pool.start(w)
    return w
