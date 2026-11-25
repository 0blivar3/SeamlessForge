"""Portable software-rendered 3D material preview (no OpenGL dependency)."""
import math

import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter, QPen
from PySide6.QtWidgets import QWidget


class Texture3DPreview(QWidget):
    """Interactive textured sphere rendered on the CPU for driver-independent preview."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(240, 240)
        self.setMouseTracking(True)
        self._image = None
        self._frame = None
        self._last_pos = None
        self.rotation_x = -12.0
        self.rotation_y = 25.0
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)

    def set_image(self, image):
        arr = np.asarray(image)
        if arr.ndim == 2:
            arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
        elif arr.shape[2] == 4:
            rgb = arr[..., :3].astype(np.float32)
            alpha = arr[..., 3:4].astype(np.float32) / 255.0
            arr = np.clip(rgb * alpha + 24 * (1 - alpha), 0, 255).astype(np.uint8)
        else:
            arr = arr[..., :3]
        self._image = np.ascontiguousarray(arr, dtype=np.uint8)
        self._render()
        self.update()

    def _render(self):
        if self._image is None:
            self._frame = None
            return
        side = max(180, min(720, min(self.width(), self.height())))
        side = max(180, side - 24)
        yy, xx = np.mgrid[-1:1:complex(side), -1:1:complex(side)]
        radius2 = xx * xx + yy * yy
        visible = radius2 <= 0.96
        z = np.sqrt(np.maximum(0.0, 0.96 - radius2))
        nx, ny, nz = xx.copy(), -yy.copy(), z

        rx, ry = math.radians(self.rotation_x), math.radians(self.rotation_y)
        # Rotate the sphere coordinates to simulate orbiting the material.
        x1 = nx * math.cos(ry) + nz * math.sin(ry)
        z1 = -nx * math.sin(ry) + nz * math.cos(ry)
        y2 = ny * math.cos(rx) - z1 * math.sin(rx)
        z2 = ny * math.sin(rx) + z1 * math.cos(rx)
        x2 = x1

        u = (np.arctan2(z2, x2) / (2 * np.pi) + 0.5) % 1.0
        v = np.arccos(np.clip(y2, -1, 1)) / np.pi
        h, w = self._image.shape[:2]
        map_x = (u * (w - 1)).astype(np.float32)
        map_y = (v * (h - 1)).astype(np.float32)
        sampled = cv2.remap(
            self._image, map_x, map_y, cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_WRAP,
        ).astype(np.float32)

        # Soft studio lighting and a subtle rim highlight.
        length = np.sqrt(x2*x2 + y2*y2 + z2*z2) + 1e-6
        nx2, ny2, nz2 = x2/length, y2/length, z2/length
        light = np.array([-0.45, 0.62, 0.78], dtype=np.float32)
        diffuse = np.maximum(0, nx2*light[0] + ny2*light[1] + nz2*light[2])
        rim = np.power(np.maximum(0, 1 - nz2), 2) * 0.10
        shade = 0.24 + 0.76 * diffuse + rim
        rendered = np.clip(sampled * shade[..., None], 0, 255).astype(np.uint8)
        canvas = np.full((side, side, 3), (20, 25, 34), dtype=np.uint8)
        canvas[visible] = rendered[visible]
        self._frame = QImage(
            np.ascontiguousarray(canvas).data, side, side, side * 3,
            QImage.Format_RGB888,
        ).copy()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)
        if self._frame is None:
            painter.setPen(QPen(Qt.lightGray))
            painter.drawText(self.rect(), Qt.AlignCenter, "Load a texture to preview")
        else:
            side = min(self.width(), self.height(), self._frame.width())
            target = self.rect().adjusted(
                (self.width()-side)//2, (self.height()-side)//2,
                -(self.width()-side)//2, -(self.height()-side)//2,
            )
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.drawImage(target, self._frame)
        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._render()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._last_pos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self._last_pos is not None and event.buttons() & Qt.LeftButton:
            pos = event.position().toPoint()
            delta = pos - self._last_pos
            self.rotation_x = max(-85, min(85, self.rotation_x + delta.y() * 0.7))
            self.rotation_y += delta.x() * 0.7
            self._last_pos = pos
            self._render()
            self.update()

    def mouseReleaseEvent(self, event):
        self._last_pos = None

    def wheelEvent(self, event):
        self.rotation_y += event.angleDelta().y() / 18
        self._render()
        self.update()
