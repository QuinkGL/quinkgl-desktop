from __future__ import annotations

from dataclasses import dataclass
from typing import Type

from PySide6.QtWidgets import QWidget

from quinkgl_desktop.ui.i18n import PAGES_COPY


@dataclass(frozen=True, slots=True)
class PageSpec:
    key: str
    label: str
    icon: str
    hint: str
    component_name: str
    requires_project: bool = True


PAGES = [
    PageSpec("home", "Home", "home", "Projects", "ProjectPickerPage", False),
    PageSpec("overview", PAGES_COPY["overview"]["label"], "layout-grid", PAGES_COPY["overview"]["hint"], "OverviewPage"),
    PageSpec("wizard", PAGES_COPY["wizard"]["label"], "wand-2", PAGES_COPY["wizard"]["hint"], "WizardPage"),
    PageSpec("manifest", PAGES_COPY["manifest"]["label"], "file-cog", PAGES_COPY["manifest"]["hint"], "ManifestPage"),
    PageSpec("telemetry", PAGES_COPY["telemetry"]["label"], "radio", PAGES_COPY["telemetry"]["hint"], "TelemetryPage"),
    PageSpec("run", PAGES_COPY["run"]["label"], "play-circle", PAGES_COPY["run"]["hint"], "RunPeerPage"),
    PageSpec("logs", PAGES_COPY["logs"]["label"], "terminal", PAGES_COPY["logs"]["hint"], "LogsPage"),
    PageSpec("settings", PAGES_COPY["settings"]["label"], "settings", PAGES_COPY["settings"]["hint"], "SettingsPage", False),
]

PAGE_BY_KEY = {page.key: page for page in PAGES}
PAGE_KEY_BY_LABEL = {page.label: page.key for page in PAGES}
PAGE_LABELS = [page.label for page in PAGES]


class Navigator:
    def __init__(self, set_page) -> None:
        self._set_page = set_page

    def go(self, page_key: str) -> None:
        if page_key in PAGE_BY_KEY:
            self._set_page(page_key)
