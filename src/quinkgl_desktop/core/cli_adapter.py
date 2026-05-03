from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from quinkgl_desktop.core.models import CliConfig, DirectoryConfig, ManifestConfig, PeerRunConfig, ProjectInitConfig


@dataclass(slots=True)
class CommandResult:
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


class QuinkGLCli:
    def __init__(self, config: CliConfig | None = None, binary: str | None = None) -> None:
        self.config = config or CliConfig(binary=binary or "quinkgl")
        self.binary = self.config.binary

    def prepare_command(self, args: list[str]) -> tuple[list[str], dict[str, str] | None]:
        local_source = self.config.local_source_path.strip()
        if not local_source:
            return [self.config.binary, *args], None

        src_path = str((Path(local_source).expanduser().resolve() / "src"))
        env = dict(os.environ)
        current = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = src_path if not current else f"{src_path}{os.pathsep}{current}"
        return [self.config.python_binary, "-m", "quinkgl.cli", *args], env

    def _cmd(self, args: list[str]) -> list[str]:
        command, _env = self.prepare_command(args)
        return command

    def exists(self) -> bool:
        local_source = self.config.local_source_path.strip()
        if local_source:
            package_path = Path(local_source).expanduser().resolve() / "src" / "quinkgl"
            return package_path.exists() and shutil.which(self.config.python_binary) is not None
        return shutil.which(self.binary) is not None

    def detect_version(self) -> str | None:
        """Return the installed CLI version string, or None if not found."""
        if not self.exists():
            return None
        try:
            command, env = self.prepare_command(["--version"])
            result = subprocess.run(
                command,
                env=env,
                text=True,
                capture_output=True,
                check=False,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip().replace("quinkgl ", "")
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # keygen
    # ------------------------------------------------------------------
    def build_keygen_command(self, output: Path) -> list[str]:
        return self._cmd(["keygen", "--output", str(output)])

    # ------------------------------------------------------------------
    # init
    # ------------------------------------------------------------------
    def build_init_command(self, config: ProjectInitConfig) -> list[str]:
        args = ["init", "--output-dir", config.output_dir]
        if config.framework:
            args.extend(["--framework", config.framework])
        args.extend(["--template", config.template])
        if config.manifest:
            args.extend(["--manifest", config.manifest])
        return self._cmd(args)

    # ------------------------------------------------------------------
    # manifest
    # ------------------------------------------------------------------
    def build_manifest_create_command(self, config: ManifestConfig, creator_key: Path) -> list[str]:
        args = [
            "manifest",
            "create",
            "--name",
            config.name,
            "--task-type",
            config.task_type,
            "--input-shape",
            config.input_shape,
            "--output-shape",
            config.output_shape,
            "--label-type",
            config.label_type,
            "--model-framework",
            config.model_framework,
        ]
        if config.model_arch_hash:
            args.extend(["--model-arch-hash", config.model_arch_hash])
        args.extend([
            "--aggregation",
            config.aggregation,
            "--topology",
            config.topology,
            "--sign-with",
            str(creator_key),
            "--output",
            config.output_path,
        ])
        return self._cmd(args)

    def build_manifest_show_command(self, manifest: Path) -> list[str]:
        return self._cmd(["manifest", "show", str(manifest)])

    def build_manifest_verify_command(self, manifest: Path) -> list[str]:
        return self._cmd(["manifest", "verify", str(manifest)])

    def build_manifest_magnet_command(self, manifest: Path) -> list[str]:
        return self._cmd(["manifest", "magnet", str(manifest)])

    # ------------------------------------------------------------------
    # telemetry
    # ------------------------------------------------------------------
    def build_enroll_command(self, manifest: Path, dashboard_url: str) -> list[str]:
        args = [
            "telemetry",
            "enroll",
            str(manifest),
        ]
        if dashboard_url:
            args.extend(["--dashboard-url", dashboard_url])
        return self._cmd(args)

    def build_dashboard_code_command(self, manifest: Path, node_id: str) -> list[str]:
        return self._cmd([
            "telemetry",
            "dashboard-code",
            str(manifest),
            "--node-id",
            node_id,
        ])

    # ------------------------------------------------------------------
    # run
    # ------------------------------------------------------------------
    def build_run_command(self, manifest: Path, config: PeerRunConfig) -> list[str]:
        args = [
            "run",
            "--manifest",
            str(manifest),
        ]
        if config.data_path:
            args.extend(["--data", config.data_path])
        if config.script_path:
            args.extend(["--script", config.script_path])
        args.extend([
            "--node-id",
            config.node_id,
            "--port",
            str(config.port),
            "--trust-policy",
            config.trust_policy,
            "--rounds",
            str(config.rounds),
        ])
        for key, value in config.script_args.items():
            args.extend(["--script-arg", f"{key}={value}"])
        for pubkey in config.trusted_pubkeys:
            args.extend(["--trusted-pubkey", pubkey])
        if config.gossip_interval is not None:
            args.extend(["--gossip-interval", str(config.gossip_interval)])
        if config.stale_round_tolerance is not None:
            args.extend(["--stale-round-tolerance", str(config.stale_round_tolerance)])
        if config.no_telemetry:
            args.append("--no-telemetry")
        if config.telemetry_secret:
            args.extend(["--telemetry-secret", config.telemetry_secret])
        if config.telemetry_heartbeat_interval != 5.0:
            args.extend(["--telemetry-heartbeat-interval", str(config.telemetry_heartbeat_interval)])
        if config.checkpoint_dir:
            args.extend(["--checkpoint-dir", config.checkpoint_dir])
        if config.resume:
            args.append("--resume")
        if config.dry_run:
            args.append("--dry-run")
        return self._cmd(args)

    # ------------------------------------------------------------------
    # status / info
    # ------------------------------------------------------------------
    def build_status_command(self, node_id: str = "", watch: bool = False) -> list[str]:
        args = ["status"]
        if node_id:
            args.extend(["--node-id", node_id])
        if watch:
            args.append("--watch")
        return self._cmd(args)

    def build_info_command(self) -> list[str]:
        return self._cmd(["info"])

    # ------------------------------------------------------------------
    # directory
    # ------------------------------------------------------------------
    def build_directory_publish_command(self, manifest: Path, creator_key: Path, config: DirectoryConfig) -> list[str]:
        args = ["publish", "--manifest", str(manifest), "--sign-with", str(creator_key)]
        if config.reference_fingerprint_path:
            args.extend(["--reference-fingerprint", config.reference_fingerprint_path])
        if config.tags:
            args.extend(["--tags", config.tags])
        args.extend(["--output", config.advertisement_output_path])
        return self._cmd(args)

    def build_directory_query_command(self, config: DirectoryConfig) -> list[str]:
        args = ["query", "--cache", config.cache_path]
        for tag in config.tag_filters:
            args.extend(["--tag", tag])
        if config.tags:
            args.extend(["--tags", config.tags])
        if config.input_shape:
            args.extend(["--input-shape", config.input_shape])
        if config.label_type:
            args.extend(["--label-type", config.label_type])
        for pubkey in config.trusted_pubkeys:
            args.extend(["--trusted-pubkey", pubkey])
        return self._cmd(args)

    def build_directory_discover_command(self, config: DirectoryConfig) -> list[str]:
        return self._cmd([
            "discover",
            "--cache",
            config.cache_path,
            "--fingerprint",
            config.fingerprint_path,
            "--min-affinity",
            str(config.min_affinity),
            "--max-swarms",
            str(config.max_swarms),
        ])

    # ------------------------------------------------------------------
    # execution
    # ------------------------------------------------------------------
    def run_short(self, command: list[str], cwd: Path | None = None) -> CommandResult:
        _command, env = self.prepare_command([])
        work_dir = self.config.work_dir.strip()
        if cwd is not None:
            run_cwd = cwd
        elif work_dir:
            run_cwd = Path(work_dir).expanduser().resolve()
        else:
            run_cwd = Path.cwd()
        completed = subprocess.run(
            command,
            cwd=run_cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        return CommandResult(
            command=command,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
