from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from quinkgl_desktop.core.models import ProjectConfig
from quinkgl_desktop.services.telemetry_service import TelemetryService
from quinkgl_desktop.ui.i18n import PAGES_COPY, TELEMETRY_COPY
from quinkgl_desktop.ui.icons import lucide_icon
from quinkgl_desktop.ui.pages.base import badge, card, card_header, field, page_header
from quinkgl_desktop.ui.tokens import COLORS, DEFAULTS


class TelemetryPage(QWidget):
    config_changed = Signal(object)
    log_requested = Signal(str)
    activity_recorded = Signal(str, str, str)

    def __init__(self, telemetry_service: TelemetryService) -> None:
        super().__init__()
        self.config: ProjectConfig | None = None
        self.telemetry_service = telemetry_service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 40, 44, 44)
        layout.setSpacing(18)
        page_copy = PAGES_COPY["telemetry"]
        layout.addWidget(page_header(
            page_copy["title"],
            page_copy["subtitle"],
            eyebrow=page_copy["eyebrow"],
        )[0])

        body = QHBoxLayout()
        body.setSpacing(22)
        left = QVBoxLayout()
        left.setSpacing(18)

        # Dashboard backend
        backend, backend_layout = card()
        backend_layout.addWidget(card_header(TELEMETRY_COPY["backend_title"], TELEMETRY_COPY["backend_subtitle"]))
        self.dashboard_url = QLineEdit(DEFAULTS["dashboard_url"])
        self.dashboard_url.setReadOnly(True)
        self.dashboard_code = QLineEdit("")
        backend_layout.addWidget(field(TELEMETRY_COPY["dashboard_url_label"], self.dashboard_url, TELEMETRY_COPY["dashboard_url_hint"]))
        backend_layout.addWidget(field(TELEMETRY_COPY["dashboard_code_label"], self.dashboard_code, TELEMETRY_COPY["dashboard_code_hint"]))
        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        enroll = QPushButton(TELEMETRY_COPY["enroll"])
        enroll.setObjectName("TelemetryEnrollButton")
        enroll.setProperty("primary", True)
        enroll.setFixedSize(156, 38)
        enroll.setIcon(lucide_icon("radio", 13, COLORS["text_disabled"]))
        enroll.clicked.connect(self.enroll)
        request = QPushButton(TELEMETRY_COPY["request_code"])
        request.setObjectName("TelemetryRequestButton")
        request.setProperty("secondary", True)
        request.setFixedSize(166, 38)
        request.setIcon(lucide_icon("refresh-cw", 12, COLORS["text_muted"]))
        request.clicked.connect(self.dashboard_code_request)
        buttons.addWidget(enroll)
        buttons.addWidget(request)
        buttons.addStretch(1)
        backend_layout.addLayout(buttons)
        left.addWidget(backend)

        # Trust & verification
        trust, trust_layout = card()
        trust_layout.addWidget(card_header(TELEMETRY_COPY["trust_title"], TELEMETRY_COPY["trust_subtitle"]))
        trust_grid = QGridLayout()
        trust_grid.setSpacing(12)
        for i, (label, value) in enumerate([
            (TELEMETRY_COPY["manifest_signed"], "-"),
            (TELEMETRY_COPY["creator_key"], TELEMETRY_COPY["ed25519"]),
            (TELEMETRY_COPY["backend_reachable"], TELEMETRY_COPY["tls"]),
        ]):
            item = QFrame()
            item.setObjectName("InnerCard")
            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(14, 12, 14, 12)
            item_layout.setSpacing(7)
            ok_row = QHBoxLayout()
            ok_row.setSpacing(4)
            ok_icon = QLabel()
            ok_icon.setPixmap(lucide_icon("check", 11, COLORS["status_ok"]).pixmap(11, 11))
            ok_label = QLabel(label.upper())
            ok_label.setStyleSheet(f"font-size: 11px; color: {COLORS['text_dim']}; letter-spacing: 1.8px; font-weight: 700;")
            ok_row.addWidget(ok_icon)
            ok_row.addWidget(ok_label)
            ok_row.addStretch(1)
            item_layout.addLayout(ok_row)
            val = QLabel(value)
            val.setStyleSheet(f"font-size: 14px; color: {COLORS['text_body']}; font-family: 'JetBrains Mono';")
            item_layout.addWidget(val)
            trust_grid.addWidget(item, 0, i)
        trust_layout.addLayout(trust_grid)
        left.addWidget(trust)
        body.addLayout(left, 7)

        # Right status
        right, right_layout = card()
        right.setMinimumWidth(340)
        right.setMaximumWidth(380)
        self.status_badge = badge(TELEMETRY_COPY["pending"], "amber")
        right_layout.addWidget(card_header(TELEMETRY_COPY["status"], action=self.status_badge))
        self.status_rows = QVBoxLayout()
        self.status_rows.setSpacing(0)
        right_layout.addLayout(self.status_rows)

        note = QLabel(TELEMETRY_COPY["telemetry_note"])
        note.setStyleSheet(f"font-size: 13px; color: {COLORS['text_dim']}; line-height: 145%; background: {COLORS['bg_input']}; border: 1px solid {COLORS['border_default']}; border-radius: 10px; padding: 14px;")
        note.setWordWrap(True)
        right_layout.addWidget(note)
        body.addWidget(right)
        layout.addLayout(body)
        layout.addStretch(1)
        self.dashboard_url.textChanged.connect(self._sync_config_soft)
        self._render_status()

    def set_config(self, config: ProjectConfig) -> None:
        self.config = config
        config.dashboard_url = DEFAULTS["dashboard_url"]
        self.dashboard_url.setText(DEFAULTS["dashboard_url"])
        self._render_status()

    def _render_status(self) -> None:
        while self.status_rows.count():
            item = self.status_rows.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        rows = [
            (TELEMETRY_COPY["endpoint"], self.dashboard_url.text()),
            (TELEMETRY_COPY["local_key"], self.config.telemetry_key_path if self.config and self.config.telemetry_key_path else "qglkey.local"),
            (TELEMETRY_COPY["last_enrolled"], TELEMETRY_COPY["pending"]),
            (TELEMETRY_COPY["manifest"], self.config.manifest_path if self.config and self.config.manifest_path else "-"),
        ]
        for index, (key, value) in enumerate(rows):
            row = QFrame()
            row.setObjectName("StatusRow")
            row.setProperty("last", index == len(rows) - 1)
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(0, 10, 0, 10)
            row_layout.setSpacing(4)
            k = QLabel(key)
            k.setStyleSheet(f"font-size: 12px; color: {COLORS['text_muted']}; letter-spacing: 1.4px; font-weight: 700;")
            v = QLabel(value)
            v.setStyleSheet(f"font-size: 14px; color: {COLORS['text_body']}; font-family: 'JetBrains Mono';")
            row_layout.addWidget(k)
            row_layout.addWidget(v)
            self.status_rows.addWidget(row)

    def _sync_config_soft(self) -> None:
        if self.config:
            self.config.dashboard_url = DEFAULTS["dashboard_url"]
            self.config_changed.emit(self.config)
        self._render_status()

    def _sync_config(self) -> ProjectConfig | None:
        if not self.config:
            return None
        self.config.dashboard_url = DEFAULTS["dashboard_url"]
        self.config_changed.emit(self.config)
        return self.config

    def enroll(self) -> None:
        config = self._sync_config()
        if not config:
            return
        result = self.telemetry_service.enroll(config)
        output = (result.stdout + result.stderr).strip()
        if result.ok:
            key_path = self._parse_written_path(output)
            if key_path:
                config.telemetry_key_path = self._workspace_relative(key_path, config)
                self.config_changed.emit(config)
            self.status_badge.setText(f"✓ {TELEMETRY_COPY['enrolled']}")
            self.status_badge.setProperty("badge", "green")
            self.activity_recorded.emit("telemetry", "Telemetry enrolled", config.dashboard_url)
        else:
            self.status_badge.setText(TELEMETRY_COPY["pending"])
            self.status_badge.setProperty("badge", "red")
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)
        self._render_status()
        self.log_requested.emit(f"$ {' '.join(result.command)}\n{result.stdout}{result.stderr}")

    def dashboard_code_request(self) -> None:
        config = self._sync_config()
        if not config:
            return
        result = self.telemetry_service.dashboard_code(config)
        output = (result.stdout + result.stderr).strip()
        self.dashboard_code.setText(self._parse_dashboard_code(output))
        self.log_requested.emit(f"$ {' '.join(result.command)}\n{result.stdout}{result.stderr}")

    def _parse_written_path(self, output: str) -> Path | None:
        for line in output.splitlines():
            if line.startswith("wrote:"):
                return Path(line.split(":", 1)[1].strip())
        return None

    def _workspace_relative(self, path: Path, config: ProjectConfig) -> str:
        workspace = Path(config.workspace_path).expanduser().resolve()
        resolved = path.expanduser()
        if not resolved.is_absolute():
            return str(resolved)
        try:
            return str(resolved.resolve().relative_to(workspace))
        except ValueError:
            return str(resolved)

    def _parse_dashboard_code(self, output: str) -> str:
        for line in output.splitlines():
            if line.lower().startswith("dashboard code:"):
                return line.split(":", 1)[1].strip()
        return output.splitlines()[-1] if output else ""
