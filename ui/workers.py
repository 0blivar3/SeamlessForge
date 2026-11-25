"""Background task runner to keep the Qt interface responsive."""
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

class WorkerSignals(QObject):
    finished = Signal(object, object)
    progress = Signal(str)

class FunctionWorker(QRunnable):
    def __init__(self, function, *args, **kwargs):
        super().__init__(); self.function=function; self.args=args; self.kwargs=kwargs
        self.signals=WorkerSignals()

    @Slot()
    def run(self):
        try: self.signals.finished.emit(self.function(*self.args, **self.kwargs), None)
        except Exception as exc: self.signals.finished.emit(None, exc)
