from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from quinkgl_desktop.core.models import CliConfig, DirectoryConfig, ManifestConfig, PeerRunConfig, ProjectConfig, ProjectInitConfig


def _model(cls, raw: dict):
    allowed = cls.__dataclass_fields__
    return cls(**{key: value for key, value in raw.items() if key in allowed})


class ProjectStore:
    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace).expanduser().resolve()
        self.state_dir = self.workspace / ".quinkgl-desktop"
        self.path = self.state_dir / "project.json"

    def save(self, config: ProjectConfig) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")

    def load(self) -> ProjectConfig:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        cli_data = data.pop("cli", {})
        directory_data = data.pop("directory", {})
        init_data = data.pop("init", {})
        peer_data = data.pop("peer", {})
        manifest_data = data.pop("manifest", {})
        return ProjectConfig(
            **data,
            cli=_model(CliConfig, cli_data),
            directory=_model(DirectoryConfig, directory_data),
            init=_model(ProjectInitConfig, init_data),
            manifest=_model(ManifestConfig, manifest_data),
            peer=_model(PeerRunConfig, peer_data),
        )
