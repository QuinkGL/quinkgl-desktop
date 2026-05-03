from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from quinkgl_desktop.core.cli_adapter import QuinkGLCli
from quinkgl_desktop.core.models import CliConfig, ProjectConfig
from quinkgl_desktop.ui.i18n import PAGES_COPY, SETTINGS_COPY
from quinkgl_desktop.ui.icons import lucide_icon
from quinkgl_desktop.ui.pages.base import badge, card, card_header, field, page_header, toggle
from quinkgl_desktop.ui.settings_nav import SETTINGS_SECTIONS
from quinkgl_desktop.ui.tokens import COLORS


class SettingsPage(QWidget):
    binary_changed = Signal(str)
    cli_changed = Signal(object)

    def __init__(self, cli: QuinkGLCli | None = None) -> None:
        super().__init__()
        self.cli = cli
        self.config: ProjectConfig | None = None
        self._syncing = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 40, 44, 44)
        layout.setSpacing(18)
        page_copy = PAGES_COPY["settings"]
        layout.addWidget(page_header(page_copy["title"], page_copy["subtitle"], eyebrow=page_copy["eyebrow"])[0])

        body = QHBoxLayout()
        body.setSpacing(22)

        # Nav
        nav, nav_layout = card(padded=False)
        nav.setFixedWidth(240)
        nav_layout.setContentsMargins(8, 8, 8, 8)
        nav_layout.setSpacing(4)
        self.nav_buttons: list[QPushButton] = []
        for i, section in enumerate(SETTINGS_SECTIONS):
            btn = QPushButton(section.label)
            btn.setIcon(lucide_icon(section.icon, 13, COLORS["text_muted"], stroke=1.7))
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda _checked=False, index=i: self.show_section(index))
            self.nav_buttons.append(btn)
            nav_layout.addWidget(btn)
        nav_layout.addStretch(1)
        body.addWidget(nav)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._general())
        self.stack.addWidget(self._workspace())
        self.stack.addWidget(self._advanced())
        self.stack.addWidget(self._storage())
        self.stack.addWidget(self._about())
        body.addWidget(self.stack, 1)
        layout.addLayout(body)
        layout.addStretch(1)
        self.show_section(0)

    def _setting_row(self, label: str, desc: str | None = None, widget: QWidget | None = None, last: bool = False) -> QFrame:
        row = QFrame()
        row.setObjectName("SettingRow")
        if last:
            row.setProperty("last", True)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 14, 0, 14)
        row_layout.setSpacing(16)
        text = QVBoxLayout()
        text.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 14px; color: {COLORS['text_body']}; font-weight: 700;")
        text.addWidget(lbl)
        if desc:
            d = QLabel(desc)
            d.setStyleSheet(f"font-size: 13px; color: {COLORS['text_dim']}; line-height: 145%;")
            text.addWidget(d)
        row_layout.addLayout(text, 1)
        if widget:
            row_layout.addWidget(widget, 0, Qt.AlignVCenter)
        return row

    def _general(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        cli, cli_layout = card()
        cli_layout.addWidget(card_header(SETTINGS_COPY["cli_title"], SETTINGS_COPY["cli_subtitle"]))
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        self.binary = QLineEdit("quinkgl")
        self.binary.setObjectName("CliBinaryField")
        self.binary.textChanged.connect(self._binary_text_changed)
        self.local_source = QLineEdit("")
        self.local_source.setObjectName("CliLocalSourceField")
        self.local_source.setPlaceholderText("~/QuinkGL")
        self.local_source.textChanged.connect(self._emit_cli_changed)
        self.python_binary = QLineEdit("python")
        self.python_binary.setObjectName("CliPythonField")
        self.python_binary.textChanged.connect(self._emit_cli_changed)
        self.cli_work_dir = QLineEdit("")
        self.cli_work_dir.setObjectName("CliWorkDirField")
        self.cli_work_dir.textChanged.connect(self._emit_cli_changed)
        grid.addWidget(field(SETTINGS_COPY["binary_label"], self.binary), 0, 0)
        grid.addWidget(field("Local source", self.local_source, "Optional QuinkGL repository override"), 0, 1)
        grid.addWidget(field("Python", self.python_binary), 1, 0)
        grid.addWidget(field("CLI work dir", self.cli_work_dir), 1, 1)
        cli_layout.addLayout(grid)
        row = QHBoxLayout()
        row.setSpacing(8)
        detect = QPushButton(SETTINGS_COPY["detect"])
        detect.setProperty("secondary", True)
        detect.clicked.connect(self._detect_cli)
        row.addWidget(detect)
        self.detect_badge = badge(SETTINGS_COPY["not_found"], "neutral")
        row.addWidget(self.detect_badge)
        row.addStretch(1)
        cli_layout.addLayout(row)
        layout.addWidget(cli)

        behavior, behavior_layout = card()
        behavior_layout.addWidget(card_header(SETTINGS_COPY["behavior"], SETTINGS_COPY["behavior_subtitle"]))
        behavior_layout.addWidget(self._setting_row(
            SETTINGS_COPY["autostart_label"],
            SETTINGS_COPY["autostart_desc"],
            toggle(False, lambda v: None),
        ))
        behavior_layout.addWidget(self._setting_row(
            SETTINGS_COPY["analytics_label"],
            SETTINGS_COPY["analytics_desc"],
            toggle(True, lambda v: None),
        ))
        behavior_layout.addWidget(self._setting_row(
            SETTINGS_COPY["updates_label"],
            SETTINGS_COPY["updates_desc"],
            toggle(True, lambda v: None),
            last=True,
        ))
        layout.addWidget(behavior)
        layout.addStretch(1)
        return page

    def _detect_cli(self) -> None:
        if not self.cli:
            return
        version = self.cli.detect_version()
        if version:
            self.detect_badge.setText(SETTINGS_COPY["found_version"].format(version=version))
            self.detect_badge.setProperty("badge", "green")
        else:
            self.detect_badge.setText(SETTINGS_COPY["not_found"])
            self.detect_badge.setProperty("badge", "red")
        self.detect_badge.style().unpolish(self.detect_badge)
        self.detect_badge.style().polish(self.detect_badge)

    def set_cli(self, cli: QuinkGLCli) -> None:
        self.cli = cli

    def set_config(self, config: ProjectConfig) -> None:
        self.config = config
        self._syncing = True
        try:
            self.binary.setText(config.cli.binary)
            self.local_source.setText(config.cli.local_source_path)
            self.python_binary.setText(config.cli.python_binary)
            self.cli_work_dir.setText(config.cli.work_dir)
        finally:
            self._syncing = False

    def _emit_cli_changed(self) -> None:
        if self._syncing:
            return
        self.cli_changed.emit(
            CliConfig(
                binary=self.binary.text() or "quinkgl",
                local_source_path=self.local_source.text(),
                python_binary=self.python_binary.text() or "python",
                work_dir=self.cli_work_dir.text(),
            )
        )

    def _binary_text_changed(self, text: str) -> None:
        if not self._syncing:
            self.binary_changed.emit(text)
        self._emit_cli_changed()

    def _workspace(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        frame, frame_layout = card()
        frame_layout.addWidget(card_header(SETTINGS_COPY["workspace_title"], SETTINGS_COPY["workspace_subtitle"]))
        frame_layout.addWidget(field(SETTINGS_COPY["default_folder_label"], QLineEdit("~/QuinkGL"), SETTINGS_COPY["default_folder_hint"]))
        frame_layout.addWidget(field(SETTINGS_COPY["logs_retention_label"], QLineEdit("30"), SETTINGS_COPY["logs_retention_hint"]))
        layout.addWidget(frame)
        layout.addStretch(1)
        return page

    def _advanced(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        frame, frame_layout = card()
        frame_layout.addWidget(card_header(SETTINGS_COPY["advanced_title"], SETTINGS_COPY["advanced_subtitle"]))
        frame_layout.addWidget(self._setting_row(SETTINGS_COPY["verbose_logging_label"], SETTINGS_COPY["verbose_logging_desc"], toggle(False, lambda v: None)))
        frame_layout.addWidget(self._setting_row(SETTINGS_COPY["strict_trust_label"], SETTINGS_COPY["strict_trust_desc"], toggle(False, lambda v: None), last=True))
        layout.addWidget(frame)
        layout.addStretch(1)
        return page

    def _storage(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        frame, frame_layout = card()
        frame_layout.addWidget(card_header(SETTINGS_COPY["storage_title"], SETTINGS_COPY["storage_subtitle"]))
        grid = QGridLayout()
        grid.setSpacing(12)
        for i, (label, value) in enumerate([
            (SETTINGS_COPY["cache_label"], "212 MB"),
            (SETTINGS_COPY["run_logs_label"], "48 MB"),
            (SETTINGS_COPY["manifests_label"], "1.2 MB"),
        ]):
            item = QFrame()
            item.setObjectName("InnerCard")
            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(10, 8, 10, 8)
            lbl = QLabel(label.upper())
            lbl.setStyleSheet(f"font-size: 10.5px; color: {COLORS['text_dim']}; letter-spacing: 0.5px;")
            val = QLabel(value)
            val.setStyleSheet(f"font-size: 16px; color: {COLORS['text_primary']}; margin-top: 4px;")
            item_layout.addWidget(lbl)
            item_layout.addWidget(val)
            grid.addWidget(item, 0, i)
        frame_layout.addLayout(grid)
        clear = QPushButton(SETTINGS_COPY["clear_cache"])
        clear.setProperty("secondary", True)
        frame_layout.addWidget(clear)
        layout.addWidget(frame)
        layout.addStretch(1)
        return page

    def _about(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        frame, frame_layout = card()
        frame_layout.addWidget(card_header(SETTINGS_COPY["about_title"]))
        for k, v in [
            (SETTINGS_COPY["version_label"], "0.1 (build 1142)"),
            (SETTINGS_COPY["cli_version_label"], "v0.3.4"),
            (SETTINGS_COPY["channel_label"], "stable"),
            (SETTINGS_COPY["license_label"], "Apache 2.0"),
        ]:
            row = QHBoxLayout()
            row.setContentsMargins(0, 6, 0, 6)
            key = QLabel(k)
            key.setStyleSheet(f"font-size: 12.5px; color: {COLORS['text_dim']};")
            val = QLabel(v)
            val.setStyleSheet(f"font-size: 12.5px; color: {COLORS['text_body']}; font-family: 'JetBrains Mono';")
            row.addWidget(key)
            row.addStretch(1)
            row.addWidget(val)
            frame_layout.addLayout(row)
            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet(f"background: {COLORS['border_default']};")
            frame_layout.addWidget(sep)
        layout.addWidget(frame)
        layout.addStretch(1)
        return page

    def show_section(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)
            icon_name = SETTINGS_SECTIONS[i].icon
            icon_color = COLORS["gold_bright"] if i == index else COLORS["text_muted"]
            button.setIcon(lucide_icon(icon_name, 13, icon_color, stroke=1.7))
