from __future__ import annotations

from pathlib import Path

from quinkgl_desktop.core.cli_adapter import CommandResult, QuinkGLCli


class StatusService:
    def __init__(self, cli: QuinkGLCli) -> None:
        self.cli = cli

    def status(self, cwd: Path, node_id: str = "", watch: bool = False) -> CommandResult:
        if watch:
            raise ValueError("watch status requires a long-running process manager")
        command = self.cli.build_status_command(node_id=node_id, watch=watch)
        return self.cli.run_short(command, cwd)

    def info(self, cwd: Path) -> CommandResult:
        command = self.cli.build_info_command()
        return self.cli.run_short(command, cwd)
