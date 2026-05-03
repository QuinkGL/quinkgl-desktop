from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


Runner = Callable[[list[str], Path, dict[str, str] | None], tuple[int, str, str]]


@dataclass(slots=True)
class PresetInstallResult:
    preset: str
    installed: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return bool(self.installed)


@dataclass(slots=True)
class PresetHashResult:
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str
    hash_value: str = ""

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and bool(self.hash_value)


class ModelPresetService:
    def __init__(self, runner: Runner | None = None) -> None:
        self.runner = runner or self._run_subprocess

    def install_preset(self, preset: str, workspace: Path) -> PresetInstallResult:
        source = self._preset_dir(preset)
        if not source.exists():
            raise ValueError(f"Unknown model preset: {preset}")

        workspace.mkdir(parents=True, exist_ok=True)
        result = PresetInstallResult(preset=preset)
        for name in ("peer_script.py", "compute_hash.py"):
            target = workspace / name
            if target.exists():
                backup = self._backup_path(target)
                target.replace(backup)
                result.installed[name] = "backed-up"
            target.write_text((source / name).read_text(encoding="utf-8"), encoding="utf-8")
            result.installed.setdefault(name, "written")
        return result

    def _backup_path(self, target: Path) -> Path:
        backup = target.with_name(f"{target.name}.bak")
        index = 1
        while backup.exists():
            backup = target.with_name(f"{target.name}.bak{index}")
            index += 1
        return backup

    def compute_hash(
        self,
        workspace: Path,
        python_binary: str = "python",
        env: dict[str, str] | None = None,
    ) -> PresetHashResult:
        command = [python_binary or "python", "compute_hash.py"]
        exit_code, stdout, stderr = self.runner(command, workspace, env)
        return PresetHashResult(
            command=command,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            hash_value=self._extract_hash(stdout + "\n" + stderr),
        )

    def _preset_dir(self, preset: str) -> Path:
        return Path(__file__).resolve().parents[1] / "resources" / "model_presets" / preset

    def _extract_hash(self, output: str) -> str:
        match = re.search(r"sha256:[0-9a-fA-F]{64}", output)
        return match.group(0) if match else ""

    def _run_subprocess(self, command: list[str], cwd: Path, env: dict[str, str] | None) -> tuple[int, str, str]:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        return completed.returncode, completed.stdout, completed.stderr
