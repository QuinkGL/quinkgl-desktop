from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


PeerStatus = Literal["stopped", "running", "failed"]


@dataclass(slots=True)
class PeerRunConfig:
    node_id: str = "peer-1"
    port: int = 7001
    data_path: str = ""
    script_path: str = "peer_script.py"
    rounds: int = 20
    trust_policy: str = "tofu"
    script_args: dict[str, str] = field(
        default_factory=lambda: {
            "peer_index": "1",
            "data_root": "./data",
        }
    )
    trusted_pubkeys: list[str] = field(default_factory=list)
    gossip_interval: float | None = None
    stale_round_tolerance: int | None = None
    no_telemetry: bool = False
    telemetry_secret: str = ""
    telemetry_heartbeat_interval: float = 5.0
    checkpoint_dir: str = ""
    resume: bool = False
    dry_run: bool = False


@dataclass(slots=True)
class ProjectInitConfig:
    output_dir: str = ""
    template: str = "minimal"
    framework: str = ""
    manifest: str = ""


@dataclass(slots=True)
class DirectoryConfig:
    cache_path: str = ""
    fingerprint_path: str = ""
    advertisement_output_path: str = "swarm-advertisement.json"
    reference_fingerprint_path: str = ""
    tags: str = ""
    tag_filters: list[str] = field(default_factory=list)
    input_shape: str = ""
    label_type: str = ""
    trusted_pubkeys: list[str] = field(default_factory=list)
    min_affinity: float = 0.5
    max_swarms: int = 1


@dataclass(slots=True)
class ManifestConfig:
    name: str = "custom-swarm"
    task_type: str = "class"
    input_shape: str = "3,32,32"
    output_shape: str = "10"
    label_type: str = "integer"
    model_framework: str = "pytorch"
    model_arch_hash: str = ""
    aggregation: str = "FedAvg"
    topology: str = "AffinityTopology"
    output_path: str = "custom.qgl"


@dataclass(slots=True)
class CliConfig:
    binary: str = "quinkgl"
    local_source_path: str = ""
    python_binary: str = "python"
    work_dir: str = ""


@dataclass(slots=True)
class ProjectConfig:
    project_name: str = "QuinkGL Project"
    workspace_path: str = ""
    manifest_path: str = ""
    telemetry_key_path: str = ""
    creator_key_path: str = "creator.key"
    dashboard_url: str = ""
    cli: CliConfig = field(default_factory=CliConfig)
    manifest: ManifestConfig = field(default_factory=ManifestConfig)
    peer: PeerRunConfig = field(default_factory=PeerRunConfig)
    directory: DirectoryConfig = field(default_factory=DirectoryConfig)
    init: ProjectInitConfig = field(default_factory=ProjectInitConfig)

    @property
    def workspace(self) -> Path:
        return Path(self.workspace_path).expanduser().resolve()


@dataclass(slots=True)
class PeerProcessState:
    node_id: str
    command: list[str]
    status: PeerStatus = "stopped"
    dashboard_code: str = ""
    exit_code: int | None = None
    latest_log_line: str = ""
