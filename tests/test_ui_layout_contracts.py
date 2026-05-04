from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QLineEdit, QPushButton

from quinkgl_desktop.ui.pages.base import card
from quinkgl_desktop.ui.main_window import MainWindow
from quinkgl_desktop.ui.pages.project_picker_page import ProjectPickerPage
from quinkgl_desktop.ui.state import AppState
from quinkgl_desktop.ui.tokens import DEFAULTS, LEVEL_COLORS, RADII, SPACING, TOKENS


def app() -> QApplication:
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def isolate_recent_projects_store(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "quinkgl_desktop.core.recent_projects_store._config_dir",
        lambda: tmp_path / "quinkgl-desktop",
    )


def test_locked_sidebar_items_use_icons_without_locked_text() -> None:
    app()
    window = MainWindow()

    locked_buttons = [
        button
        for key, button in window.nav_buttons.items()
        if key not in {"home", "settings"}
    ]

    assert locked_buttons
    assert all("locked" not in button.text().lower() for button in locked_buttons)


def test_recent_activity_header_has_no_last_24h_badge() -> None:
    app()
    window = MainWindow()

    labels = [label.text() for label in window.overview.findChildren(QLabel)]

    assert "Last 24h" not in labels


def test_wizard_progress_header_is_not_repeated() -> None:
    app()
    window = MainWindow()

    labels = [label.text() for label in window.wizard.findChildren(QLabel)]

    assert labels.count("PROGRESS") == 0
    assert labels.count("Progress") == 1


def test_design_tokens_match_reference_dark_gold_system() -> None:
    assert TOKENS["bg"] == "#080808"
    assert TOKENS["bgDeep"] == "#070707"
    assert TOKENS["panel"] == "#141414"
    assert TOKENS["panelHi"] == "#101010"
    assert TOKENS["gold"] == "#E0B84D"
    assert TOKENS["goldSoft"] == "#E8C75A"
    assert TOKENS["info"] == "#63D9F5"
    assert LEVEL_COLORS["info"] == TOKENS["info"]
    assert RADII["card"] >= 14
    assert SPACING["page_x"] >= 40


def test_default_dashboard_url_points_to_public_telemetry_endpoint() -> None:
    assert DEFAULTS["dashboard_url"] == "https://141-147-36-24.sslip.io/"


def test_telemetry_dashboard_url_is_fixed_to_public_endpoint() -> None:
    from quinkgl_desktop.core.models import ProjectConfig

    app()
    window = MainWindow()
    config = ProjectConfig(
        project_name="project",
        workspace_path="/tmp/project",
        dashboard_url="https://custom.example.com",
    )

    window.telemetry.set_config(config)

    assert window.telemetry.dashboard_url.text() == DEFAULTS["dashboard_url"]
    assert window.telemetry.dashboard_url.isReadOnly()
    assert config.dashboard_url == DEFAULTS["dashboard_url"]


def test_shell_uses_reference_sidebar_and_topbar_scale() -> None:
    app()
    window = MainWindow()

    assert 260 <= window.sidebar_frame.width() <= 280

    topbars = [frame for frame in window.findChildren(type(window.sidebar_frame), "Topbar")]
    assert topbars
    assert all(56 <= frame.height() <= 60 for frame in topbars)


def test_pages_do_not_expose_horizontal_scroll_with_sidebar_states(tmp_path) -> None:
    app()
    window = MainWindow()
    window.resize(1180, 740)
    window.show()
    window.open_project(str(tmp_path / "project"))
    QCoreApplication.processEvents()

    page_keys = ["home", "overview", "wizard", "manifest", "telemetry", "run", "logs", "settings"]
    for collapsed in (False, True):
        if window.sidebar_collapsed != collapsed:
            window.toggle_sidebar()
        for page_key in page_keys:
            window.set_page(page_key)
            QCoreApplication.processEvents()

            assert window.page_scroll.horizontalScrollBar().maximum() == 0, (collapsed, page_key)


def test_page_margins_are_breathable_and_consistent() -> None:
    app()
    window = MainWindow()

    pages = [
        window.project_picker,
        window.overview,
        window.wizard,
        window.manifest,
        window.telemetry,
        window.run_peer,
        window.logs,
        window.settings,
    ]

    for page in pages:
        margins = page.layout().contentsMargins()
        assert margins.left() >= SPACING["page_x"]
        assert margins.right() >= SPACING["page_x"]
        assert margins.top() >= SPACING["page_y"]


def test_card_primitive_uses_premium_default_padding() -> None:
    _frame, layout = card()
    margins = layout.contentsMargins()

    assert margins.left() >= 22
    assert margins.right() >= 22
    assert margins.top() >= 20
    assert margins.bottom() >= 20


