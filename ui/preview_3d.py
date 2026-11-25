"""Interactive OpenGL sphere material preview."""
import ctypes

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QMatrix4x4, QVector3D, QSurfaceFormat
from PySide6.QtOpenGL import QOpenGLShader, QOpenGLShaderProgram, QOpenGLTexture
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import (
    glClearColor, glClear, glEnable, glViewport, glGenVertexArrays, glBindVertexArray,
    glGenBuffers, glBindBuffer, glBufferData, glEnableVertexAttribArray, glVertexAttribPointer,
    glDrawElements, glDeleteBuffers, glDeleteVertexArrays, glDepthFunc,
    GL_DEPTH_TEST, GL_LEQUAL, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER, GL_STATIC_DRAW, GL_FLOAT,
    GL_FALSE, GL_TRIANGLES, GL_UNSIGNED_INT,
)

VERTEX_SHADER = """#version 330 core
layout(location=0) in vec3 position;
layout(location=1) in vec2 texcoord;
layout(location=2) in vec3 normal;
uniform mat4 mvp;
uniform mat4 model;
out vec2 uv;
out vec3 worldNormal;
void main() {
    uv = texcoord;
    worldNormal = mat3(model) * normal;
    gl_Position = mvp * vec4(position, 1.0);
}
"""

FRAGMENT_SHADER = """#version 330 core
in vec2 uv;
in vec3 worldNormal;
uniform sampler2D materialTexture;
out vec4 fragColor;
void main() {
    vec3 n = normalize(worldNormal);
    vec3 l = normalize(vec3(-0.4, 0.8, 0.7));
    float d = max(dot(n, l), 0.0);
    vec4 t = texture(materialTexture, uv);
    fragColor = vec4(t.rgb * (0.28 + d * 0.72), t.a);
}
"""


def _sphere(rows=32, columns=64):
    vertices = []
    indices = []
    for y in range(rows + 1):
        v = y / rows
        phi = v * np.pi
        for x in range(columns + 1):
            u = x / columns
            theta = u * 2 * np.pi
            point = (
                np.sin(phi) * np.cos(theta),
                np.cos(phi),
                np.sin(phi) * np.sin(theta),
            )
            vertices.extend((*point, u, v, *point))
    for y in range(rows):
        for x in range(columns):
            a = y * (columns + 1) + x
            b = a + columns + 1
            indices.extend((a, b, a + 1, a + 1, b, b + 1))
    return np.asarray(vertices, np.float32), np.asarray(indices, np.uint32)


