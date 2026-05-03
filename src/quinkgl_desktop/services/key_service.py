from __future__ import annotations

from pathlib import Path

from quinkgl_desktop.core.cli_adapter import CommandResult, QuinkGLCli


class KeyService:
    def __init__(self, cli: QuinkGLCli) -> None:
        self.cli = cli

    def generate_creator_key(self, workspace: Path, output_name: str = "creator.key") -> CommandResult:
        command = self.cli.build_keygen_command(workspace / output_name)
        return self.cli.run_short(command, workspace)
