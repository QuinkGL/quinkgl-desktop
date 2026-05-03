from __future__ import annotations

from pathlib import Path

from quinkgl_desktop.core.cli_adapter import QuinkGLCli
from quinkgl_desktop.core.models import ProjectConfig


class PeerRunService:
    def __init__(self, cli: QuinkGLCli) -> None:
        self.cli = cli

    def build_command(self, config: ProjectConfig) -> list[str]:
        workspace = Path(config.workspace_path)
        manifest = workspace / config.manifest_path
        return self.cli.build_run_command(manifest, config.peer)

    def build_environment(self) -> dict[str, str] | None:
        _command, env = self.cli.prepare_command([])
        return env
