from __future__ import annotations

from PySide6.QtWidgets import QPlainTextEdit


class TerminalView(QPlainTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Terminal")
        self.setReadOnly(True)
        self.setPlaceholderText("Peer logs will appear here.")

    def append_log(self, line: str) -> None:
        self.appendPlainText(line)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
