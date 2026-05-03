from __future__ import annotations

from pathlib import Path

from quinkgl_desktop.core.cli_adapter import CommandResult, QuinkGLCli
from quinkgl_desktop.core.models import ProjectConfig


class DirectoryService:
    def __init__(self, cli: QuinkGLCli) -> None:
        self.cli = cli

    def publish(self, config: ProjectConfig) -> CommandResult:
        workspace = Path(config.workspace_path)
        command = self.cli.build_directory_publish_command(
            workspace / config.manifest_path,
            workspace / config.creator_key_path,
            config.directory,
        )
        return self.cli.run_short(command, workspace)

    def query(self, config: ProjectConfig) -> CommandResult:
        workspace = Path(config.workspace_path)
        command = self.cli.build_directory_query_command(config.directory)
        return self.cli.run_short(command, workspace)

    def discover(self, config: ProjectConfig) -> CommandResult:
        workspace = Path(config.workspace_path)
        command = self.cli.build_directory_discover_command(config.directory)
        return self.cli.run_short(command, workspace)
