from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QTextEdit, QVBoxLayout, QWidget

from quinkgl_desktop.core.models import PeerRunConfig, ProjectConfig
from quinkgl_desktop.core.process_manager import PeerProcessManager
from quinkgl_desktop.services.peer_run_service import PeerRunService
from quinkgl_desktop.ui.i18n import PAGES_COPY, RUN_COPY
from quinkgl_desktop.ui.icons import lucide_icon
from quinkgl_desktop.ui.pages.base import card, card_header, field, page_header, segmented
from quinkgl_desktop.ui.templates import RUN_PEER_CLI_TEMPLATE
from quinkgl_desktop.ui.tokens import COLORS, DEFAULTS, TOKENS


class RunPeerPage(QWidget):
    config_changed = Signal(object)
    navigate_requested = Signal(str)
    log_requested = Signal(str)

    def __init__(self, peer_run_service: PeerRunService, process_manager: PeerProcessManager) -> None:
        super().__init__()
        self.config: ProjectConfig | None = None
        self.peer_run_service = peer_run_service
        self.process_manager = process_manager
        self.is_running = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 40, 44, 44)
        layout.setSpacing(18)
        self.mode = segmented(
            [("basic", "Basic"), ("advanced", "Advanced")],
            "basic",
            self._mode_changed,
        )
        page_copy = PAGES_COPY["run"]
        layout.addWidget(page_header(
            page_copy["title"],
            page_copy["subtitle"],
            eyebrow=page_copy["eyebrow"],
            actions=self.mode,
        )[0])

        # Pre-flight strip
        preflight = QHBoxLayout()
        preflight.setSpacing(12)
        self.preflight_labels = {}
        for label, value in RUN_COPY["preflight"]:
            chip = QFrame()
            chip.setObjectName("PreflightChip")
            chip.setFixedHeight(52)
            row = QHBoxLayout(chip)
            row.setContentsMargins(16, 0, 16, 0)
            row.setSpacing(8)
            ok = QLabel()
            ok.setPixmap(lucide_icon("check", 12, COLORS["status_ok"]).pixmap(12, 12))
            lbl = QLabel(label.upper())
            lbl.setStyleSheet(f"font-size: 11px; color: {COLORS['text_dim']}; letter-spacing: 2px; font-weight: 700;")
            val = QLabel(value)
            val.setStyleSheet(f"font-size: 14px; color: {COLORS['text_body']}; font-family: 'JetBrains Mono'; font-weight: 700;")
            row.addWidget(ok)
            row.addWidget(lbl)
            row.addStretch(1)
            row.addWidget(val)
            self.preflight_labels[label] = val
            preflight.addWidget(chip, 1)
        layout.addLayout(preflight)

        body = QHBoxLayout()
        body.setSpacing(22)
        left = QVBoxLayout()
        left.setSpacing(18)

        # Identity
        identity, identity_layout = card()
        identity_layout.addWidget(card_header(RUN_COPY["identity_title"], RUN_COPY["identity_subtitle"]))
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        self.node_id = QLineEdit(DEFAULTS["node_id"])
        self.port = QSpinBox()
        self.port.setRange(0, 65535)
        self.port.setValue(DEFAULTS["port"])
        grid.addWidget(field(RUN_COPY["node_id_label"], self.node_id), 0, 0)
        grid.addWidget(field(RUN_COPY["port_label"], self.port, RUN_COPY["port_hint"]), 0, 1)
        identity_layout.addLayout(grid)
        left.addWidget(identity)

        # Training script
        script, script_layout = card()
        script_layout.addWidget(card_header(RUN_COPY["script_title"], RUN_COPY["script_subtitle"]))
        self.script_path = QLineEdit(DEFAULTS["script_path"])
        self.rounds = QSpinBox()
        self.rounds.setRange(1, 1_000_000)
        self.rounds.setValue(DEFAULTS["rounds"])
        self.trust_policy = QLineEdit(DEFAULTS["trust_policy"])
        self.script_args = QLineEdit("--data_root=./data")
        script_layout.addWidget(field(RUN_COPY["script_path_label"], self.script_path))
        script_grid = QGridLayout()
        script_grid.setHorizontalSpacing(12)
        script_grid.setVerticalSpacing(12)
        script_grid.addWidget(field(RUN_COPY["rounds_label"], self.rounds), 0, 0)
        self.trust_field = field(RUN_COPY["trust_policy_label"], self.trust_policy)
        script_grid.addWidget(self.trust_field, 0, 1)
        script_layout.addLayout(script_grid)
        self.args_field = field(RUN_COPY["script_args_label"], self.script_args, RUN_COPY["script_args_hint"])
        script_layout.addWidget(self.args_field)
        left.addWidget(script)

        # Runtime (advanced)
        self.runtime_card, runtime_layout = card()
        runtime_layout.addWidget(card_header(RUN_COPY["runtime_title"]))
        runtime_grid = QGridLayout()
        runtime_grid.setHorizontalSpacing(12)
        for i, (label, value) in enumerate([
            (RUN_COPY["device_label"], DEFAULTS["device"]),
            (RUN_COPY["workers_label"], DEFAULTS["workers"]),
            (RUN_COPY["log_level_label"], DEFAULTS["log_level"]),
        ]):
            edit = QLineEdit(value)
            runtime_grid.addWidget(field(label, edit), 0, i)
        runtime_layout.addLayout(runtime_grid)
        left.addWidget(self.runtime_card)

        # Launch action panel
        self.launch_panel = QFrame()
        self.launch_panel.setObjectName("LaunchPanel")
        self.launch_panel.setStyleSheet(f"""
            QFrame#LaunchPanel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {COLORS['launch_panel_start_stopped']}, stop:1 {COLORS['bg_app']});
                border: 1px solid {COLORS['border_strong']};
                border-radius: 14px;
            }}
        """)
        launch_layout = QHBoxLayout(self.launch_panel)
        launch_layout.setContentsMargins(20, 18, 20, 18)
        launch_layout.setSpacing(14)
        self.launch_icon_box = QFrame()
        self.launch_icon_box.setFixedSize(44, 44)
        self.launch_icon_box.setStyleSheet(f"background: {COLORS['launch_icon_bg_stopped']}; border: 1px solid {COLORS['launch_icon_border_stopped']}; border-radius: 9px;")
        icon_layout = QHBoxLayout(self.launch_icon_box)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        self.launch_icon = QLabel()
        self.launch_icon.setPixmap(lucide_icon("play-circle", 18, COLORS["gold_bright"]).pixmap(18, 18))
        icon_layout.addWidget(self.launch_icon, alignment=Qt.AlignCenter)
        launch_layout.addWidget(self.launch_icon_box)

        launch_text = QVBoxLayout()
        launch_text.setSpacing(4)
        self.launch_title = QLabel(RUN_COPY["ready_title"])
        self.launch_title.setStyleSheet(f"font-size: 15px; color: {COLORS['text_primary']}; font-weight: 720;")
        self.launch_desc = QLabel(RUN_COPY["ready_desc"])
        self.launch_desc.setStyleSheet(f"font-size: 13px; color: {COLORS['text_dim']};")
        launch_text.addWidget(self.launch_title)
        launch_text.addWidget(self.launch_desc)
        launch_layout.addLayout(launch_text, 1)

        self.start_button = QPushButton(RUN_COPY["start"])
        self.start_button.setProperty("primary", True)
        self.start_button.setFixedHeight(40)
        self.start_button.setIcon(lucide_icon("play-circle", 14, COLORS["text_disabled"]))
        self.start_button.clicked.connect(self.start_peer)
        self.stop_button = QPushButton(RUN_COPY["stop"])
        self.stop_button.setProperty("danger", True)
        self.stop_button.setFixedHeight(40)
        self.stop_button.setIcon(lucide_icon("square", 14, COLORS["status_error"]))
        self.stop_button.clicked.connect(self.process_manager.stop)
        self.stop_button.setVisible(False)
        launch_layout.addWidget(self.start_button)
        launch_layout.addWidget(self.stop_button)
        left.addWidget(self.launch_panel)
        body.addLayout(left, 7)

        # Right
        right = QVBoxLayout()
        right.setSpacing(16)
        preview, preview_layout = card(padded=False)
        preview.setMinimumWidth(380)
        preview.setMaximumWidth(460)
        ph = QFrame()
        ph.setObjectName("CodePreviewHeader")
        ph.setFixedHeight(52)
        ph_layout = QHBoxLayout(ph)
        ph_layout.setContentsMargins(18, 0, 18, 0)
        ph_layout.setSpacing(8)
        code_icon = QLabel()
        code_icon.setPixmap(lucide_icon("file-code", 13, COLORS["gold_bright"]).pixmap(13, 13))
        ph_layout.addWidget(code_icon)
        generated_title = QLabel(RUN_COPY["generated_command"])
        generated_title.setObjectName("CardTitle")
        ph_layout.addWidget(generated_title)
        ph_layout.addStretch(1)
        copy = QPushButton()
        copy.setFixedSize(28, 28)
        copy.setIcon(lucide_icon("copy", 12, COLORS["text_muted"]))
        copy.setProperty("ghost", True)
        copy.clicked.connect(lambda: QApplication.clipboard().setText(self.preview.toPlainText()))
        ph_layout.addWidget(copy)
        preview_layout.addWidget(ph)
        self.preview = QTextEdit()
        self.preview.setObjectName("CodePreview")
        self.preview.setReadOnly(True)
        self.preview.setMinimumHeight(250)
        preview_layout.addWidget(self.preview)
        terminal_hint = QLabel(RUN_COPY["terminal_hint"])
        terminal_hint.setStyleSheet(f"font-size: 13px; color: {TOKENS['textMute']}; padding: 12px 18px;")
        preview_layout.addWidget(terminal_hint)
        right.addWidget(preview)

        trust = QFrame()
        trust.setObjectName("TrustAdvisory")
        t_layout = QHBoxLayout(trust)
        t_layout.setContentsMargins(12, 12, 12, 12)
        t_layout.setSpacing(8)
        shield = QLabel()
        shield.setPixmap(lucide_icon("shield", 14, COLORS["gold_bright"]).pixmap(14, 14))
        t_layout.addWidget(shield)
        t_text = QLabel(RUN_COPY["trust_advisory"].format(policy=DEFAULTS["trust_policy"]))
        t_text.setStyleSheet(f"font-size: 13px; color: {COLORS['text_muted']}; line-height: 145%;")
        t_text.setWordWrap(True)
        t_layout.addWidget(t_text, 1)
        right.addWidget(trust)
        logs_note = QFrame()
        logs_note.setObjectName("TrustAdvisory")
        logs_layout = QHBoxLayout(logs_note)
        logs_layout.setContentsMargins(12, 12, 12, 12)
        logs_layout.setSpacing(8)
        logs_icon = QLabel()
        logs_icon.setPixmap(lucide_icon("info", 14, COLORS["text_muted"]).pixmap(14, 14))
        logs_layout.addWidget(logs_icon)
        logs_text = QLabel("Logs will stream into the Logs page once the peer is started.")
        logs_text.setStyleSheet(f"font-size: 13px; color: {COLORS['text_muted']}; line-height: 145%;")
        logs_text.setWordWrap(True)
        logs_layout.addWidget(logs_text, 1)
        right.addWidget(logs_note)
        body.addLayout(right)
        layout.addLayout(body)
        layout.addStretch(1)

        for widget in [self.node_id, self.script_path, self.trust_policy, self.script_args]:
            widget.textChanged.connect(self._update_preview)
        self.port.valueChanged.connect(lambda _v: self._update_preview())
        self.rounds.valueChanged.connect(lambda _v: self._update_preview())
        process_manager.status_changed.connect(self._set_status)
        self._mode_changed("basic")
        self._update_preview()

    def set_config(self, config: ProjectConfig) -> None:
        self.config = config
        self.node_id.setText(config.peer.node_id)
        self.port.setValue(config.peer.port)
        self.script_path.setText(config.peer.script_path)
        self.rounds.setValue(config.peer.rounds)
        self.trust_policy.setText(config.peer.trust_policy)
        self.script_args.setText(",".join(f"{k}={v}" for k, v in config.peer.script_args.items()))
        self.preflight_labels["Manifest"].setText(config.manifest_path or "missing")
        self.preflight_labels["Script"].setText(config.peer.script_path)
        self._update_preview()

    def _mode_changed(self, mode: str) -> None:
        advanced = mode == "advanced"
        self.trust_field.setVisible(advanced)
        self.args_field.setVisible(advanced)
        self.runtime_card.setVisible(advanced)

    def _parse_script_args(self) -> dict[str, str]:
        result = {}
        for item in self.script_args.text().split(","):
            if not item.strip() or "=" not in item:
                continue
            key, value = item.split("=", 1)
            result[key.strip()] = value.strip()
        return result

    def _sync_config(self) -> ProjectConfig | None:
        if not self.config:
            self.log_requested.emit("Open a project first.")
            return None
        self.config.peer = PeerRunConfig(
            node_id=self.node_id.text(),
            port=self.port.value(),
            script_path=self.script_path.text(),
            rounds=self.rounds.value(),
            trust_policy=self.trust_policy.text(),
            script_args=self._parse_script_args(),
        )
        self.config_changed.emit(self.config)
        return self.config

    def _update_preview(self) -> None:
        manifest = self.config.manifest_path if self.config and self.config.manifest_path else "<manifest.qgl>"
        args = "".join(f" \\\n  --script-arg {item.strip()}" for item in self.script_args.text().split(",") if item.strip())
        self.preview.setText(
            RUN_PEER_CLI_TEMPLATE.safe_substitute(
                manifest_path=manifest,
                script_path=self.script_path.text(),
                node_id=self.node_id.text(),
                port=self.port.value(),
                trust_policy=self.trust_policy.text(),
                rounds=self.rounds.value(),
                script_args=args,
            )
        )

    def start_peer(self) -> None:
        config = self._sync_config()
        if not config:
            return
        command = self.peer_run_service.build_command(config)
        env = self.peer_run_service.build_environment()
        self.log_requested.emit(f"$ {' '.join(command)}")
        self.process_manager.start(command, Path(config.workspace_path), env=env)
        self.navigate_requested.emit("logs")

    def _set_status(self, status: str) -> None:
        running = status == "running"
        self.is_running = running
        if running:
            self.launch_icon.setPixmap(lucide_icon("circle", 18, COLORS["status_ok"]).pixmap(18, 18))
            self.launch_icon_box.setStyleSheet(f"background: {COLORS['launch_icon_bg_running']}; border: 1px solid {COLORS['launch_icon_border_running']}; border-radius: 9px;")
            self.launch_panel.setStyleSheet(f"""
                QFrame#LaunchPanel {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {COLORS['launch_panel_start_running']}, stop:1 {COLORS['bg_app']});
                    border: 1px solid {COLORS['launch_icon_border_running']};
                    border-radius: 14px;
                }}
            """)
            self.launch_title.setText(RUN_COPY["running_title"])
            self.launch_desc.setText(RUN_COPY["running_desc"])
        else:
            self.launch_icon.setPixmap(lucide_icon("play-circle", 18, COLORS["gold_bright"]).pixmap(18, 18))
            self.launch_icon_box.setStyleSheet(f"background: {COLORS['launch_icon_bg_stopped']}; border: 1px solid {COLORS['launch_icon_border_stopped']}; border-radius: 9px;")
            self.launch_panel.setStyleSheet(f"""
                QFrame#LaunchPanel {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {COLORS['launch_panel_start_stopped']}, stop:1 {COLORS['bg_app']});
                    border: 1px solid {COLORS['border_strong']};
                    border-radius: 14px;
                }}
            """)
            self.launch_title.setText(RUN_COPY["ready_title"])
            self.launch_desc.setText(RUN_COPY["ready_desc"])
        self.start_button.setVisible(not running)
        self.stop_button.setVisible(running)
