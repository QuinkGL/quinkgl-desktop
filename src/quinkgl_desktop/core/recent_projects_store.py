from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths


def _config_dir() -> Path:
    location = QStandardPaths.writableLocation(QStandardPaths.ConfigLocation)
    if not location:
        location = str(Path.home())
    return Path(location) / "quinkgl-desktop"


def load_recent_projects() -> list[dict[str, str]]:
    path = _config_dir() / "recent_projects.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_recent_projects(projects: list[dict[str, str]]) -> None:
    config_dir = _config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    path = config_dir / "recent_projects.json"
    path.write_text(json.dumps(projects, indent=2), encoding="utf-8")
