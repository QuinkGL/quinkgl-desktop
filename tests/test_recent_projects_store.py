from __future__ import annotations

import json

from quinkgl_desktop.core.recent_projects_store import load_recent_projects, save_recent_projects


def test_round_trip_recent_projects(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "quinkgl_desktop.core.recent_projects_store._config_dir",
        lambda: tmp_path / "quinkgl-desktop",
    )

    projects = [
        {"name": "demo", "path": "/tmp/demo", "manifest": "demo.qgl", "status": "ready"},
        {"name": "test", "path": "/tmp/test", "manifest": "test.qgl", "status": "draft"},
    ]

    save_recent_projects(projects)
    loaded = load_recent_projects()

    assert len(loaded) == 2
    assert loaded[0]["name"] == "demo"
    assert loaded[1]["path"] == "/tmp/test"


def test_load_returns_empty_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "quinkgl_desktop.core.recent_projects_store._config_dir",
        lambda: tmp_path / "quinkgl-desktop",
    )

    assert load_recent_projects() == []


def test_load_returns_empty_on_corrupt_json(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "quinkgl_desktop.core.recent_projects_store._config_dir",
        lambda: tmp_path / "quinkgl-desktop",
    )

    config_dir = tmp_path / "quinkgl-desktop"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "recent_projects.json").write_text("not-json", encoding="utf-8")

    assert load_recent_projects() == []


def test_recent_projects_store_ignores_pytest_temp_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "quinkgl_desktop.core.recent_projects_store._config_dir",
        lambda: tmp_path / "quinkgl-desktop",
    )

    projects = [
        {
            "name": "real-workspace",
            "path": "/Users/alice/QuinkGL/real-workspace",
            "manifest": "real.qgl",
            "status": "ready",
        },
        {
            "name": "generated-test-workspace",
            "path": "/private/var/folders/cache/T/pytest-of-alice/pytest-12/test_case0/generated-test-workspace",
            "manifest": "test.qgl",
            "status": "draft",
        },
    ]

    save_recent_projects(projects)

    loaded = load_recent_projects()
    assert loaded == [projects[0]]


def test_remove_recent_project_by_path(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "quinkgl_desktop.core.recent_projects_store._config_dir",
        lambda: tmp_path / "quinkgl-desktop",
    )

    projects = [
        {"name": "keep", "path": "/tmp/keep", "manifest": "keep.qgl", "status": "ready"},
        {"name": "remove", "path": "/tmp/remove", "manifest": "remove.qgl", "status": "draft"},
    ]

    save_recent_projects(projects)
    loaded = load_recent_projects()
    assert len(loaded) == 2

    # Simulate removal
    filtered = [p for p in loaded if p["path"] != "/tmp/remove"]
    save_recent_projects(filtered)

    after = load_recent_projects()
    assert len(after) == 1
    assert after[0]["name"] == "keep"
