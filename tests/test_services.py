from pathlib import Path

from quinkgl_desktop.core.cli_adapter import CommandResult
from quinkgl_desktop.core.models import DirectoryConfig, ProjectConfig, ProjectInitConfig
from quinkgl_desktop.services.directory_service import DirectoryService
from quinkgl_desktop.services.hash_service import HashService
from quinkgl_desktop.services.project_init_service import ProjectInitService
from quinkgl_desktop.services.status_service import StatusService
from quinkgl_desktop.services.telemetry_service import TelemetryService


class FakeCli:
    def __init__(self):
        self.commands = []

    def build_enroll_command(self, manifest: Path, dashboard_url: str) -> list[str]:
        return ["quinkgl", "telemetry", "enroll", str(manifest), "--dashboard-url", dashboard_url]

    def run_short(self, command: list[str], cwd: Path) -> CommandResult:
        self.commands.append((command, cwd))
        return CommandResult(command=command, exit_code=0, stdout="wrote: demo.telemetry.qglkey\n", stderr="")


class ServiceFakeCli(FakeCli):
    def build_init_command(self, config: ProjectInitConfig) -> list[str]:
        return ["quinkgl", "init", "--output-dir", config.output_dir, "--template", config.template]

    def build_status_command(self, node_id: str = "", watch: bool = False) -> list[str]:
        command = ["quinkgl", "status"]
        if node_id:
            command.extend(["--node-id", node_id])
        if watch:
            command.append("--watch")
        return command

    def build_info_command(self) -> list[str]:
        return ["quinkgl", "info"]

    def build_directory_publish_command(
        self,
        manifest: Path,
        creator_key: Path,
        config: DirectoryConfig,
    ) -> list[str]:
        return [
            "quinkgl",
            "publish",
            "--manifest",
            str(manifest),
            "--sign-with",
            str(creator_key),
            "--output",
            config.advertisement_output_path,
        ]


def test_telemetry_service_enrolls_manifest(tmp_path):
    manifest = tmp_path / "demo.qgl"
    manifest.write_text("{}", encoding="utf-8")
    config = ProjectConfig(
        workspace_path=str(tmp_path),
        manifest_path="demo.qgl",
        dashboard_url="https://dash.example.com",
    )
    service = TelemetryService(cli=FakeCli())

    result = service.enroll(config)

    assert result.exit_code == 0
    assert result.command[0:3] == ["quinkgl", "telemetry", "enroll"]


def test_hash_service_returns_sha256_prefixed_digest(tmp_path):
    path = tmp_path / "model.py"
    path.write_text("model", encoding="utf-8")

    digest = HashService().sha256_file(path)

    assert digest.startswith("sha256:")
    assert len(digest) == len("sha256:") + 64


def test_project_init_service_runs_init(tmp_path):
    cli = ServiceFakeCli()
    service = ProjectInitService(cli)
    result = service.init_project(tmp_path, ProjectInitConfig(output_dir=str(tmp_path), template="minimal"))
    assert result.ok is True
    assert result.command[:3] == ["quinkgl", "init", "--output-dir"]


def test_status_service_runs_status(tmp_path):
    cli = ServiceFakeCli()
    service = StatusService(cli)
    result = service.status(tmp_path, node_id="peer-a")
    assert result.command == ["quinkgl", "status", "--node-id", "peer-a"]


def test_status_service_rejects_watch_mode_for_short_run(tmp_path):
    import pytest

    service = StatusService(ServiceFakeCli())
    with pytest.raises(ValueError, match="watch status requires"):
        service.status(tmp_path, watch=True)


def test_directory_service_publish_uses_project_paths(tmp_path):
    cli = ServiceFakeCli()
    config = ProjectConfig(workspace_path=str(tmp_path), manifest_path="demo.qgl", creator_key_path="creator.key")
    config.directory = DirectoryConfig(advertisement_output_path="ad.json")
    service = DirectoryService(cli)
    result = service.publish(config)
    assert result.command == [
        "quinkgl",
        "publish",
        "--manifest",
        str(tmp_path / "demo.qgl"),
        "--sign-with",
        str(tmp_path / "creator.key"),
        "--output",
        "ad.json",
    ]