def test_sidebar_nav_items_use_structured_right_aligned_meta_column() -> None:
    app()
    window = MainWindow()

    nav_items = window.sidebar.findChildren(QFrame, "NavItem")
    assert len(nav_items) == 7

    meta_right_edges = []
    for item in nav_items:
        title = item.findChild(QLabel, "NavTitle")
        meta = item.findChild(QLabel, "NavMeta")
        assert title is not None
        assert meta is not None
        assert item.text() == title.text()
        meta_right_edges.append(meta.geometry().right())

    assert max(meta_right_edges) - min(meta_right_edges) <= 2


def test_sidebar_collapse_button_is_inside_sidebar_edge() -> None:
    app()
    window = MainWindow()

    button = window.collapse_button
    assert button.x() + button.width() <= window.sidebar_frame.width() - 8
    assert button.width() == button.height()
    assert button.width() <= 24


def test_app_version_is_current_and_old_version_is_not_rendered() -> None:
    app()
    window = MainWindow()

    labels = [label.text() for label in window.findChildren(QLabel)]

    assert AppState().app_version == "0.1"
    assert any("v0.1" in text for text in labels)
    assert all("0.4.2" not in text for text in labels)


def test_topbar_search_has_no_shortcut_or_notification_button() -> None:
    app()
    window = MainWindow()

    search_box = window.findChild(QFrame, "SearchBox")
    assert search_box is not None
    assert search_box.findChild(QLabel, "KBD") is None

    topbar = search_box.parentWidget()
    assert topbar is not None
    empty_topbar_buttons = [
        button
        for button in topbar.findChildren(QPushButton)
        if button.parentWidget() is topbar and button.text() == ""
    ]

    assert empty_topbar_buttons == []
    assert window.peer_chip.minimumWidth() >= 94


def test_landing_hero_and_first_time_card_have_internal_padding_without_clone() -> None:
    app()
    page = ProjectPickerPage()

    hero = page.findChild(QFrame, "HeroCard")
    assert hero is not None
    assert hero.layout().contentsMargins().left() >= 20

    buttons = page.findChildren(QPushButton)
    assert "Clone from Git" not in {button.text() for button in buttons}

    # Start from template removed; first_time card is present instead
    template_rows = page.findChild(QFrame, "TemplateRows")
    assert template_rows is None


def test_landing_recent_projects_are_real_project_history(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "quinkgl_desktop.ui.pages.project_picker_page.load_recent_projects",
        lambda: [],
    )
    app()
    window = MainWindow()

    recent_card = window.project_picker.findChild(QFrame, "RecentProjectsCard")
    assert recent_card is not None
    assert recent_card.maximumHeight() <= 150

    rows = window.project_picker.findChildren(QFrame, "ProjectRow")
    labels = [label.text() for label in window.project_picker.findChildren(QLabel)]
    assert rows == []
    assert all("count" not in text.lower() for text in labels)
    assert "test-playground-5" not in labels

    search = window.project_picker.findChild(QLineEdit, "RecentProjectFilter")
    assert search is not None
    assert search.width() <= 280 or search.maximumWidth() <= 280

    workspace = tmp_path / "opened-workspace"
    window.open_project(str(workspace))
    window.show_project_picker()

    rows = window.project_picker.findChildren(QFrame, "ProjectRow")
    labels = [label.text() for label in window.project_picker.findChildren(QLabel)]

    assert len(rows) == 1
    assert all(row.minimumHeight() <= 100 for row in rows)
    assert 120 <= recent_card.maximumHeight() <= 220
    assert "opened-workspace" in labels
    assert all(text not in labels for text in ["12m", "2 days ago", "1 week ago", "3 weeks ago", "1 month ago"])


def test_landing_empty_recent_projects_is_narrower_than_first_time(monkeypatch) -> None:
    monkeypatch.setattr(
        "quinkgl_desktop.ui.pages.project_picker_page.load_recent_projects",
        lambda: [],
    )
    app()
    page = ProjectPickerPage()
    page.resize(908, 620)
    page.show()
    QCoreApplication.processEvents()

    recent_card = page.findChild(QFrame, "RecentProjectsCard")
    first_time_card = page.findChild(QFrame, "FirstTimeCard")

    assert recent_card is not None
    assert first_time_card is not None
    assert recent_card.width() < first_time_card.width()
    assert first_time_card.width() >= 540


