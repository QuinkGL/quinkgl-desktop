from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from quinkgl_desktop.core.recent_projects_store import load_recent_projects
from quinkgl_desktop.ui.i18n import OVERVIEW_COPY, PAGES_COPY, SETTINGS_COPY
from quinkgl_desktop.ui.icons import lucide_icon
from quinkgl_desktop.ui.nav import PAGES
from quinkgl_desktop.ui.settings_nav import SETTINGS_SECTIONS
from quinkgl_desktop.ui.tokens import TOKENS


@dataclass
class SearchItem:
    id: str
    label: str
    description: str = ""
    icon: str = "search"
    action: str = ""
    action_type: str = "page"


def _build_index() -> list[SearchItem]:
    items: list[SearchItem] = []

    for page in PAGES:
        copy = PAGES_COPY.get(page.key, {})
        subtitle = copy.get("subtitle", "") if isinstance(copy, dict) else ""
        items.append(
            SearchItem(
                id=f"page-{page.key}",
                label=page.label,
                description=subtitle,
                icon=page.icon,
                action=page.key,
                action_type="page",
            )
        )

    for item in OVERVIEW_COPY["quick_items"]:
        page, title, desc = item
        icon_map = {
            "wizard": "wand-2",
            "manifest": "file-code-2",
            "telemetry": "antenna",
            "logs": "terminal",
        }
        items.append(
            SearchItem(
                id=f"quick-{page}",
                label=title,
                description=desc,
                icon=icon_map.get(page, "arrow-right"),
                action=page,
                action_type="page",
            )
        )

    for step in OVERVIEW_COPY["readiness"]:
        title, desc, page = step
        items.append(
            SearchItem(
                id=f"step-{page}",
                label=title,
                description=desc,
                icon="shield-check",
                action=page,
                action_type="page",
            )
        )

    for section in SETTINGS_SECTIONS:
        items.append(
            SearchItem(
                id=f"settings-{section.key}",
                label=f"Settings \u203a {section.label}",
                icon=section.icon,
                action=section.key,
                action_type="settings_section",
            )
        )

    settings_entries = [
        ("Binary path", "Path or alias for the quinkgl binary"),
        ("Default port", "Default port for peer"),
        ("Default projects folder", "Used by Create Project"),
        ("Run logs retention", "Days to keep logs"),
        ("Verbose logging", "Include debug-level lines in console"),
        ("Strict trust policy", "Reject unknown peer keys"),
        ("Auto-start last peer", "Resume the previous run on app open"),
        ("Usage analytics", "Send anonymous usage analytics"),
        ("Check for updates", "Notify when a new desktop version ships"),
    ]
    for label, desc in settings_entries:
        items.append(
            SearchItem(
                id=f"setting-{label.lower().replace(' ', '-')}",
                label=label,
                description=desc,
                icon="settings",
                action="settings",
                action_type="page",
            )
        )

    label_entries = [
        ("Launch Peer", "Start a QuinkGL peer process", "play-circle", "run"),
        ("Continue setup", "Step through the wizard", "wand-2", "wizard"),
        ("Creator key", "Generate or load creator.key", "key-round", "manifest"),
        ("Quickstart Guide", "Five minutes from empty folder to a running peer", "book-open", "home"),
        ("What is QuinkGL?", "Federated learning framework", "graduation-cap", "home"),
        ("Change Project", "Open a different workspace", "folder-input", "home"),
    ]
    for label, desc, icon, page in label_entries:
        items.append(
            SearchItem(
                id=f"label-{label.lower().replace(' ', '-')}",
                label=label,
                description=desc,
                icon=icon,
                action=page,
                action_type="page",
            )
        )

    try:
        recent = load_recent_projects()
        for proj in recent[:5]:
            name = proj.get("name", proj.get("path", ""))
            path = proj.get("path", "")
            items.append(
                SearchItem(
                    id=f"project-{path}",
                    label=name,
                    description=path,
                    icon="folder-open",
                    action=path,
                    action_type="project",
                )
            )
    except Exception:
        pass

    return items


