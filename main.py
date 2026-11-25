"""SeamlessForge application entry point."""
import sys

from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    # Set the default before QApplication creates any native OpenGL contexts.
    # This keeps QOpenGLWidget and PyOpenGL on the same 3.3 core-profile context.
    surface_format = QSurfaceFormat()
    surface_format.setRenderableType(QSurfaceFormat.OpenGL)
    surface_format.setVersion(3, 3)
    surface_format.setProfile(QSurfaceFormat.CoreProfile)
    surface_format.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(surface_format)

    app = QApplication(sys.argv)
    app.setApplicationName("SeamlessForge")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