def test_landing_long_recent_paths_do_not_collapse_first_time(monkeypatch) -> None:
    long_path = (
        "/Users/alice/Documents/QuinkGL/workspaces/with/a/very/deep/nested/folder/"
        "created/by/a/user/to/check/landing/recent/project/layout"
    )
    monkeypatch.setattr(
        "quinkgl_desktop.ui.pages.project_picker_page.load_recent_projects",
        lambda: [
            {"name": "vision-training", "path": f"{long_path}/vision-training", "manifest": "manifest.qgl", "status": "draft"},
            {"name": "audio-baseline", "path": f"{long_path}/audio-baseline", "manifest": "manifest.qgl", "status": "draft"},
        ],
    )
    app()
    page = ProjectPickerPage()
    page.resize(1600, 900)
    page.show()
    QCoreApplication.processEvents()

    first_time_card = page.findChild(QFrame, "FirstTimeCard")

    assert first_time_card is not None
    assert first_time_card.width() >= 540


def test_logs_page_starts_without_demo_seed():
    import pytest

    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    from quinkgl_desktop.core.process_manager import PeerProcessManager
    from quinkgl_desktop.ui.pages.logs_page import LogsPage

    app = QApplication.instance() or QApplication([])
    page = LogsPage(PeerProcessManager())

    assert page.all_lines == []
    assert "peer-1 starting" not in page.terminal.toPlainText()


def test_process_manager_sets_environment_when_empty_mapping_provided(monkeypatch, tmp_path):
    import pytest

    pytest.importorskip("PySide6")
    import PySide6.QtCore as qtcore

    import quinkgl_desktop.core.process_manager as process_manager_module
    from quinkgl_desktop.core.process_manager import PeerProcessManager

    class FakeSignal:
        def __init__(self) -> None:
            self.callbacks = []

        def connect(self, callback) -> None:
            self.callbacks.append(callback)

    class FakeEnvironment:
        created = 0

        def __init__(self) -> None:
            self.values = {}

        @classmethod
        def systemEnvironment(cls):
            cls.created += 1
            return cls()

        def insert(self, key, value) -> None:
            self.values[key] = value

    class FakeProcess:
        instances = []

        def __init__(self, parent) -> None:
            self.parent = parent
            self.readyReadStandardOutput = FakeSignal()
            self.readyReadStandardError = FakeSignal()
            self.finished = FakeSignal()
            self.process_environment = None
            FakeProcess.instances.append(self)

        def setWorkingDirectory(self, cwd) -> None:
            self.cwd = cwd

        def setProgram(self, program) -> None:
            self.program = program

        def setArguments(self, arguments) -> None:
            self.arguments = arguments

        def setProcessEnvironment(self, environment) -> None:
            self.process_environment = environment

        def start(self) -> None:
            self.started = True

    monkeypatch.setattr(process_manager_module, "QProcess", FakeProcess)
    monkeypatch.setattr(qtcore, "QProcessEnvironment", FakeEnvironment)

    manager = PeerProcessManager()
    manager.start(["quinkgl"], tmp_path, env={})

    assert FakeEnvironment.created == 1
    assert FakeProcess.instances[0].process_environment is not None


def test_process_manager_forces_unbuffered_peer_output(monkeypatch, tmp_path):
    import pytest

    pytest.importorskip("PySide6")
    import PySide6.QtCore as qtcore

    import quinkgl_desktop.core.process_manager as process_manager_module
    from quinkgl_desktop.core.process_manager import PeerProcessManager

    class FakeSignal:
        def connect(self, callback) -> None:
            self.callback = callback

    class FakeEnvironment:
        def __init__(self) -> None:
            self.values = {}

        @classmethod
        def systemEnvironment(cls):
            return cls()

        def insert(self, key, value) -> None:
            self.values[key] = value

    class FakeProcess:
        instances = []

        def __init__(self, parent) -> None:
            self.readyReadStandardOutput = FakeSignal()
            self.readyReadStandardError = FakeSignal()
            self.finished = FakeSignal()
            self.process_environment = None
            FakeProcess.instances.append(self)

        def setWorkingDirectory(self, cwd) -> None:
            self.cwd = cwd

        def setProgram(self, program) -> None:
            self.program = program

        def setArguments(self, arguments) -> None:
            self.arguments = arguments

        def setProcessEnvironment(self, environment) -> None:
            self.process_environment = environment

        def start(self) -> None:
            self.started = True

    monkeypatch.setattr(process_manager_module, "QProcess", FakeProcess)
    monkeypatch.setattr(qtcore, "QProcessEnvironment", FakeEnvironment)

    manager = PeerProcessManager()
    manager.start(["quinkgl"], tmp_path)

    assert FakeProcess.instances[0].process_environment.values["PYTHONUNBUFFERED"] == "1"