class SearchPopup(QFrame):
    result_selected = Signal(str, str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SearchPopup")
        self.setFixedWidth(520)
        self._all_items: list[SearchItem] = _build_index()
        self._filtered: list[SearchItem] = []
        self._selected_index: int = -1
        self._result_widgets: list[QFrame] = []
        self.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(1)

        self._results_layout = QVBoxLayout()
        self._results_layout.setSpacing(1)
        layout.addLayout(self._results_layout)

        self._empty_label = QLabel("No results found")
        self._empty_label.setStyleSheet(
            f"color: {TOKENS['textMute']}; font-size: 13px; padding: 20px 16px;"
        )
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.hide()
        layout.addWidget(self._empty_label)

        self.setStyleSheet(f"""
            QFrame#SearchPopup {{
                background: {TOKENS['panel']};
                border: 1px solid {TOKENS['borderMid']};
                border-radius: 12px;
            }}
        """)

    def filter(self, query: str) -> None:
        q = query.strip().lower()
        if not q:
            self.hide()
            return
        self._filtered = [
            item
            for item in self._all_items
            if q in item.label.lower() or q in item.description.lower()
        ][:8]
        self._selected_index = 0 if self._filtered else -1
        self._rebuild_results()

    def _rebuild_results(self) -> None:
        for w in self._result_widgets:
            w.setParent(None)
            w.deleteLater()
        self._result_widgets.clear()

        if not self._filtered:
            self._empty_label.show()
            self.setFixedHeight(60)
            return

        self._empty_label.hide()

        for idx, item in enumerate(self._filtered):
            row = QFrame()
            row.setCursor(Qt.PointingHandCursor)
            row.setFixedHeight(52)
            row.setStyleSheet("QFrame { background: transparent; border: none; border-radius: 8px; }")

            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 0, 10, 0)
            row_layout.setSpacing(10)

            icon_label = QLabel()
            icon_label.setFixedSize(16, 16)
            icon_label.setPixmap(lucide_icon(item.icon, 16, TOKENS["textDim"]).pixmap(16, 16))
            row_layout.addWidget(icon_label, 0, Qt.AlignVCenter)

            text_col = QVBoxLayout()
            text_col.setSpacing(1)

            title_label = QLabel(item.label)
            title_label.setStyleSheet(f"font-size: 13.5px; color: {TOKENS['text']}; font-weight: 600;")
            text_col.addWidget(title_label)

            if item.description:
                desc_label = QLabel(item.description)
                desc_label.setStyleSheet(f"font-size: 11.5px; color: {TOKENS['textDim']};")
                text_col.addWidget(desc_label)

            row_layout.addLayout(text_col, 1)

            row.mousePressEvent = lambda event, item=item: self._select_item(item)
            self._result_widgets.append(row)
            self._results_layout.addWidget(row)

        self._update_highlight()
        height = 12 + len(self._result_widgets) * 52
        self.setFixedHeight(min(height, 400))

    def _update_highlight(self) -> None:
        for i, row in enumerate(self._result_widgets):
            if i == self._selected_index:
                row.setStyleSheet(f"""
                    QFrame {{
                        background: {TOKENS['panelHover']};
                        border: none;
                        border-radius: 8px;
                    }}
                """)
            else:
                row.setStyleSheet("QFrame { background: transparent; border: none; border-radius: 8px; }")

    def _select_item(self, item: SearchItem) -> None:
        self.result_selected.emit(item.action, item.action_type)
        self.hide()

    def select_next(self) -> None:
        if not self._filtered:
            return
        self._selected_index = (self._selected_index + 1) % len(self._filtered)
        self._update_highlight()

    def select_previous(self) -> None:
        if not self._filtered:
            return
        self._selected_index = (self._selected_index - 1) % len(self._filtered)
        self._update_highlight()

    def select_current(self) -> None:
        if 0 <= self._selected_index < len(self._filtered):
            self._select_item(self._filtered[self._selected_index])
