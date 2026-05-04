from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from quinkgl_desktop.core.models import ManifestConfig, ProjectConfig
from quinkgl_desktop.services.hash_service import HashService
from quinkgl_desktop.services.key_service import KeyService
from quinkgl_desktop.services.manifest_service import ManifestService
from quinkgl_desktop.services.model_preset_service import ModelPresetService
from quinkgl_desktop.ui.i18n import MANIFEST_COPY, PAGES_COPY
from quinkgl_desktop.ui.icons import lucide_icon
from quinkgl_desktop.ui.pages.base import badge, card, card_header, field, gold_button, page_header, segmented
from quinkgl_desktop.ui.presets import MANIFEST_PRESETS, PRESET_BY_LABEL
from quinkgl_desktop.ui.templates import MANIFEST_CLI_TEMPLATE
from quinkgl_desktop.ui.tokens import COLORS, DEFAULTS, TOKENS


class ManifestPage(QWidget):
    config_changed = Signal(object)
    log_requested = Signal(str)
    activity_recorded = Signal(str, str, str)

    def __init__(self, key_service: KeyService, manifest_service: ManifestService) -> None:
        super().__init__()
        self.config: ProjectConfig | None = None
        self.key_service = key_service
        self.manifest_service = manifest_service
        self.hash_service = HashService()
        self.model_preset_service = ModelPresetService()
        self.active_preset_key = "custom"
        self.view = "CLI"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 40, 44, 44)
        layout.setSpacing(18)

        self.mode = segmented(
            [("basic", "Basic"), ("advanced", "Advanced")],
            "basic",
            self._mode_changed,
        )
        page_copy = PAGES_COPY["manifest"]
        layout.addWidget(page_header(
            page_copy["title"],
            page_copy["subtitle"],
            eyebrow=page_copy["eyebrow"],
            actions=self.mode,
        )[0])

        body = QHBoxLayout()
        body.setSpacing(22)
        left = QVBoxLayout()
        left.setSpacing(18)

        # Presets — prototype style
        preset_card, preset_layout = card()
        preset_layout.addWidget(card_header(MANIFEST_COPY["preset_title"], MANIFEST_COPY["preset_subtitle"]))
        preset_grid = QGridLayout()
        preset_grid.setSpacing(8)
        self.preset_buttons: dict[str, tuple[QFrame, QLabel]] = {}
        for i, preset in enumerate(MANIFEST_PRESETS):
            tile = QFrame()
            tile.setObjectName("PresetTile")
            tile_layout = QVBoxLayout(tile)
            tile_layout.setContentsMargins(16, 16, 16, 16)
            tile_layout.setSpacing(7)
            title_row = QHBoxLayout()
            title = QLabel(preset.label)
            title.setStyleSheet(f"font-size: 15px; color: {TOKENS['text']}; font-weight: 700;")
            check_label = QLabel()
            check_label.setPixmap(lucide_icon("check", 12, TOKENS["goldSoft"]).pixmap(12, 12))
            check_label.setVisible(False)
            title_row.addWidget(title)
            title_row.addStretch(1)
            title_row.addWidget(check_label)
            desc = QLabel(preset.description)
            desc.setStyleSheet(f"font-size: 13px; color: {TOKENS['textDim']}; line-height: 1.45;")
            desc.setWordWrap(True)
            tile_layout.addLayout(title_row)
            tile_layout.addWidget(desc, 1)
            tile.mousePressEvent = lambda event, name=preset.label: self.apply_preset(name)  # type: ignore[method-assign]
            self.preset_buttons[preset.label] = (tile, check_label)
            preset_grid.addWidget(tile, 0, i)
        preset_layout.addLayout(preset_grid)
        left.addWidget(preset_card)

        # Dataset — prototype style
        dataset, dataset_layout = card()
        dataset_layout.addWidget(card_header(MANIFEST_COPY["dataset_title"], MANIFEST_COPY["dataset_subtitle"]))
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        self.name = QLineEdit(DEFAULTS["manifest_name"])
        self.task_type = QLineEdit(DEFAULTS["task_type"])
        self.input_shape = QLineEdit(DEFAULTS["input_shape"])
        self.output_shape = QLineEdit(DEFAULTS["output_shape"])
        self.label_type = QLineEdit(DEFAULTS["label_type"])
        self.output = QLineEdit(DEFAULTS["output_path"])
        fields = [
            (MANIFEST_COPY["manifest_name_label"], self.name, None),
            (MANIFEST_COPY["task_type_label"], self.task_type, None),
            (MANIFEST_COPY["input_shape_label"], self.input_shape, MANIFEST_COPY["input_shape_hint"]),
            (MANIFEST_COPY["output_shape_label"], self.output_shape, None),
            (MANIFEST_COPY["label_type_label"], self.label_type, None),
            (MANIFEST_COPY["output_file_label"], self.output, None),
        ]
        for idx, (label, widget, hint) in enumerate(fields):
            grid.addWidget(field(label, widget, hint), idx // 2, idx % 2)
        dataset_layout.addLayout(grid)

        # Advanced fields
        self.advanced_frame = QFrame()
        adv_layout = QGridLayout(self.advanced_frame)
        adv_layout.setHorizontalSpacing(12)
        adv_layout.setVerticalSpacing(12)
        self.model_framework = QLineEdit(DEFAULTS["model_framework"])
        self.model_hash = QLineEdit()
        self.aggregation = QLineEdit(DEFAULTS["aggregation"])
        self.topology = QLineEdit(DEFAULTS["topology"])
        adv_layout.addWidget(field("Framework", self.model_framework), 0, 0)
        adv_layout.addWidget(field("Aggregation", self.aggregation), 0, 1)
        adv_layout.addWidget(field("Topology", self.topology), 1, 0)
        self.hash_field = field("Arch hash", self.model_hash, "Auto-filled from script")
        adv_layout.addWidget(self.hash_field, 1, 1)
        dataset_layout.addWidget(self.advanced_frame)

        preset_actions = QHBoxLayout()
        preset_actions.setSpacing(8)
        generate_key = QPushButton("Generate creator.key")
        generate_key.setProperty("secondary", True)
        generate_key.setIcon(lucide_icon("key-round", 12, COLORS["text_muted"]))
        generate_key.clicked.connect(self.generate_key)
        install_preset = QPushButton("Install preset files")
        install_preset.setProperty("secondary", True)
        install_preset.setIcon(lucide_icon("download", 12, COLORS["text_muted"]))
        install_preset.clicked.connect(self.install_preset_files)
        compute_hash = QPushButton("Compute hash")
        compute_hash.setProperty("secondary", True)
        compute_hash.setIcon(lucide_icon("file-code", 12, COLORS["text_muted"]))
        compute_hash.clicked.connect(self.compute_model_hash)
        preset_actions.addWidget(generate_key)
        preset_actions.addWidget(install_preset)
        preset_actions.addWidget(compute_hash)
        preset_actions.addStretch(1)
        dataset_layout.addLayout(preset_actions)

        self.feedback_label = QLabel("Ready.")
        self.feedback_label.setObjectName("ManifestFeedback")
        self.feedback_label.setStyleSheet(f"font-size: 12.5px; color: {TOKENS['textDim']};")
        dataset_layout.addWidget(self.feedback_label)

        # Footer actions
        footer = QHBoxLayout()
        self.output_label = QLabel(MANIFEST_COPY["output_label"].format(file=DEFAULTS["output_path"]))
        self.output_label.setStyleSheet(f"font-size: 11.5px; color: {TOKENS['textDim']};")
        show_btn = QPushButton("Show")
        show_btn.setProperty("ghost", True)
        show_btn.clicked.connect(self.show_manifest)
        verify_btn = gold_button("Validate", variant="outline", size="sm")
        verify_btn.clicked.connect(self.verify_manifest)
        create = gold_button(MANIFEST_COPY["create"], variant="primary", size="sm", icon="layers")
        create.clicked.connect(self.create_manifest)
        footer.addWidget(self.output_label)
        footer.addStretch(1)
        footer.addWidget(show_btn)
        footer.addWidget(verify_btn)
        footer.addWidget(create)
        dataset_layout.addLayout(footer)
        left.addWidget(dataset)
        body.addLayout(left, 7)

        # Right preview — prototype style
        preview, preview_layout = card(padded=False)
        preview.setMinimumWidth(380)
        preview.setMaximumWidth(460)
        preview_header = QFrame()
        preview_header.setObjectName("CodePreviewHeader")
        preview_header.setFixedHeight(52)
        ph_layout = QHBoxLayout(preview_header)
        ph_layout.setContentsMargins(18, 0, 18, 0)
        ph_layout.setSpacing(8)
        code_icon = QLabel()
        code_icon.setPixmap(lucide_icon("file-code-2", 13, TOKENS["goldSoft"]).pixmap(13, 13))
        preview_title = QLabel("Preview")
        preview_title.setStyleSheet(f"font-size: 15px; color: {TOKENS['text']}; font-weight: 700;")
        ph_layout.addWidget(code_icon)
        ph_layout.addWidget(preview_title)
        ph_layout.addStretch(1)
        self.view_toggle = segmented(
            [("CLI", "CLI"), ("YAML", "YAML")],
            "CLI",
            self._set_view,
        )
        ph_layout.addWidget(self.view_toggle)
        copy_button = QPushButton()
        copy_button.setFixedSize(26, 24)
        copy_button.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {TOKENS['border']};
                border-radius: 5px;
                color: {TOKENS['textDim']};
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.03);
                border-color: {TOKENS['borderMid']};
            }}
        """)
        copy_button.setIcon(lucide_icon("copy", 11, TOKENS["textDim"]))
        copy_button.clicked.connect(self.copy_preview)
        ph_layout.addWidget(copy_button)
        preview_layout.addWidget(preview_header)

        self.preview = QTextEdit()
        self.preview.setObjectName("CodePreview")
        self.preview.setReadOnly(True)
        self.preview.setMinimumHeight(320)
        preview_layout.addWidget(self.preview)

        self.preview_footer = QLabel()
        self.preview_footer.setStyleSheet(f"font-size: 12px; color: {TOKENS['textMute']}; padding: 10px 18px;")
        preview_layout.addWidget(self.preview_footer)
        body.addWidget(preview)
        layout.addLayout(body)
        layout.addStretch(1)

        for widget in [self.name, self.task_type, self.input_shape, self.output_shape, self.label_type, self.output, self.model_framework, self.model_hash, self.aggregation, self.topology]:
            widget.textChanged.connect(self._update_preview)
        self.apply_preset("Custom")
        self._mode_changed("basic")

    def set_config(self, config: ProjectConfig) -> None:
        self.config = config
        self.name.setText(config.manifest.name)
        self.task_type.setText(config.manifest.task_type)
        self.input_shape.setText(config.manifest.input_shape)
        self.output_shape.setText(config.manifest.output_shape)
        self.label_type.setText(config.manifest.label_type)
        self.model_framework.setText(config.manifest.model_framework)
        self.model_hash.setText(config.manifest.model_arch_hash)
        self.aggregation.setText(config.manifest.aggregation)
        self.topology.setText(config.manifest.topology)
        self.output.setText(config.manifest.output_path)
        self._update_preview()

    def apply_preset(self, name: str) -> None:
        values = PRESET_BY_LABEL[name]
        self.active_preset_key = values.key
        self.name.setText(values.name)
        self.task_type.setText(values.task_type)
        self.input_shape.setText(values.input_shape)
        self.output_shape.setText(values.output_shape)
        self.label_type.setText(values.label_type)
        self.output.setText(values.output_path)
        for preset, (tile, check) in self.preset_buttons.items():
            is_active = preset == name
            check.setVisible(is_active)
            tile.setProperty("selected", is_active)
            tile.style().unpolish(tile)
            tile.style().polish(tile)
        self._update_preview()

    def _mode_changed(self, mode: str) -> None:
        self.advanced_frame.setVisible(mode == "advanced")

    def _set_view(self, view: str) -> None:
        self.view = view
        self._update_preview()

    def _cli(self) -> str:
        return MANIFEST_CLI_TEMPLATE.safe_substitute(
            name=self.name.text(),
            task_type=self.task_type.text(),
            input_shape=self.input_shape.text(),
            output_shape=self.output_shape.text(),
            label_type=self.label_type.text(),
            model_framework=self.model_framework.text(),
            model_arch_hash=self.model_hash.text() or "<auto>",
            aggregation=self.aggregation.text(),
            topology=self.topology.text(),
            output_path=self.output.text(),
        )

    def _yaml(self) -> str:
        return (
            f"name: {self.name.text()}\n"
            f"task: {self.task_type.text()}\n"
            f"input_shape: [{self.input_shape.text()}]\n"
            f"output_shape: [{self.output_shape.text()}]\n"
            f"label_type: {self.label_type.text()}\n"
            "model:\n"
            f"  framework: {self.model_framework.text()}\n"
            f"  arch_hash: {self.model_hash.text() or '<auto>'}\n"
            f"aggregation: {self.aggregation.text()}\n"
            f"topology: {self.topology.text()}\n"
            f"output: {self.output.text()}"
        )

    def _update_preview(self) -> None:
        text = self._yaml() if self.view == "YAML" else self._cli()
        self.preview.setText(text)
        self.preview_footer.setText(f"{'manifest.yaml' if self.view == 'YAML' else 'shell'} \u00b7 {len(text)} chars")
        self.output_label.setText(MANIFEST_COPY["output_label"].format(file=self.output.text()))

    def copy_preview(self) -> None:
        QApplication.clipboard().setText(self.preview.toPlainText())

    def _sync_config(self) -> ProjectConfig | None:
        if not self.config:
            return None
        self.config.manifest = ManifestConfig(
            name=self.name.text(),
            task_type=self.task_type.text(),
            input_shape=self.input_shape.text(),
            output_shape=self.output_shape.text(),
            label_type=self.label_type.text(),
            model_framework=self.model_framework.text(),
            model_arch_hash=self.model_hash.text(),
            aggregation=self.aggregation.text(),
            topology=self.topology.text(),
            output_path=self.output.text(),
        )
        self.config.manifest_path = self.output.text()
        self.config_changed.emit(self.config)
        return self.config

    def generate_key(self) -> None:
        config = self._sync_config()
        if not config:
            return
        self._feedback("Generating creator key...")
        result = self.key_service.generate_creator_key(config.workspace)
        if result.ok:
            config.creator_key_path = "creator.key"
            self.config_changed.emit(config)
            self._feedback("Creator key generated.")
            self.activity_recorded.emit("creator_key", "Creator key generated", "creator.key")
        else:
            self._feedback("Creator key generation failed.")
        self.log_requested.emit(f"$ {' '.join(result.command)}\n{result.stdout}{result.stderr}")

    def hash_default_script(self) -> None:
        config = self._sync_config()
        if not config:
            return
        script = config.workspace / config.peer.script_path
        if not script.exists():
            return
        self.model_hash.setText(self.hash_service.sha256_file(Path(script)))
        self._sync_config()

    def create_manifest(self) -> None:
        config = self._sync_config()
        if not config:
            return
        if not config.manifest.model_arch_hash.strip():
            self._feedback("Model architecture hash is required before manifest creation.")
            return
        self._feedback("Creating manifest...")
        result = self.manifest_service.create_manifest(config)
        self._feedback("Manifest created." if result.ok else "Manifest creation failed.")
        self.log_requested.emit(f"$ {' '.join(result.command)}\n{result.stdout}{result.stderr}")
        if result.ok:
            self.activity_recorded.emit("manifest", "Manifest signed", config.manifest.output_path)

    def install_preset_files(self) -> None:
        config = self._sync_config()
        if not config:
            return
        if self.active_preset_key == "custom":
            self._feedback("Choose CIFAR-10, MNIST, or ImageNet-1k before installing preset files.")
            return
        self._feedback(f"Installing {self.active_preset_key} preset files...")
        result = self.model_preset_service.install_preset(self.active_preset_key, config.workspace)
        for name, status in result.installed.items():
            self.log_requested.emit(f"{name}: {status}")
        config.peer.script_path = "peer_script.py"
        self.config_changed.emit(config)
        self._feedback("Preset files installed.")

    def compute_model_hash(self) -> None:
        config = self._sync_config()
        if not config:
            return
        script = config.workspace / "compute_hash.py"
        if not script.exists():
            self._feedback("compute_hash.py is missing. Install preset files first.")
            return
        self._feedback("Computing model architecture hash...")
        _command, env = self.manifest_service.cli.prepare_command([])
        result = self.model_preset_service.compute_hash(
            config.workspace,
            python_binary=config.cli.python_binary,
            env=env,
        )
        self.log_requested.emit(f"$ {' '.join(result.command)}\n{result.stdout}{result.stderr}")
        if result.ok:
            self.model_hash.setText(result.hash_value)
            self._sync_config()
            self._feedback(f"Computed model hash: {result.hash_value}")
        else:
            self._feedback("Model hash computation failed.")

    def _feedback(self, message: str) -> None:
        self.feedback_label.setText(message)
        self.log_requested.emit(message)

    def show_manifest(self) -> None:
        config = self._sync_config()
        if not config:
            return
        result = self.manifest_service.show_manifest(config)
        self.log_requested.emit(f"$ {' '.join(result.command)}\n{result.stdout}{result.stderr}")

    def verify_manifest(self) -> None:
        config = self._sync_config()
        if not config:
            return
        result = self.manifest_service.verify_manifest(config)
        self.log_requested.emit(f"$ {' '.join(result.command)}\n{result.stdout}{result.stderr}")
