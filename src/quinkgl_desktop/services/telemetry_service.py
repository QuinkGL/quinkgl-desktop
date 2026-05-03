from __future__ import annotations

from pathlib import Path

from quinkgl_desktop.core.cli_adapter import CommandResult, QuinkGLCli
from quinkgl_desktop.core.models import ProjectConfig


class TelemetryService:
    def __init__(self, cli: QuinkGLCli) -> None:
        self.cli = cli

    def enroll(self, config: ProjectConfig) -> CommandResult:
        workspace = Path(config.workspace_path)
        manifest = workspace / config.manifest_path
        command = self.cli.build_enroll_command(manifest, config.dashboard_url)
        return self.cli.run_short(command, workspace)

    def dashboard_code(self, config: ProjectConfig) -> CommandResult:
        workspace = Path(config.workspace_path)
        manifest = workspace / config.manifest_path
        command = self.cli.build_dashboard_code_command(manifest, config.peer.node_id)
        return self.cli.run_short(command, workspace)
