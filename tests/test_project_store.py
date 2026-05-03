import json
from dataclasses import asdict

from quinkgl_desktop.core.models import CliConfig, DirectoryConfig, ProjectConfig, ProjectInitConfig


def test_project_config_serializes_nested_peer_config():
    config = ProjectConfig(
        project_name="cifar10-swarm-test",
        workspace_path="/tmp/quinkgl",
        manifest_path="cifar10-test.qgl",
    )

    data = asdict(config)

    assert data["project_name"] == "cifar10-swarm-test"
    assert data["peer"]["node_id"] == "peer-1"
    assert data["peer"]["script_args"]["data_root"] == "./data"


def test_project_store_round_trips_project_config(tmp_path):
    from quinkgl_desktop.core.project_store import ProjectStore

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config = ProjectConfig(
        project_name="demo",
        workspace_path=str(workspace),
        manifest_path="demo.qgl",
    )

    store = ProjectStore(workspace)
    store.save(config)

    loaded = store.load()

    assert loaded.project_name == "demo"
    assert loaded.workspace_path == str(workspace)
    assert loaded.manifest_path == "demo.qgl"
    assert loaded.peer.node_id == "peer-1"
    assert (workspace / ".quinkgl-desktop" / "project.json").exists()


def test_project_store_round_trips_new_nested_configs(tmp_path):
    from quinkgl_desktop.core.project_store import ProjectStore

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config = ProjectConfig(
        workspace_path=str(workspace),
        cli=CliConfig(binary="quinkgl-dev"),
        directory=DirectoryConfig(cache_path="ads.json"),
        init=ProjectInitConfig(template="pytorch-vision"),
    )

    store = ProjectStore(workspace)
    store.save(config)

    loaded = store.load()

    assert loaded.cli.binary == "quinkgl-dev"
    assert not isinstance(loaded.cli, dict)
    assert loaded.directory.cache_path == "ads.json"
    assert not isinstance(loaded.directory, dict)
    assert loaded.init.template == "pytorch-vision"
    assert not isinstance(loaded.init, dict)


def test_project_store_loads_old_project_without_new_sections(tmp_path):
    from quinkgl_desktop.core.project_store import ProjectStore

    workspace = tmp_path / "workspace"
    state = workspace / ".quinkgl-desktop"
    state.mkdir(parents=True)
    (state / "project.json").write_text(json.dumps({
        "project_name": "old",
        "workspace_path": str(workspace),
        "manifest_path": "old.qgl",
        "peer": {"node_id": "old-peer"},
        "manifest": {"name": "old-swarm"}
    }), encoding="utf-8")

    loaded = ProjectStore(workspace).load()

    assert loaded.project_name == "old"
    assert loaded.workspace_path == str(workspace)
    assert loaded.manifest_path == "old.qgl"
    assert loaded.cli.binary == "quinkgl"
    assert loaded.directory.max_swarms == 1
    assert loaded.peer.node_id == "old-peer"
    assert loaded.manifest.name == "old-swarm"


def test_project_store_ignores_unknown_nested_project_keys(tmp_path):
    from quinkgl_desktop.core.project_store import ProjectStore

    workspace = tmp_path / "workspace"
    state = workspace / ".quinkgl-desktop"
    state.mkdir(parents=True)
    (state / "project.json").write_text(json.dumps({
        "project_name": "future",
        "workspace_path": str(workspace),
        "manifest_path": "future.qgl",
        "cli": {"binary": "quinkgl-dev", "future_option": True},
        "directory": {"max_swarms": 3, "future_option": True},
        "init": {"template": "pytorch-vision", "future_option": True},
        "peer": {"node_id": "future-peer", "future_option": True},
        "manifest": {"name": "future-swarm", "future_option": True},
    }), encoding="utf-8")

    loaded = ProjectStore(workspace).load()

    assert loaded.cli.binary == "quinkgl-dev"
    assert loaded.directory.max_swarms == 3
    assert loaded.init.template == "pytorch-vision"
    assert loaded.peer.node_id == "future-peer"
    assert loaded.manifest.name == "future-swarm"


def test_main_window_starts_on_home_with_sidebar_and_locked_project_pages():
    import pytest

    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    from quinkgl_desktop.ui.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()

    assert window.stack.currentWidget() is window.project_picker
    assert window.sidebar.isVisibleTo(window) is True
    assert window.project_label.text() == "No project selected"
    assert window.nav_buttons["home"].isEnabled() is True
    assert window.nav_buttons["overview"].isEnabled() is False
    assert window.nav_buttons["settings"].isEnabled() is True


def test_project_picker_shows_brand_logo_and_compact_actions():
    import pytest

    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPushButton

    from quinkgl_desktop.ui.pages.project_picker_page import ProjectPickerPage

    app = QApplication.instance() or QApplication([])
    page = ProjectPickerPage()
    logo_backdrop = page.findChild(QFrame, "LogoBackdrop")
    logo = page.findChild(QLabel, "BrandLogo")
    buttons = page.findChildren(QPushButton)

    assert logo_backdrop is not None
    assert logo is not None
    assert logo.pixmap() is not None
    assert logo.pixmap().isNull() is False
    assert {button.text() for button in buttons} >= {"Create Project", "Open Project"}
    assert len(buttons) >= 6


def test_main_window_can_return_to_project_picker_after_project_open(tmp_path):
    import pytest

    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    from quinkgl_desktop.ui.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.open_project(str(tmp_path / "first-project"))

    assert window.stack.currentWidget() is window.overview
    assert window.sidebar_frame.isHidden() is False

    window.show_project_picker()

    assert window.stack.currentWidget() is window.project_picker
    assert window.sidebar_frame.isHidden() is False
    assert window.project_label.text() == "first-project"


def test_main_window_uses_config_artifact_paths_after_project_open(tmp_path):
    import pytest

    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    from quinkgl_desktop.core.models import ProjectConfig
    from quinkgl_desktop.core.project_store import ProjectStore
    from quinkgl_desktop.ui.main_window import MainWindow

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "keys").mkdir()
    (workspace / "keys" / "creator.pem").write_text("secret", encoding="utf-8")
    (workspace / "custom.qgl").write_text("{}", encoding="utf-8")
    config = ProjectConfig(
        workspace_path=str(workspace),
        creator_key_path="keys/creator.pem",
        manifest_path="custom.qgl",
    )
    ProjectStore(workspace).save(config)

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.open_project(str(workspace))

    assert window.config.creator_key_path == "keys/creator.pem"
    assert window.config.manifest_path == "custom.qgl"
    assert window.overview.artifacts.creator_key_ready is True
    assert window.overview.artifacts.manifest_ready is True


def test_navigation_structure_remains_fixed_and_collapsible():
    import pytest

    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    from quinkgl_desktop.ui.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()

    assert window.PAGE_NAMES == ["Home", "Overview", "Wizard", "Manifest", "Telemetry", "Run Peer", "Logs", "Settings"]
    assert len(window.nav_buttons) == len(window.PAGE_NAMES)

    expanded_width = window.sidebar_frame.width()
    window.toggle_sidebar()

    assert window.sidebar_collapsed is True
    assert window.sidebar_frame.width() < expanded_width
