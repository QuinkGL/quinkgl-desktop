from __future__ import annotations

from html import escape

from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from quinkgl_desktop.core.process_manager import PeerProcessManager
from quinkgl_desktop.ui.i18n import LOGS_COPY, PAGES_COPY, STATUS_LABELS
from quinkgl_desktop.ui.icons import lucide_icon
from quinkgl_desktop.ui.pages.base import badge, card, page_header, segmented
from quinkgl_desktop.ui.tokens import COLORS, DEFAULTS, LEVEL_COLORS


class LogsPage(QWidget):
    def __init__(self, process_manager: PeerProcessManager) -> None:
        super().__init__()
        self.process_manager = process_manager
        self.all_lines: list[tuple[str, str, str, str]] = []
        self.paused = False
        self.wrap = True
        self.copied = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 40, 44, 44)
        layout.setSpacing(18)

        page_copy = PAGES_COPY["logs"]
        actions = QHBoxLayout()
        actions.setSpacing(8)
        self.status_badge = badge(f"● {STATUS_LABELS['stopped']}", "neutral")
        self.dashboard_code = badge("dashboard -", "gold")
        actions.addWidget(self.status_badge)
        actions.addWidget(self.dashboard_code)
        action_widget = QWidget()
        action_widget.setLayout(actions)
        layout.addWidget(page_header(page_copy["title"], page_copy["subtitle"], eyebrow=page_copy["eyebrow"], actions=action_widget)[0])

        # Console card
        console, console_layout = card(padded=False)
        console.setObjectName("ConsoleFrame")
        console_layout.setContentsMargins(0, 0, 0, 0)
        console_layout.setSpacing(0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setObjectName("LogsToolbar")
        toolbar.setFixedHeight(56)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(14, 0, 14, 0)
        tb_layout.setSpacing(8)

        search_container = QFrame()
        search_container.setObjectName("ToolbarSearchFrame")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(6, 0, 6, 0)
        search_layout.setSpacing(4)
        search_icon = QLabel()
        search_icon.setPixmap(lucide_icon("search", 12, COLORS["text_faint"]).pixmap(12, 12))
        self.search = QLineEdit()
        self.search.setObjectName("ToolbarSearch")
        self.search.setPlaceholderText(LOGS_COPY["filter_placeholder"])
        self.search.setStyleSheet(f"background: transparent; border: none; color: {COLORS['text_body']}; font-size: 13px; padding: 4px 0; min-height: 0;")
        self.search.textChanged.connect(self._render)
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search, 1)
        tb_layout.addWidget(search_container, 1)

        self.level_filter = segmented(
            [("all", "All"), ("info", "Info"), ("warn", "Warn"), ("error", "Error")],
            "all",
            self._set_filter,
        )
        tb_layout.addWidget(self.level_filter)
        tb_layout.addStretch(1)

        self.pause_button = QPushButton(LOGS_COPY["pause"])
        self.pause_button.setProperty("ghost", True)
        self.pause_button.setIcon(lucide_icon("pause", 11, COLORS["text_muted"]))
        self.pause_button.clicked.connect(self.toggle_pause)
        tb_layout.addWidget(self.pause_button)

        self.wrap_button = QPushButton(LOGS_COPY["no_wrap"])
        self.wrap_button.setProperty("ghost", True)
        self.wrap_button.setIcon(lucide_icon("align-left", 11, COLORS["text_muted"]))
        self.wrap_button.clicked.connect(self.toggle_wrap)
        tb_layout.addWidget(self.wrap_button)

        copy_btn = QPushButton(LOGS_COPY["copy"])
        copy_btn.setProperty("ghost", True)
        copy_btn.setIcon(lucide_icon("copy", 11, COLORS["text_muted"]))
        copy_btn.clicked.connect(self.copy_logs)
        tb_layout.addWidget(copy_btn)

        export_btn = QPushButton(LOGS_COPY["export"])
        export_btn.setProperty("ghost", True)
        export_btn.setIcon(lucide_icon("download", 11, COLORS["text_muted"]))
        export_btn.clicked.connect(self.export_logs)
        tb_layout.addWidget(export_btn)

        clear_btn = QPushButton(LOGS_COPY["clear"])
        clear_btn.setProperty("ghost", True)
        clear_btn.setIcon(lucide_icon("trash-2", 11, COLORS["text_muted"]))
        clear_btn.clicked.connect(self.clear)
        tb_layout.addWidget(clear_btn)
        console_layout.addWidget(toolbar)

        # Terminal
        self.terminal = QTextEdit()
        self.terminal.setObjectName("Terminal")
        self.terminal.setReadOnly(True)
        self.terminal.setPlaceholderText(LOGS_COPY["empty_stopped"])
        self.terminal.document().setMaximumBlockCount(5000)
        self.terminal.setMinimumHeight(420)
        console_layout.addWidget(self.terminal, 1)

        # Footer
        footer = QFrame()
        footer.setObjectName("LogsFooter")
        footer.setFixedHeight(42)
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(14, 0, 14, 0)
        self.footer_left = QLabel(LOGS_COPY["lines_fmt"].format(count=0, filter="all"))
        self.footer_left.setStyleSheet(f"font-size: 10.5px; color: {COLORS['text_faint']};")
        self.footer_right = QLabel(LOGS_COPY["peer_fmt"].format(node_id=DEFAULTS["node_id"], port=DEFAULTS["port"]))
        self.footer_right.setStyleSheet(f"font-size: 10.5px; color: {COLORS['text_faint']}; font-family: 'JetBrains Mono';")
        f_layout.addWidget(self.footer_left)
        f_layout.addStretch(1)
        f_layout.addWidget(self.footer_right)
        console_layout.addWidget(footer)

        layout.addWidget(console, 1)

        process_manager.log_line.connect(self.append_log)
        process_manager.dashboard_code.connect(self._set_dashboard_code)
        process_manager.status_changed.connect(self._set_status)

    def append_log(self, text: str) -> None:
        for line in text.splitlines():
            parts = line.split(None, 2)
            if len(parts) >= 3:
                t, level, msg = parts[0], parts[1].lower(), parts[2]
                tag = "peer"
                self.all_lines.append((t, level, tag, msg))
            else:
                self.all_lines.append(("", "info", "peer", line))
        if not self.paused:
            self._render()

    def _set_filter(self, level: str) -> None:
        self._render()

    def _render(self) -> None:
        query = self.search.text().lower()
        active_level = "all"
        for btn in self.level_filter.findChildren(QPushButton):
            if btn.isChecked():
                active_level = btn.text().lower()
                break

        visible = []
        for i, (t, level, tag, msg) in enumerate(self.all_lines):
            if active_level != "all" and level != active_level:
                continue
            if query and query not in msg.lower() and query not in tag.lower():
                continue
            num = str(i + 1).rjust(4)
            level_color = LEVEL_COLORS.get(level, COLORS["text_muted"])
            visible.append(
                f'<span style="color:{COLORS["text_disabled"]}">{num}</span>  '
                f'<span style="color:{COLORS["text_faint"]}">{t}</span>  '
                f'<span style="color:{level_color}; font-weight:700; letter-spacing:1px">{level.upper()}</span>  '
                f'<span style="color:{COLORS["gold_bright"]}">{escape(tag)}</span>  '
                f'<span style="color:{COLORS["text_disabled"]}">›</span>  '
                f'<span style="color:{COLORS["text_body"]}">{escape(msg)}</span>'
            )

        self.terminal.clear()
        line_count = len(visible)
        if visible:
            status = LOGS_COPY["live"] if self.process_manager.is_running() else LOGS_COPY["eof"]
            visible.append(
                f'<br><span style="color:{COLORS["text_disabled"]}">{str(len(visible)).rjust(4)}</span>  '
                f'<span style="color:{COLORS["text_faint"]}">───</span>  '
                f'<span style="color:{COLORS["text_faint"]}">{status}</span>'
            )
            self.terminal.setHtml(
                '<div style="font-family: JetBrains Mono, Menlo, Consolas, monospace; '
                'font-size: 13px; line-height: 1.45; white-space: pre;">'
                + "<br>".join(visible)
                + "</div>"
            )
        else:
            self.terminal.setPlainText(
                LOGS_COPY["empty_running"] if self.process_manager.is_running() else LOGS_COPY["empty_stopped"]
            )

        if self.paused:
            self.footer_left.setText(LOGS_COPY["lines_fmt_paused"].format(count=line_count, filter=active_level))
        else:
            self.footer_left.setText(LOGS_COPY["lines_fmt"].format(count=line_count, filter=active_level))
        if not self.paused:
            sb = self.terminal.verticalScrollBar()
            sb.setValue(sb.maximum())

    def toggle_pause(self) -> None:
        self.paused = not self.paused
        self.pause_button.setText(LOGS_COPY["resume"] if self.paused else LOGS_COPY["pause"])
        self.pause_button.setIcon(lucide_icon("play" if self.paused else "pause", 11, COLORS["text_muted"]))
        if not self.paused:
            self._render()

    def toggle_wrap(self) -> None:
        self.wrap = not self.wrap
        self.wrap_button.setText(LOGS_COPY["no_wrap"] if self.wrap else LOGS_COPY["wrap"])
        self.terminal.setLineWrapMode(QTextEdit.WidgetWidth if self.wrap else QTextEdit.NoWrap)

    def clear(self) -> None:
        self.all_lines.clear()
        self._render()

    def copy_logs(self) -> None:
        text = self.terminal.toPlainText()
        QApplication.clipboard().setText(text)
        self.copied = True

    def export_logs(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export QuinkGL logs", "quinkgl-peer.log", "Log files (*.log);;Text files (*.txt);;All files (*)")
        if path:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(self.terminal.toPlainText())

    def _set_dashboard_code(self, code: str) -> None:
        self.dashboard_code.setText(f"dashboard {code}")

    def _set_status(self, status: str) -> None:
        self.status_badge.setText(f"● {status}")
        self.status_badge.setProperty("badge", "green" if status == "running" else "neutral")
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)
        self._render()
