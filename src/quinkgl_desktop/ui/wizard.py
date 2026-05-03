from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WizardStep:
    key: str
    label: str
    description: str
    icon: str
    target_page: str


WIZARD_STEPS = [
    WizardStep("workspace", "Workspace", "Select your local project folder", "folder-open", "overview"),
    WizardStep("creator", "Creator Key", "Generate or select creator.key", "key-round", "manifest"),
    WizardStep("manifest", "Manifest", "Describe the swarm and create .qgl", "file-cog", "manifest"),
    WizardStep("telemetry", "Telemetry", "Enroll with the dashboard backend", "radio", "telemetry"),
    WizardStep("peer", "Peer Config", "Set node id, port, script, and rounds", "settings", "run"),
    WizardStep("launch", "Review & Launch", "Start the peer and watch logs", "play-circle", "run"),
]

