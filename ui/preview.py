"""Qt image preview helpers."""
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QScrollArea, QWidget, QVBoxLayout

def to_qimage(array: np.ndarray) -> QImage:
    arr = np.ascontiguousarray(array)
    if arr.ndim == 2:
        return QImage(arr.data, arr.shape[1], arr.shape[0], arr.strides[0], QImage.Format_Grayscale8).copy()
    if arr.shape[2] == 4:
        return QImage(arr.data, arr.shape[1], arr.shape[0], arr.strides[0], QImage.Format_RGBA8888).copy()
    rgb = np.ascontiguousarray(arr[..., :3])
    return QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.strides[0], QImage.Format_RGB888).copy()

class ImagePreview(QWidget):
    def __init__(self, title="Preview", parent=None):
        super().__init__(parent)
        self.label = QLabel("Open an image to begin")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(240, 180)
        self.label.setStyleSheet("background:#171b24;border:1px solid #303746;border-radius:8px;color:#8792a5;")
        self.title = QLabel(title)
        self.title.setStyleSheet("font-weight:600;color:#dce4f2;padding:4px;")
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.label)
        self.scroll.setWidgetResizable(True)
        layout = QVBoxLayout(self); layout.addWidget(self.title); layout.addWidget(self.scroll)
        self._pixmap = None

    def set_image(self, array, repeat=1):
        qimg = to_qimage(array)
        pix = QPixmap.fromImage(qimg)
        if repeat > 1:
            tiled = QPixmap(pix.width()*repeat, pix.height()*repeat)
            tiled.fill(Qt.transparent)
            from PySide6.QtGui import QPainter
            painter = QPainter(tiled)
            for y in range(repeat):
                for x in range(repeat):
                    painter.drawPixmap(x*pix.width(), y*pix.height(), pix)
            painter.end()
            pix = tiled
        self._pixmap = pix
        self._fit()

    def _fit(self):
        if self._pixmap:
            target = self.scroll.viewport().size()
            self.label.setPixmap(self._pixmap.scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.label.resize(self.label.pixmap().size())
