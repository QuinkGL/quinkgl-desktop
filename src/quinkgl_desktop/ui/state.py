from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from quinkgl_desktop.ui.nav import PAGES
from quinkgl_desktop.ui.tokens import PeerState


@dataclass(slots=True)
class AppState:
    app_version: str = "0.1"
    page: str = PAGES[0].key
    project_name: str = ""
    peer_state: PeerState = PeerState.STOPPED
    readiness: dict[str, bool] = field(default_factory=lambda: {"creator": False, "manifest": False, "telemetry": False})
    dashboard_code: str = ""

    # Prototype state fields
    wizard_step: int = 0
    wizard_completed: list[int] = field(default_factory=list)
    manifest_mode: str = "basic"
    run_peer_mode: str = "basic"
    manifest_preview: str = "cli"
    log_filter: str = "all"
    log_paused: bool = False
    log_search: str = ""
    activity: list[dict] = field(default_factory=list)

    @property
    def readiness_done(self) -> int:
        return sum(1 for ready in self.readiness.values() if ready)

    @property
    def readiness_total(self) -> int:
        return len(self.readiness)

    @property
    def setup_complete(self) -> bool:
        return self.readiness_done == self.readiness_total

    def set_page(self, page: str) -> None:
        self.page = page

    def set_wizard_step(self, step: int) -> None:
        self.wizard_step = step

    def mark_wizard_complete(self, step: int) -> None:
        if step not in self.wizard_completed:
            self.wizard_completed.append(step)

    def add_activity(self, kind: str, label: str, meta: str = "") -> None:
        self.activity.insert(0, {"kind": kind, "label": label, "meta": meta, "timestamp": datetime.now()})
        self.activity = self.activity[:20]
