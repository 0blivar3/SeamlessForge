"""Qt image preview helpers."""
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap, QPainter
from PySide6.QtWidgets import QLabel, QScrollArea, QWidget, QVBoxLayout, QSizePolicy


def to_qimage(array: np.ndarray) -> QImage:
    arr = np.ascontiguousarray(array)
    if arr.ndim == 2:
        return QImage(
            arr.data, arr.shape[1], arr.shape[0], arr.strides[0],
            QImage.Format_Grayscale8
        ).copy()
    if arr.shape[2] == 4:
        return QImage(
            arr.data, arr.shape[1], arr.shape[0], arr.strides[0],
            QImage.Format_RGBA8888
        ).copy()
    rgb = np.ascontiguousarray(arr[..., :3])
    return QImage(
        rgb.data, rgb.shape[1], rgb.shape[0], rgb.strides[0],
        QImage.Format_RGB888
    ).copy()


class ImagePreview(QWidget):
    def __init__(self, title="Preview", parent=None):
        super().__init__(parent)
        self.setMinimumSize(0, 0)
        self.title = QLabel(title)
        self.title.setStyleSheet("font-weight:600;color:#dce4f2;padding:4px;")
        self.label = QLabel("Open an image to begin")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(1, 1)
        self.label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.label.setStyleSheet(
            "background:#171b24;border:1px solid #303746;border-radius:8px;color:#8792a5;"
        )
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.label)
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumSize(0, 0)
        self.scroll.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.title)
        layout.addWidget(self.scroll)
        self._pixmap = None

    def set_image(self, array, repeat=1):
        pix = QPixmap.fromImage(to_qimage(array))
        if repeat > 1:
            tiled = QPixmap(pix.width() * repeat, pix.height() * repeat)
            tiled.fill(Qt.transparent)
            painter = QPainter(tiled)
            for y in range(repeat):
                for x in range(repeat):
                    painter.drawPixmap(x * pix.width(), y * pix.height(), pix)
            painter.end()
            pix = tiled
        self._pixmap = pix
        self._fit()

    def clear(self, message="Open an image to begin"):
        self._pixmap = None
        self.label.setPixmap(QPixmap())
        self.label.setText(message)
        self.label.resize(self.scroll.viewport().size())

    def _fit(self):
        if self._pixmap is None:
            return
        target = self.scroll.viewport().size()
        if target.width() < 2 or target.height() < 2:
            return
        scaled = self._pixmap.scaled(
            target, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.label.setText("")
        self.label.setPixmap(scaled)
        self.label.resize(target)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit()
