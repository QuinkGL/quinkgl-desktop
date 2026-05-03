from __future__ import annotations

from pathlib import Path

from quinkgl_desktop.core.cli_adapter import CommandResult, QuinkGLCli
from quinkgl_desktop.core.models import ProjectInitConfig


class ProjectInitService:
    def __init__(self, cli: QuinkGLCli) -> None:
        self.cli = cli

    def init_project(self, cwd: Path, config: ProjectInitConfig) -> CommandResult:
        command = self.cli.build_init_command(config)
        return self.cli.run_short(command, cwd)
