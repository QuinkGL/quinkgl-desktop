from __future__ import annotations

from PySide6.QtWidgets import QLabel

from quinkgl_desktop.ui.tokens import COLORS


class StatusBadge(QLabel):
    COLORS = {
        "ready": (COLORS["status_ok"], "rgba(123,211,137,0.12)"),
        "running": (COLORS["status_ok"], "rgba(123,211,137,0.12)"),
        "missing": (COLORS["status_warn"], "rgba(244,208,111,0.10)"),
        "stopped": (COLORS["text_faint"], "rgba(90,84,70,0.10)"),
        "failed": (COLORS["status_error"], "rgba(255,138,107,0.12)"),
    }

    def __init__(self, text: str = "stopped", tone: str = "stopped") -> None:
        super().__init__(text)
        self.set_tone(text, tone)

    def set_tone(self, text: str, tone: str) -> None:
        color, bg = self.COLORS.get(tone, self.COLORS["stopped"])
        self.setText(text)
        self.setStyleSheet(
            "QLabel {"
            f"color: {color};"
            f"background: {bg};"
            f"border: 1px solid {color};"
            "border-radius: 10px;"
            "padding: 5px 9px;"
            "}"
        )
