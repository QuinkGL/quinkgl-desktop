from __future__ import annotations

from pathlib import Path

from quinkgl_desktop.core.cli_adapter import CommandResult, QuinkGLCli
from quinkgl_desktop.core.models import ProjectConfig


class ManifestService:
    def __init__(self, cli: QuinkGLCli) -> None:
        self.cli = cli

    def create_manifest(self, config: ProjectConfig) -> CommandResult:
        workspace = Path(config.workspace_path)
        creator_key = workspace / config.creator_key_path
        command = self.cli.build_manifest_create_command(config.manifest, creator_key)
        return self.cli.run_short(command, workspace)

    def show_manifest(self, config: ProjectConfig) -> CommandResult:
        workspace = Path(config.workspace_path)
        manifest = workspace / config.manifest_path
        command = self.cli.build_manifest_show_command(manifest)
        return self.cli.run_short(command, workspace)

    def verify_manifest(self, config: ProjectConfig) -> CommandResult:
        workspace = Path(config.workspace_path)
        manifest = workspace / config.manifest_path
        command = self.cli.build_manifest_verify_command(manifest)
        return self.cli.run_short(command, workspace)

    def magnet_manifest(self, config: ProjectConfig) -> CommandResult:
        workspace = Path(config.workspace_path)
        manifest = workspace / config.manifest_path
        command = self.cli.build_manifest_magnet_command(manifest)
        return self.cli.run_short(command, workspace)
