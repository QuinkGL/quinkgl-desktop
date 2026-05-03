import os
import sys
from pathlib import Path

from quinkgl_desktop.core.cli_adapter import QuinkGLCli
from quinkgl_desktop.core.models import CliConfig, DirectoryConfig, ManifestConfig, PeerRunConfig, ProjectInitConfig


def test_installed_cli_profile_uses_configured_binary():
    cli = QuinkGLCli(CliConfig(binary="quinkgl-dev"))

    command, env = cli.prepare_command(["info"])

    assert command == ["quinkgl-dev", "info"]
    assert env is None


def test_local_source_cli_profile_uses_python_module_and_pythonpath(tmp_path):
    repo = tmp_path / "QuinkGL"
    (repo / "src").mkdir(parents=True)
    cli = QuinkGLCli(CliConfig(binary="quinkgl", local_source_path=str(repo), python_binary="python3"))

    command, env = cli.prepare_command(["info"])

    assert command == ["python3", "-m", "quinkgl.cli", "info"]
    assert env is not None
    assert str(repo / "src") in env["PYTHONPATH"].split(os.pathsep)


def test_local_source_cli_profile_exists_checks_source_package_not_installed_binary(tmp_path):
    repo = tmp_path / "QuinkGL"
    (repo / "src" / "quinkgl").mkdir(parents=True)
    cli = QuinkGLCli(
        CliConfig(
            binary="definitely-not-installed-quinkgl",
            local_source_path=str(repo),
            python_binary=sys.executable,
        )
    )

    assert cli.exists() is True


def test_local_source_cli_profile_detect_version_uses_python_module_and_env(tmp_path):
    repo = tmp_path / "QuinkGL"
    package = repo / "src" / "quinkgl"
    package.mkdir(parents=True)
    cli_package = package / "cli"
    cli_package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (cli_package / "__init__.py").write_text("", encoding="utf-8")
    (cli_package / "__main__.py").write_text("print('quinkgl 9.8.7')\n", encoding="utf-8")
    cli = QuinkGLCli(
        CliConfig(
            binary="definitely-not-installed-quinkgl",
            local_source_path=str(repo),
            python_binary=sys.executable,
        )
    )

    assert cli.detect_version() == "9.8.7"


def test_run_short_uses_configured_work_dir_when_cwd_is_omitted(tmp_path):
    cli = QuinkGLCli(CliConfig(binary=sys.executable, work_dir=str(tmp_path)))
    command = cli.prepare_command(["-c", "from pathlib import Path; print(Path.cwd())"])[0]

    result = cli.run_short(command)

    assert result.ok
    assert result.stdout.strip() == str(tmp_path)


def test_build_run_command_includes_script_args():
    cli = QuinkGLCli(binary="quinkgl")
    config = PeerRunConfig(
        node_id="peer-1",
        port=7001,
        script_path="peer_script.py",
        rounds=20,
        script_args={"peer_index": "1", "data_root": "./data"},
    )

    command = cli.build_run_command(Path("cifar10-test.qgl"), config)

    assert command[:4] == ["quinkgl", "run", "--manifest", "cifar10-test.qgl"]
    assert "--node-id" in command
    assert "peer-1" in command
    assert "--script-arg" in command
    assert "peer_index=1" in command
    assert "data_root=./data" in command


def test_build_enroll_command_uses_dashboard_url():
    cli = QuinkGLCli(binary="quinkgl")

    command = cli.build_enroll_command(Path("cifar10-test.qgl"), "https://dash.example.com")

    assert command == [
        "quinkgl",
        "telemetry",
        "enroll",
        "cifar10-test.qgl",
        "--dashboard-url",
        "https://dash.example.com",
    ]


def test_build_enroll_command_omits_empty_dashboard_url():
    cli = QuinkGLCli(binary="quinkgl")

    command = cli.build_enroll_command(Path("demo.qgl"), "")

    assert command == ["quinkgl", "telemetry", "enroll", "demo.qgl"]


def test_build_init_command_matches_cli():
    cli = QuinkGLCli()
    command = cli.build_init_command(ProjectInitConfig(output_dir="workspace", template="pytorch-vision", framework="pytorch"))
    assert command == ["quinkgl", "init", "--output-dir", "workspace", "--framework", "pytorch", "--template", "pytorch-vision"]


def test_build_init_command_includes_optional_manifest():
    cli = QuinkGLCli()

    command = cli.build_init_command(ProjectInitConfig(output_dir="workspace", template="minimal", manifest="demo.qgl"))

    assert command == ["quinkgl", "init", "--output-dir", "workspace", "--template", "minimal", "--manifest", "demo.qgl"]


