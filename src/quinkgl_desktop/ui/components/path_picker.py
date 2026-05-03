from __future__ import annotations

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, QWidget


class PathPicker(QWidget):
    def __init__(self, mode: str = "file") -> None:
        super().__init__()
        self.mode = mode
        self.input = QLineEdit()
        self.button = QPushButton("Browse")
        self.button.clicked.connect(self._browse)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.input, 1)
        layout.addWidget(self.button)

    def text(self) -> str:
        return self.input.text()

    def setText(self, value: str) -> None:
        self.input.setText(value)

    def _browse(self) -> None:
        if self.mode == "directory":
            path = QFileDialog.getExistingDirectory(self, "Select directory")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Select file")
        if path:
            self.input.setText(path)
