from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SettingsSection:
    key: str
    label: str
    icon: str


SETTINGS_SECTIONS = [
    SettingsSection("general", "General", "settings"),
    SettingsSection("workspace", "Workspace", "folder-open"),
    SettingsSection("advanced", "Advanced", "flask-conical"),
    SettingsSection("storage", "Storage", "archive"),
    SettingsSection("about", "About", "info"),
]

