from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from quinkgl_desktop.core.artifact_resolver import ProjectArtifacts
from quinkgl_desktop.core.models import ProjectConfig
from quinkgl_desktop.ui.i18n import OVERVIEW_COPY, PAGES_COPY
from quinkgl_desktop.ui.icons import lucide_icon
from quinkgl_desktop.ui.pages.base import card, card_header, gold_button, gold_icon_box, muted_label, page_header, progress_bar
from quinkgl_desktop.ui.tokens import TOKENS

DELIM_MAP = {
    "creator_key": "key-round",
    "manifest": "file-cog",
    "telemetry": "radio",
    "peer_start": "play-circle",
    "peer_stop": "square",
    "navigation": "arrow-right",
    "project": "folder-open",
}


def format_relative_time(timestamp: datetime) -> str:
    seconds = (datetime.now() - timestamp).total_seconds()
    if seconds < 60:
        return "just now"
    minutes = int(seconds / 60)
    if minutes < 60:
        return f"{minutes}m ago"
    hours = int(minutes / 60)
    if hours < 24:
        return f"{hours}h ago"
    days = int(hours / 24)
    return f"{days}d ago"


class OverviewPage(QWidget):
    navigate_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.config: ProjectConfig | None = None
        self.artifacts: ProjectArtifacts | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 40, 44, 44)
        layout.setSpacing(18)

        page_copy = PAGES_COPY["overview"]
        actions = gold_button(
            OVERVIEW_COPY["continue_setup"],
            variant="soft",
            icon="wand-2",
            icon_size=13,
        )
        actions.clicked.connect(lambda: self.navigate_requested.emit("wizard"))
        self.header = page_header(
            page_copy["title"].format(project=""),
            page_copy["subtitle"],
            eyebrow=page_copy["eyebrow"],
            actions=actions,
        )[0]
        layout.addWidget(self.header)

        # Hero readiness card — prototype style
        hero = QFrame()
        hero.setProperty("card", True)
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(0, 0, 0, 0)
        hero_layout.setSpacing(0)

        hero_top = QHBoxLayout()
        hero_top.setContentsMargins(24, 22, 24, 22)
        hero_top.setSpacing(24)
        hero_text = QVBoxLayout()
        hero_text.setSpacing(10)

        eyebrow_row = QHBoxLayout()
        eyebrow_row.setSpacing(6)
        shield = QLabel()
        shield.setPixmap(lucide_icon("shield-check", 13, TOKENS["goldSoft"]).pixmap(13, 13))
        eyebrow_label = QLabel("PROJECT READINESS")
        eyebrow_label.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {TOKENS['goldSoft']};")
        self.launch_button = gold_button(
            OVERVIEW_COPY["launch_peer"],
            variant="primary",
            icon="play",
            icon_size=13,
        )
        self.launch_button.clicked.connect(self._launch_peer)
        eyebrow_row.addWidget(shield)
        eyebrow_row.addWidget(eyebrow_label)
        eyebrow_row.addStretch(1)
        eyebrow_row.addWidget(self.launch_button, 0, Qt.AlignVCenter)
        hero_text.addLayout(eyebrow_row)

        count_row = QHBoxLayout()
        count_row.setSpacing(8)
        self.ready_count = QLabel("0")
        self.ready_count.setStyleSheet(f"font-size: 38px; color: {TOKENS['text']}; font-weight: 600; line-height: 1;")
        self.ready_count_suffix = QLabel("/ 3 prerequisites complete")
        self.ready_count_suffix.setStyleSheet(f"font-size: 14px; color: {TOKENS['textDim']};")
        count_row.addWidget(self.ready_count)
        count_row.addWidget(self.ready_count_suffix)
        count_row.addStretch(1)
        hero_text.addLayout(count_row)

        self.progress_holder = QVBoxLayout()
        self.progress_holder.setContentsMargins(0, 4, 0, 4)
        hero_text.addLayout(self.progress_holder)

        self.hero_guidance = QLabel(OVERVIEW_COPY["incomplete_guidance"])
        self.hero_guidance.setStyleSheet(f"font-size: 12px; color: {TOKENS['textDim']}; line-height: 140%; max-width: 760px;")
        self.hero_guidance.setWordWrap(True)
        hero_text.addWidget(self.hero_guidance)
        hero_top.addLayout(hero_text, 1)
        hero_layout.addLayout(hero_top)

        # Steps strip — prototype style with numbered circles
        strip = QHBoxLayout()
        strip.setContentsMargins(18, 0, 18, 18)
        strip.setSpacing(14)
        self.step_widgets: list[tuple[QFrame, QLabel, QLabel, QPushButton]] = []
        steps = OVERVIEW_COPY["readiness"]
        for col, (title, desc, page) in enumerate(steps):
            step = QFrame()
            step.setObjectName("ReadinessStep")
            step.setCursor(Qt.PointingHandCursor)
            step_layout = QVBoxLayout(step)
            step_layout.setContentsMargins(16, 16, 16, 16)
            step_layout.setSpacing(8)

            top_row = QHBoxLayout()
            top_row.setSpacing(6)
            tick_frame = QFrame()
            tick_frame.setObjectName("ReadinessTickCircle")
            tick_frame.setFixedSize(18, 18)
            tick_layout = QVBoxLayout(tick_frame)
            tick_layout.setContentsMargins(0, 0, 0, 0)
            tick_label = QLabel()
            tick_label.setAlignment(Qt.AlignCenter)
            tick_label.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {TOKENS['textMute']};")
            tick_layout.addWidget(tick_label)
            step_label = QLabel(f"STEP {col + 1}")
            step_label.setStyleSheet(f"font-size: 10px; font-weight: 600; letter-spacing: 0.16em; color: {TOKENS['textMute']}; text-transform: uppercase;")
            top_row.addWidget(tick_frame)
            top_row.addWidget(step_label)
            top_row.addStretch(1)
            step_layout.addLayout(top_row)

            title_label = QLabel(title)
            title_label.setStyleSheet(f"font-size: 13.5px; color: {TOKENS['text']}; font-weight: 600;")
            desc_label = QLabel(desc)
            desc_label.setStyleSheet(f"font-size: 12px; color: {TOKENS['textDim']}; line-height: 1.5;")
            desc_label.setWordWrap(True)
            step_layout.addWidget(title_label)
            step_layout.addWidget(desc_label)

            action_btn = QPushButton("Review \u2192")
            action_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    color: {TOKENS['goldSoft']};
                    font-size: 12px;
                    font-weight: 500;
                    padding: 0;
                    text-align: left;
                }}
                QPushButton:hover {{
                    color: {TOKENS['gold']};
                }}
            """)
            action_btn.setCursor(Qt.PointingHandCursor)
            action_btn.clicked.connect(lambda _checked=False, p=page: self.navigate_requested.emit(p))
            step_layout.addWidget(action_btn)

            step.mousePressEvent = lambda event, p=page: self.navigate_requested.emit(p)  # type: ignore[method-assign]
            strip.addWidget(step, 1)
            self.step_widgets.append((tick_frame, tick_label, title_label, action_btn))
        hero_layout.addLayout(strip)
        layout.addWidget(hero)

        # Two-up lower section
        lower = QHBoxLayout()
        lower.setSpacing(18)

        # Quick actions — prototype style with gold icon boxes
        quick, quick_layout = card()
        quick_layout.addWidget(card_header(OVERVIEW_COPY["quick_actions"], OVERVIEW_COPY["quick_actions_subtitle"]))
        quick_grid = QGridLayout()
        quick_grid.setSpacing(8)
        for index, (page, title, desc) in enumerate(OVERVIEW_COPY["quick_items"]):
            q = QFrame()
            q.setObjectName("QuickAction")
            q.setCursor(Qt.PointingHandCursor)
            q_layout = QHBoxLayout(q)
            q_layout.setContentsMargins(14, 14, 14, 14)
            q_layout.setSpacing(12)

            icon_map = {
                "wizard": "wand-2",
                "manifest": "file-code-2",
                "telemetry": "antenna",
                "logs": "terminal",
            }
            icon_name = icon_map.get(page, "arrow-right")
            box = gold_icon_box(icon_name, 13)
            q_layout.addWidget(box)

            copy = QVBoxLayout()
            copy.setSpacing(3)
            title_label = QLabel(title)
            title_label.setStyleSheet(f"font-size: 13px; color: {TOKENS['text']}; font-weight: 600;")
            desc_label = QLabel(desc)
            desc_label.setStyleSheet(f"font-size: 11.5px; color: {TOKENS['textDim']};")
            desc_label.setWordWrap(True)
            copy.addWidget(title_label)
            copy.addWidget(desc_label)
            q_layout.addLayout(copy, 1)

            arrow = QLabel("\u2192")
            arrow.setStyleSheet(f"font-size: 13px; color: {TOKENS['textMute']};")
            q_layout.addWidget(arrow)
            q.mousePressEvent = lambda event, p=page: self.navigate_requested.emit(p)  # type: ignore[method-assign]
            quick_grid.addWidget(q, index // 2, index % 2)
        quick_layout.addLayout(quick_grid)
        lower.addWidget(quick, 2)

        # Activity — prototype style
        activity, activity_layout = card()
        activity_layout.addWidget(card_header(OVERVIEW_COPY["recent_activity"]))
        self.activity_lines = QVBoxLayout()
        self.activity_lines.setSpacing(10)
        activity_layout.addLayout(self.activity_lines)
        lower.addWidget(activity, 1)
        layout.addLayout(lower)
        layout.addStretch(1)

    def _launch_peer(self) -> None:
        self.navigate_requested.emit("run")

    def refresh(self, config: ProjectConfig | None, artifacts: ProjectArtifacts | None, peer_status: str, activity: list[dict] | None = None) -> None:
        self.config = config
        self.artifacts = artifacts
        manifest_ready = bool(artifacts and artifacts.manifest_ready)
        key_ready = bool(artifacts and artifacts.creator_key_ready)
        telemetry_ready = bool(artifacts and artifacts.telemetry_ready)
        ready = [key_ready, manifest_ready, telemetry_ready]
        completed = sum(ready)
        project_name = config.project_name if config else "project"

        page_title = self.header.findChild(QLabel, "PageTitle")
        if page_title:
            page_title.setText(PAGES_COPY["overview"]["title"].format(project=project_name))
        self.ready_count.setText(str(completed))
        self.launch_button.setEnabled(completed == 3)
        self.hero_guidance.setText(
            OVERVIEW_COPY["complete_guidance"]
            if completed == 3
            else OVERVIEW_COPY["incomplete_guidance"]
        )

        while self.progress_holder.count():
            item = self.progress_holder.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        self.progress_holder.addWidget(progress_bar(completed / 3))

        for index, (tick_frame, tick_label, title_label, action_btn) in enumerate(self.step_widgets):
            label, desc, _page = OVERVIEW_COPY["readiness"][index]
            is_ready = ready[index]
            action = OVERVIEW_COPY["review"] if is_ready else OVERVIEW_COPY["configure"]
            if is_ready:
                tick_frame.setProperty("ready", True)
                tick_label.setText("\u2713")
                tick_label.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {TOKENS['goldSoft']};")
            else:
                tick_frame.setProperty("ready", False)
                tick_label.setText(str(index + 1))
                tick_label.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {TOKENS['textMute']};")
            tick_frame.style().unpolish(tick_frame)
            tick_frame.style().polish(tick_frame)
            title_label.setText(label)
            action_btn.setText(f"{action} \u2192")

        while self.activity_lines.count():
            item = self.activity_lines.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        activities = activity if activity else []

        if not activities:
            fallback = [
                ("Manifest signed", "missing", "file-cog"),
                ("Telemetry enrolled", "pending", "radio"),
                ("Creator key", "missing", "key-round"),
                ("Peer runtime", peer_status, "play-circle"),
            ]
            for title, detail, icon_name in fallback:
                row = self._make_activity_row(icon_name, title, detail, "")
                self.activity_lines.addWidget(row)
            return

        for entry in activities[:6]:
            kind = entry.get("kind", "")
            label = entry.get("label", "")
            meta = entry.get("meta", "")
            ts = entry.get("timestamp")
            ago = format_relative_time(ts) if ts else ""
            icon_name = DELIM_MAP.get(kind, "arrow-right")
            row = self._make_activity_row(icon_name, label, meta, ago)
            self.activity_lines.addWidget(row)

    def _make_activity_row(self, icon_name: str, title: str, detail: str, ago: str) -> QFrame:
        row = QFrame()
        row.setObjectName("ActivityItem")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        dot = QLabel()
        dot.setFixedSize(16, 16)
        dot.setPixmap(lucide_icon(icon_name, 16, TOKENS["goldSoft"]).pixmap(16, 16))
        copy = QVBoxLayout()
        copy.setSpacing(2)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {TOKENS['text']}; font-size: 12.5px;")
        detail_label = QLabel(detail)
        detail_label.setStyleSheet(f"color: {TOKENS['textMute']}; font-size: 11px; font-family: 'JetBrains Mono', monospace;")
        copy.addWidget(title_label)
        copy.addWidget(detail_label)
        row_layout.addWidget(dot, 0, Qt.AlignTop)
        row_layout.addLayout(copy, 1)
        time_label = QLabel(ago)
        time_label.setStyleSheet(f"font-size: 11px; color: {TOKENS['textMute']};")
        row_layout.addWidget(time_label)
        return row
