from quinkgl_desktop.core.artifact_resolver import ProjectArtifacts
from quinkgl_desktop.core.models import ProjectConfig


def test_artifact_status_detects_project_files(tmp_path):
    (tmp_path / "creator.key").write_text("secret", encoding="utf-8")
    (tmp_path / "demo.qgl").write_text("manifest", encoding="utf-8")
    (tmp_path / "demo.telemetry.qglkey").write_text("key", encoding="utf-8")

    artifacts = ProjectArtifacts.from_workspace(tmp_path)

    assert artifacts.creator_key_ready is True
    assert artifacts.manifest_path.name == "demo.qgl"
    assert artifacts.telemetry_key_path.name == "demo.telemetry.qglkey"
    assert artifacts.telemetry_ready is True


def test_artifacts_resolve_from_project_config_paths(tmp_path):
    (tmp_path / "keys").mkdir()
    (tmp_path / "keys" / "creator.pem").write_text("secret", encoding="utf-8")
    (tmp_path / "custom.qgl").write_text("{}", encoding="utf-8")
    (tmp_path / "custom.telemetry.qglkey").write_text("{}", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "peer.py").write_text("", encoding="utf-8")
    config = ProjectConfig(
        workspace_path=str(tmp_path),
        creator_key_path="keys/creator.pem",
        manifest_path="custom.qgl",
        telemetry_key_path="custom.telemetry.qglkey",
    )
    config.peer.script_path = "src/peer.py"

    artifacts = ProjectArtifacts.from_config(config)

    assert artifacts.creator_key_ready is True
    assert artifacts.manifest_ready is True
    assert artifacts.telemetry_ready is True
    assert artifacts.script_ready is True


def test_artifacts_from_config_omits_missing_configured_paths(tmp_path):
    config = ProjectConfig(
        workspace_path=str(tmp_path),
        creator_key_path="missing.key",
        manifest_path="missing.qgl",
        telemetry_key_path="missing.qglkey",
    )
    config.peer.script_path = "missing.py"

    artifacts = ProjectArtifacts.from_config(config)

    assert artifacts.creator_key_path is None
    assert artifacts.manifest_path is None
    assert artifacts.telemetry_key_path is None
    assert artifacts.script_path is None