class Texture3DPreview(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        fmt = QSurfaceFormat()
        fmt.setRenderableType(QSurfaceFormat.OpenGL)
        fmt.setVersion(3, 3)
        fmt.setProfile(QSurfaceFormat.CoreProfile)
        fmt.setDepthBufferSize(24)
        self.setFormat(fmt)

        self.setMinimumSize(0, 0)
        self._vertices, self._indices = _sphere()
        self._texture = None
        self._image = None
        self._vao = 0
        self._vbo = 0
        self._ebo = 0
        self._program = None
        self._last_pos = None
        self.rotation_x = -15.0
        self.rotation_y = 25.0

    def set_image(self, image):
        self._image = np.array(image, copy=True)
        if self.isValid():
            self.makeCurrent()
            try:
                self._upload_texture()
            finally:
                self.doneCurrent()
        self.update()

    def initializeGL(self):
        # QOpenGLWidget owns the context; all PyOpenGL calls must happen while
        # this widget's context is current. Normalize GL object names to Python
        # ints because PyOpenGL can return NumPy scalar types on some platforms.
        from OpenGL.GL import glGetString, GL_VERSION
        context = self.context()
        if context is None or not context.isValid():
            raise RuntimeError("Qt did not create a valid OpenGL context.")
        actual = context.format()
        if (actual.majorVersion(), actual.minorVersion()) < (3, 3):
            raise RuntimeError(
                f"OpenGL 3.3 is required; received {actual.majorVersion()}.{actual.minorVersion()}."
            )
        version = glGetString(GL_VERSION)
        if not version:
            raise RuntimeError("OpenGL context is not current.")
        glClearColor(0.055, 0.07, 0.095, 1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        self._program = QOpenGLShaderProgram(self)
        if not self._program.addShaderFromSourceCode(QOpenGLShader.Vertex, VERTEX_SHADER):
            raise RuntimeError(f"Vertex shader compilation failed: {self._program.log()}")
        if not self._program.addShaderFromSourceCode(QOpenGLShader.Fragment, FRAGMENT_SHADER):
            raise RuntimeError(f"Fragment shader compilation failed: {self._program.log()}")
        if not self._program.link():
            raise RuntimeError(f"Shader link failed: {self._program.log()}")

        self._vao = int(glGenVertexArrays(1))
        self._vbo = int(glGenBuffers(1))
        self._ebo = int(glGenBuffers(1))
        if not self._vao or not self._vbo or not self._ebo:
            raise RuntimeError("OpenGL could not allocate the sphere mesh buffers.")

        glBindVertexArray(self._vao)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, self._vertices.nbytes, self._vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self._indices.nbytes, self._indices, GL_STATIC_DRAW)
        for location, size, offset in ((0, 3, 0), (1, 2, 12), (2, 3, 20)):
            glEnableVertexAttribArray(location)
            glVertexAttribPointer(
                location, size, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(offset)
            )
        glBindVertexArray(0)

        if self._image is not None:
            self._upload_texture()

    def _upload_texture(self):
        if self._texture is not None:
            self._texture.destroy()
            self._texture = None
        if self._image is None:
            return
        from .preview import to_qimage
        self._texture = QOpenGLTexture(to_qimage(self._image).mirrored())
        self._texture.setWrapMode(QOpenGLTexture.DirectionS, QOpenGLTexture.Repeat)
        self._texture.setWrapMode(QOpenGLTexture.DirectionT, QOpenGLTexture.Repeat)
        self._texture.setMinificationFilter(QOpenGLTexture.LinearMipMapLinear)
        self._texture.setMagnificationFilter(QOpenGLTexture.Linear)
        self._texture.generateMipMaps()

    def paintGL(self):
        glViewport(0, 0, self.width(), self.height())
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self._program is None or self._texture is None:
            return
        projection = QMatrix4x4()
        projection.perspective(
            42, max(1, self.width()) / max(1, self.height()), 0.1, 100
        )
        view = QMatrix4x4()
        view.lookAt(QVector3D(0, 0, 3.2), QVector3D(0, 0, 0), QVector3D(0, 1, 0))
        model = QMatrix4x4()
        model.rotate(self.rotation_x, 1, 0, 0)
        model.rotate(self.rotation_y, 0, 1, 0)

        self._program.bind()
        self._program.setUniformValue("mvp", projection * view * model)
        self._program.setUniformValue("model", model)
        self._program.setUniformValue("materialTexture", 0)
        self._texture.bind(0)
        glBindVertexArray(int(self._vao))
        glDrawElements(GL_TRIANGLES, int(self._indices.size), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        self._texture.release()
        self._program.release()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, max(1, height))

    def mousePressEvent(self, event):
        self._last_pos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self._last_pos is not None and event.buttons() & Qt.LeftButton:
            pos = event.position().toPoint()
            delta = pos - self._last_pos
            self.rotation_x = max(-89, min(89, self.rotation_x + delta.y() * 0.6))
            self.rotation_y += delta.x() * 0.6
            self._last_pos = pos
            self.update()

    def mouseReleaseEvent(self, event):
        self._last_pos = None

    def wheelEvent(self, event):
        self.rotation_y += event.angleDelta().y() / 24
        self.update()

    def closeEvent(self, event):
        if self.isValid():
            self.makeCurrent()
            try:
                if self._texture is not None:
                    self._texture.destroy()
                if self._vbo:
                    glDeleteBuffers(1, [int(self._vbo)])
                if self._ebo:
                    glDeleteBuffers(1, [int(self._ebo)])
                if self._vao:
                    glDeleteVertexArrays(1, [int(self._vao)])
            finally:
                self.doneCurrent()
        super().closeEvent(event)
