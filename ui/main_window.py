"""Main SeamlessForge desktop interface."""
from pathlib import Path

from PySide6.QtCore import QThreadPool, Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QComboBox, QSpinBox, QGroupBox, QGridLayout,
    QMessageBox, QStatusBar, QDialog, QScrollArea, QSplitter,
    QSizePolicy,
)

from core.image_io import load_image, save_image
from core.processor import process_image
from core.quality import analyze_edges
from core.batch import process_folder
from core.history import ImageHistory
from .preview import ImagePreview
from .preview_3d import Texture3DPreview
from .workers import FunctionWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SeamlessForge")
        self.resize(1360, 860)
        self.setMinimumSize(760, 520)
        self.original = None
        self.result = None
        self.path = None
        self.pool = QThreadPool.globalInstance()
        self.history = ImageHistory()
        self._workers = set()
        self.preview_dialog = None
        self.setAcceptDrops(True)
        self._build_ui()
        self.setStyleSheet("""
            QMainWindow,QWidget { background:#10141c;color:#e7edf7;font-family:'Segoe UI';font-size:10pt; }
            QPushButton { background:#273449;border:1px solid #3a4a62;border-radius:6px;padding:9px 14px; }
            QPushButton:hover { background:#344762; }
            QPushButton:disabled { color:#687386;background:#1a202b; }
            QComboBox,QSpinBox { background:#1b2330;border:1px solid #39465a;border-radius:5px;padding:6px; }
            QGroupBox { border:1px solid #303b4d;border-radius:8px;margin-top:12px;padding:12px;font-weight:600; }
            QGroupBox::title { subcontrol-origin:margin;left:10px;padding:0 5px; }
            QSplitter::handle { background:#273449; }
            QSplitter::handle:hover { background:#526b8d; }
        """)

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(8)

        # Keep the controls in a scrollable column so smaller windows and
        # maximized displays with unusual aspect ratios never clip controls.
        side_content = QWidget()
        side_content.setMinimumWidth(250)
        side_content.setMaximumWidth(340)
        side = QVBoxLayout(side_content)
        side.setContentsMargins(4, 4, 4, 4)
        side.setSpacing(10)

        brand = QLabel("SEAMLESSFORGE")
        brand.setStyleSheet("font-size:20px;font-weight:800;color:#8ab4ff;padding:8px;")
        side.addWidget(brand)

        self.open_btn = QPushButton("Open texture")
        self.open_btn.clicked.connect(self.open_dialog)
        side.addWidget(self.open_btn)

        box = QGroupBox("Processing")
        form = QVBoxLayout(box)
        self.algorithm = QComboBox()
        self.algorithm.addItems(["Offset Blending", "Poisson Blending", "Mirror Tiling", "Edge Feather", "FFT Seamless", "Directional Match"])
        form.addWidget(QLabel("Algorithm"))
        form.addWidget(self.algorithm)
        form.addWidget(QLabel("Preview repetitions"))
        self.repeat = QSpinBox()
        self.repeat.setRange(1, 10)
        self.repeat.setValue(3)
        form.addWidget(self.repeat)
        self.process_btn = QPushButton("Process texture")
        self.process_btn.clicked.connect(self.process)
        form.addWidget(self.process_btn)
        self.save_btn = QPushButton("Export result")
        self.save_btn.clicked.connect(self.save_dialog)
        self.save_btn.setEnabled(False)
        form.addWidget(self.save_btn)
        self.preview3d_btn = QPushButton("3D material preview")
        self.preview3d_btn.clicked.connect(self.show_3d_preview)
        form.addWidget(self.preview3d_btn)
        side.addWidget(box)

        history = QGroupBox("History")
        hbox = QHBoxLayout(history)
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo)
        self.undo_btn.setEnabled(False)
        self.redo_btn = QPushButton("Redo")
        self.redo_btn.clicked.connect(self.redo)
        self.redo_btn.setEnabled(False)
        hbox.addWidget(self.undo_btn)
        hbox.addWidget(self.redo_btn)
        side.addWidget(history)

        batch = QGroupBox("Batch processing")
        batch_layout = QVBoxLayout(batch)
        self.batch_btn = QPushButton("Process folder…")
        self.batch_btn.clicked.connect(self.batch_dialog)
        batch_layout.addWidget(self.batch_btn)
        side.addWidget(batch)

        metrics = QGroupBox("Seam analysis")
        grid = QGridLayout(metrics)
        self.score = QLabel("—")
        self.horizontal = QLabel("—")
        self.vertical = QLabel("—")
        self.rating = QLabel("Load a texture")
        for row, (name, widget) in enumerate([
            ("Seam score", self.score),
            ("Left / right", self.horizontal),
            ("Top / bottom", self.vertical),
            ("Assessment", self.rating),
        ]):
            grid.addWidget(QLabel(name), row, 0)
            grid.addWidget(widget, row, 1)
        side.addWidget(metrics)

        hint = QLabel("Drag & drop an image here\nPNG · JPG · TIFF · TGA · WEBP")
        hint.setStyleSheet("color:#8491a5;padding:8px;")
        hint.setWordWrap(True)
        side.addWidget(hint)
        side.addStretch(1)

        side_scroll = QScrollArea()
        side_scroll.setWidgetResizable(True)
        side_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        side_scroll.setFrameShape(QScrollArea.NoFrame)
        side_scroll.setMinimumWidth(250)
        side_scroll.setMaximumWidth(350)
        side_scroll.setWidget(side_content)

        previews = QSplitter(Qt.Horizontal)
        previews.setChildrenCollapsible(False)
        self.source_preview = ImagePreview("SOURCE")
        self.result_preview = ImagePreview("PROCESSED RESULT")
        self.source_preview.setMinimumSize(0, 0)
        self.result_preview.setMinimumSize(0, 0)
        previews.addWidget(self.source_preview)
        previews.addWidget(self.result_preview)
        previews.setStretchFactor(0, 1)
        previews.setStretchFactor(1, 1)
        previews.setSizes([500, 500])

        outer.addWidget(side_scroll, 0)
        outer.addWidget(previews, 1)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

    def open_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open texture", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.tga *.webp)"
        )
        if path:
            self.load_path(path)

    def load_path(self, path):
        try:
            self.original = load_image(path)
            self.path = Path(path)
            self.result = None
            self.history = ImageHistory()
            self.history.push("Opened image", self.original)
            self.source_preview.set_image(self.original, self.repeat.value())
            self.result_preview.clear("Process the source texture")
            self.save_btn.setEnabled(False)
            self._sync_history()
            self._show_metrics(analyze_edges(self.original))
            self.statusBar().showMessage(
                f"Loaded {self.path.name} · {self.original.shape[1]}×{self.original.shape[0]}"
            )
        except Exception as exc:
            QMessageBox.critical(self, "Could not open image", str(exc))

    def process(self):
        if self.original is None:
            return
        self.process_btn.setEnabled(False)
        self.statusBar().showMessage("Processing…")
        worker = FunctionWorker(process_image, self.original.copy(), self.algorithm.currentText())
        self._workers.add(worker)
        worker.signals.finished.connect(
            lambda payload, error, w=worker: (self._workers.discard(w), self._processed(payload, error))
        )
        self.pool.start(worker)

    def _processed(self, payload, error):
        self.process_btn.setEnabled(True)
        if error:
            QMessageBox.critical(self, "Processing failed", str(error))
            self.statusBar().showMessage("Processing failed")
            return
        self.result, metrics = payload
        self.history.push(self.algorithm.currentText(), self.result)
        self._display_result(metrics)
        self.statusBar().showMessage(f"Done · {self.result.shape[1]}×{self.result.shape[0]}")

    def _display_result(self, metrics=None):
        if self.result is None:
            return
        self.result_preview.set_image(self.result, self.repeat.value())
        self._show_metrics(metrics or analyze_edges(self.result))
        self.save_btn.setEnabled(True)
        self._sync_history()

    def _show_metrics(self, metrics):
        self.score.setText(f"{metrics['seam_score']:.1f}/100")
        self.horizontal.setText(f"{metrics['horizontal_edge_difference']:.2f}")
        self.vertical.setText(f"{metrics['vertical_edge_difference']:.2f}")
        self.rating.setText(metrics["rating"])

    def _sync_history(self):
        self.undo_btn.setEnabled(self.history.can_undo)
        self.redo_btn.setEnabled(self.history.can_redo)

    def undo(self):
        image = self.history.undo()
        if image is not None:
            self.result = image
            self._display_result()

    def redo(self):
        image = self.history.redo()
        if image is not None:
            self.result = image
            self._display_result()

    def show_3d_preview(self):
        image = self.result if self.result is not None else self.original
        if image is None:
            QMessageBox.information(self, "3D preview", "Open a texture first.")
            return
        self.preview_dialog = QDialog(self)
        self.preview_dialog.setWindowTitle("SeamlessForge · 3D Material Preview")
        self.preview_dialog.resize(900, 720)
        self.preview_dialog.setMinimumSize(520, 420)
        layout = QVBoxLayout(self.preview_dialog)
        layout.setContentsMargins(8, 8, 8, 8)
        try:
            view = Texture3DPreview(self.preview_dialog)
            view.setMinimumSize(0, 0)
            view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            view.set_image(image)
            layout.addWidget(view)
            self.preview_dialog.show()
        except Exception as exc:
            self.preview_dialog.deleteLater()
            self.preview_dialog = None
            QMessageBox.warning(
                self, "3D preview unavailable",
                f"Could not initialize OpenGL preview:\n{exc}"
            )

    def batch_dialog(self):
        source = QFileDialog.getExistingDirectory(self, "Select source folder")
        if not source:
            return
        output = QFileDialog.getExistingDirectory(self, "Select output folder")
        if not output:
            return
        self.batch_btn.setEnabled(False)
        self.statusBar().showMessage("Batch processing…")
        worker = FunctionWorker(process_folder, source, output, self.algorithm.currentText(), True)
        self._workers.add(worker)
        worker.signals.finished.connect(
            lambda result, error, w=worker: (self._workers.discard(w), self._batch_finished(result, error))
        )
        self.pool.start(worker)

    def _batch_finished(self, result, error):
        self.batch_btn.setEnabled(True)
        if error:
            QMessageBox.critical(self, "Batch processing failed", str(error))
            return
        QMessageBox.information(
            self, "Batch complete",
            f"Processed: {len(result['completed'])}\nFailed: {len(result['failures'])}"
        )
        self.statusBar().showMessage("Batch processing complete")

    def save_dialog(self):
        if self.result is None:
            return
        default = (self.path.stem if self.path else "texture") + "_seamless.png"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export texture", default,
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;TIFF (*.tiff);;TGA (*.tga);;WebP (*.webp)"
        )
        if path:
            try:
                save_image(path, self.result)
                self.statusBar().showMessage(f"Saved: {path}")
            except Exception as exc:
                QMessageBox.critical(self, "Export failed", str(exc))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.load_path(urls[0].toLocalFile())