def test_settings_page_has_cli_override_fields():
    app()
    from quinkgl_desktop.ui.pages.settings_page import SettingsPage

    page = SettingsPage()
    object_names = {field.objectName() for field in page.findChildren(QLineEdit)}

    assert "CliBinaryField" in object_names
    assert "CliLocalSourceField" in object_names


def test_run_peer_passes_cli_environment_to_process_manager(tmp_path):
    from quinkgl_desktop.core.models import ProjectConfig

    app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    local_repo = tmp_path / "QuinkGL"
    (local_repo / "src").mkdir(parents=True)

    config = ProjectConfig(workspace_path=str(workspace), manifest_path="demo.qgl")
    config.cli.local_source_path = str(local_repo)
    config.cli.python_binary = "python3"

    window = MainWindow()
    window.config = config
    window.store = None
    window._bind_cli(config.cli)
    window.run_peer.set_config(config)
    captured = {}

    def fake_start(command, cwd, env=None):
        captured["command"] = command
        captured["cwd"] = cwd
        captured["env"] = env

    window.process_manager.start = fake_start
    window.run_peer.start_peer()

    assert captured["command"][:3] == ["python3", "-m", "quinkgl.cli"]
    assert captured["env"] is not None
    assert str(local_repo / "src") in captured["env"]["PYTHONPATH"].split(":")


def test_overview_launch_button_aligns_with_readiness_header(tmp_path) -> None:
    app()
    window = MainWindow()
    window.resize(1600, 1000)
    window.open_project(str(tmp_path / "launch-workspace"))
    window.show()
    app().processEvents()

    readiness_label = next(
        label for label in window.overview.findChildren(QLabel)
        if label.text() == "PROJECT READINESS"
    )
    launch_button = window.overview.launch_button

    assert abs(launch_button.geometry().center().y() - readiness_label.geometry().center().y()) <= 10


def test_wizard_and_telemetry_action_buttons_have_production_control_size() -> None:
    app()
    window = MainWindow()

    assert window.wizard.skip_button.minimumWidth() >= 88
    assert window.wizard.done_button.minimumWidth() >= 142
    assert window.wizard.skip_button.minimumHeight() >= 38
    assert window.wizard.done_button.minimumHeight() >= 38

    telemetry_buttons = {
        button.text(): button
        for button in window.telemetry.findChildren(QPushButton)
    }

    assert telemetry_buttons["Enroll Telemetry"].minimumWidth() >= 150
    assert telemetry_buttons["Request new code"].minimumWidth() >= 156
    assert telemetry_buttons["Enroll Telemetry"].minimumHeight() >= 38
    assert telemetry_buttons["Request new code"].minimumHeight() >= 38


def test_manifest_page_exposes_preset_install_and_hash_actions() -> None:
    app()
    window = MainWindow()

    buttons = {button.text(): button for button in window.manifest.findChildren(QPushButton)}

    assert "Generate creator.key" in buttons
    assert "Install preset files" in buttons
    assert "Compute hash" in buttons
    assert window.manifest.findChild(QLabel, "ManifestFeedback") is not None


def test_manifest_preset_install_updates_page_feedback(tmp_path) -> None:
    from quinkgl_desktop.core.models import ProjectConfig

    app()
    window = MainWindow()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config = ProjectConfig(workspace_path=str(workspace))
    window.manifest.set_config(config)
    window.manifest.apply_preset("MNIST")

    window.manifest.install_preset_files()

    feedback = window.manifest.findChild(QLabel, "ManifestFeedback")
    assert feedback.text() == "Preset files installed."
    assert (workspace / "peer_script.py").exists()
    assert (workspace / "compute_hash.py").exists()


def test_manifest_generate_key_updates_page_feedback(tmp_path) -> None:
    from quinkgl_desktop.core.cli_adapter import CommandResult
    from quinkgl_desktop.core.models import ProjectConfig

    class FakeKeyService:
        def generate_creator_key(self, workspace):
            return CommandResult(["quinkgl", "keygen"], 0, "wrote key\n", "")

    app()
    window = MainWindow()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config = ProjectConfig(workspace_path=str(workspace))
    window.manifest.key_service = FakeKeyService()
    window.manifest.set_config(config)

    window.manifest.generate_key()

    feedback = window.manifest.findChild(QLabel, "ManifestFeedback")
    assert feedback.text() == "Creator key generated."


def test_wizard_progress_uses_lightweight_step_rows() -> None:
    app()
    window = MainWindow()

    rows = window.wizard.findChildren(QFrame, "WizardStepRow")
    assert len(rows) == 6
    assert all(row.minimumHeight() <= 58 for row in rows)

    active = [row for row in rows if row.property("active") is True]
    assert len(active) == 1
