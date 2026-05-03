from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from quinkgl_desktop.core.models import ProjectConfig


@dataclass(slots=True)
class ProjectArtifacts:
    workspace: Path
    creator_key_path: Path | None
    manifest_path: Path | None
    telemetry_key_path: Path | None
    script_path: Path | None

    @property
    def creator_key_ready(self) -> bool:
        return bool(self.creator_key_path and self.creator_key_path.exists())

    @property
    def manifest_ready(self) -> bool:
        return bool(self.manifest_path and self.manifest_path.exists())

    @property
    def telemetry_ready(self) -> bool:
        return bool(self.telemetry_key_path and self.telemetry_key_path.exists())

    @property
    def script_ready(self) -> bool:
        return bool(self.script_path and self.script_path.exists())

    @classmethod
    def from_config(cls, config: ProjectConfig) -> "ProjectArtifacts":
        root = config.workspace

        def artifact_path(value: str) -> Path | None:
            if not value:
                return None
            path = (root / value).expanduser().resolve()
            return path if path.exists() else None

        return cls(
            workspace=root,
            creator_key_path=artifact_path(config.creator_key_path),
            manifest_path=artifact_path(config.manifest_path),
            telemetry_key_path=artifact_path(config.telemetry_key_path),
            script_path=artifact_path(config.peer.script_path),
        )

    @classmethod
    def from_workspace(cls, workspace: str | Path) -> "ProjectArtifacts":
        root = Path(workspace).expanduser().resolve()
        creator = root / "creator.key"
        script = root / "peer_script.py"
        manifests = sorted(root.glob("*.qgl"))
        telemetry_keys = sorted(root.glob("*.telemetry.qglkey"))
        return cls(
            workspace=root,
            creator_key_path=creator if creator.exists() else None,
            manifest_path=manifests[0] if manifests else None,
            telemetry_key_path=telemetry_keys[0] if telemetry_keys else None,
            script_path=script if script.exists() else None,
        )