def test_build_status_command_supports_optional_node_and_watch():
    cli = QuinkGLCli()
    assert cli.build_status_command("peer-a", watch=True) == [
        "quinkgl",
        "status",
        "--node-id",
        "peer-a",
        "--watch",
    ]


def test_manifest_create_has_no_zero_hash_fallback():
    cli = QuinkGLCli()
    config = ManifestConfig(name="demo", task_type="class", input_shape="1,28,28", output_shape="10", label_type="integer", model_framework="pytorch", model_arch_hash="", aggregation="FedAvg", topology="AffinityTopology", output_path="demo.qgl")
    command = cli.build_manifest_create_command(config, Path("creator.key"))
    assert "sha256:0000000000000000000000000000000000000000000000000000000000000000" not in command
    assert "--model-arch-hash" not in command


def test_publish_query_discover_match_current_cli_shape():
    cli = QuinkGLCli()
    directory = DirectoryConfig(cache_path="ads.json", fingerprint_path="fp.json", advertisement_output_path="ad.json", tags="vision")

    assert cli.build_directory_publish_command(Path("demo.qgl"), Path("creator.key"), directory) == [
        "quinkgl", "publish", "--manifest", "demo.qgl", "--sign-with", "creator.key", "--tags", "vision", "--output", "ad.json"
    ]
    assert cli.build_directory_query_command(directory) == ["quinkgl", "query", "--cache", "ads.json", "--tags", "vision"]
    assert cli.build_directory_discover_command(directory) == ["quinkgl", "discover", "--cache", "ads.json", "--fingerprint", "fp.json", "--min-affinity", "0.5", "--max-swarms", "1"]


def test_directory_commands_include_optional_and_repeated_flags():
    cli = QuinkGLCli()
    publish_config = DirectoryConfig(
        advertisement_output_path="ad.json",
        reference_fingerprint_path="reference.json",
    )
    query_config = DirectoryConfig(
        cache_path="ads.json",
        tag_filters=["vision", "mnist"],
        input_shape="1,28,28",
        label_type="integer",
        trusted_pubkeys=["ed25519:abc", "ed25519:def"],
    )

    publish_command = cli.build_directory_publish_command(Path("demo.qgl"), Path("creator.key"), publish_config)
    query_command = cli.build_directory_query_command(query_config)

    assert "--reference-fingerprint" in publish_command
    assert publish_command[publish_command.index("--reference-fingerprint") + 1] == "reference.json"
    assert query_command.count("--tag") == 2
    assert "vision" in query_command
    assert "mnist" in query_command
    assert query_command[query_command.index("--input-shape") + 1] == "1,28,28"
    assert query_command[query_command.index("--label-type") + 1] == "integer"
    assert query_command.count("--trusted-pubkey") == 2
    assert "ed25519:abc" in query_command
    assert "ed25519:def" in query_command


def test_run_command_includes_advanced_flags():
    cli = QuinkGLCli()
    config = PeerRunConfig(
        node_id="node-a",
        port=7001,
        script_path="peer_script.py",
        rounds=5,
        trust_policy="pinned",
        script_args={"data_root": "./data"},
        trusted_pubkeys=["ed25519:abc"],
        gossip_interval=2.5,
        stale_round_tolerance=3,
        no_telemetry=True,
        checkpoint_dir="checkpoints",
        resume=True,
        dry_run=True,
    )

    command = cli.build_run_command(Path("demo.qgl"), config)

    assert "--trusted-pubkey" in command
    assert "ed25519:abc" in command
    assert command[command.index("--gossip-interval") + 1] == "2.5"
    assert "--no-telemetry" in command
    assert "--checkpoint-dir" in command
    assert "--resume" in command
    assert "--dry-run" in command


def test_run_command_includes_data_mode_repeated_keys_and_remaining_advanced_flags():
    cli = QuinkGLCli()
    config = PeerRunConfig(
        node_id="node-a",
        port=7001,
        data_path="./data",
        script_path="",
        rounds=5,
        trust_policy="pinned",
        script_args={},
        trusted_pubkeys=["ed25519:abc", "ed25519:def"],
        stale_round_tolerance=3,
        telemetry_secret="secret-token",
        telemetry_heartbeat_interval=7.5,
    )

    command = cli.build_run_command(Path("demo.qgl"), config)

    assert command[command.index("--data") + 1] == "./data"
    assert "--script" not in command
    assert command.count("--trusted-pubkey") == 2
    assert "ed25519:abc" in command
    assert "ed25519:def" in command
    assert command[command.index("--stale-round-tolerance") + 1] == "3"
    assert command[command.index("--telemetry-secret") + 1] == "secret-token"
    assert command[command.index("--telemetry-heartbeat-interval") + 1] == "7.5"
