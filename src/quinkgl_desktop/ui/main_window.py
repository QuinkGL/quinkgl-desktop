from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QFontDatabase, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from quinkgl_desktop.core.artifact_resolver import ProjectArtifacts
from quinkgl_desktop.core.cli_adapter import QuinkGLCli
from quinkgl_desktop.core.models import CliConfig, ProjectConfig
from quinkgl_desktop.core.process_manager import PeerProcessManager
from quinkgl_desktop.core.project_store import ProjectStore
from quinkgl_desktop.services.key_service import KeyService
from quinkgl_desktop.services.manifest_service import ManifestService
from quinkgl_desktop.services.peer_run_service import PeerRunService
from quinkgl_desktop.services.project_init_service import ProjectInitService
from quinkgl_desktop.services.telemetry_service import TelemetryService
from quinkgl_desktop.ui.i18n import APP_COPY, STATUS_LABELS
from quinkgl_desktop.ui.icons import lucide_icon
from quinkgl_desktop.ui.nav import PAGE_BY_KEY, PAGE_KEY_BY_LABEL, PAGE_LABELS, PAGES, Navigator
from quinkgl_desktop.ui.pages.logs_page import LogsPage
from quinkgl_desktop.ui.pages.manifest_page import ManifestPage
from quinkgl_desktop.ui.pages.overview_page import OverviewPage
from quinkgl_desktop.ui.pages.project_picker_page import ProjectPickerPage
from quinkgl_desktop.ui.pages.run_peer_page import RunPeerPage
from quinkgl_desktop.ui.pages.settings_page import SettingsPage
from quinkgl_desktop.ui.pages.telemetry_page import TelemetryPage
from quinkgl_desktop.ui.pages.wizard_page import WizardPage
from quinkgl_desktop.ui.search import SearchPopup
from quinkgl_desktop.ui.state import AppState
from quinkgl_desktop.ui.tokens import COLORS, PEER_STATE_BADGES, PEER_STATE_COLORS, PeerState, TOKENS


class SidebarNavItem(QFrame):
    clicked = Signal()

    def __init__(self, title: str, meta: str, icon_name: str) -> None:
        super().__init__()
        self._title = title
        self._meta = meta
        self._checked = False
        self._collapsed = False
        self._icon_name = icon_name
        self.setObjectName("NavItem")
        self.setFixedHeight(38)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(9)

        self.icon_label = QLabel()
        self.icon_label.setObjectName("NavIcon")
        self.icon_label.setFixedSize(16, 16)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("NavTitle")
        self.meta_label = QLabel(meta)
        self.meta_label.setObjectName("NavMeta")
        self.meta_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.meta_label.setFixedWidth(92)

        layout.addWidget(self.icon_label, 0, Qt.AlignVCenter)
        layout.addWidget(self.title_label, 0, Qt.AlignVCenter)
        layout.addStretch(1)
        layout.addWidget(self.meta_label, 0, Qt.AlignVCenter)
        self.setIcon(lucide_icon(icon_name, 16, TOKENS["textMute"], stroke=1.65))
        self._update_state()

    def text(self) -> str:
        return self._title

    def setText(self, text: str) -> None:
        self._title = text
        self.title_label.setText(text)

    def setMeta(self, text: str) -> None:
        self._meta = text
        self.meta_label.setText(text)

    def setIcon(self, icon: QIcon) -> None:
        self.icon_label.setPixmap(icon.pixmap(QSize(16, 16)))

    def setChecked(self, checked: bool) -> None:
        self._checked = checked
        self.setProperty("active", checked)
        self._update_state()

    def isChecked(self) -> bool:
        return self._checked

    def setCollapsed(self, collapsed: bool) -> None:
        self._collapsed = collapsed
        self.title_label.setVisible(not collapsed)
        self.meta_label.setVisible(not collapsed)
        self.layout().setContentsMargins(0 if collapsed else 12, 0, 0 if collapsed else 12, 0)
        self.layout().setAlignment(self.icon_label, Qt.AlignCenter)

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self.setProperty("locked", not enabled)
        self.setCursor(Qt.PointingHandCursor if enabled else Qt.ArrowCursor)
        self._update_state()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self.isEnabled():
            self.clicked.emit()
        super().mousePressEvent(event)

    def _update_state(self) -> None:
        active = self._checked
        locked = not self.isEnabled()
        if locked:
            icon_color = TOKENS["textDisabled"]
            title_color = TOKENS["textDisabled"]
            meta_color = TOKENS["textDisabled"]
        elif active:
            icon_color = TOKENS["goldSoft"]
            title_color = TOKENS["goldSoft"]
            meta_color = TOKENS["goldSoft"]
        else:
            icon_color = TOKENS["textDim"]
            title_color = TOKENS["textDim"]
            meta_color = TOKENS["textMute"]
        self.title_label.setStyleSheet(f"color: {title_color}; font-size: 14px; font-weight: 700;")
        self.meta_label.setStyleSheet(f"color: {meta_color}; font-size: 13px; font-weight: 700;")
        icon_name = "lock" if locked else self._icon_name
        self.setIcon(lucide_icon(icon_name, 14 if locked else 16, icon_color, stroke=1.65))
        for widget in (self, self.title_label, self.meta_label, self.icon_label):
            widget.style().unpolish(widget)
            widget.style().polish(widget)


class ResponsiveStackedWidget(QStackedWidget):
    def sizeHint(self) -> QSize:
        current = self.currentWidget()
        height = current.sizeHint().height() if current else super().sizeHint().height()
        return QSize(0, height)

    def minimumSizeHint(self) -> QSize:
        current = self.currentWidget()
        height = current.minimumSizeHint().height() if current else super().minimumSizeHint().height()
        return QSize(0, height)


class MainWindow(QMainWindow):
    PAGE_NAMES = PAGE_LABELS

    def __init__(self) -> None:
        super().__init__()
        self.app_state = AppState()
        self.navigator = Navigator(self.set_page)
        self.setWindowTitle(f"{APP_COPY['brand_name']} {APP_COPY['brand_product']}")
        self.setMinimumSize(1180, 740)
        self.config: ProjectConfig | None = None
        self.store: ProjectStore | None = None
        self.sidebar_collapsed = False
        self.nav_buttons: dict[str, QPushButton] = {}
        self.page_index_by_key: dict[str, int] = {}

        self.cli = QuinkGLCli()
        self.process_manager = PeerProcessManager()
        self.key_service = KeyService(self.cli)
        self.manifest_service = ManifestService(self.cli)
        self.telemetry_service = TelemetryService(self.cli)
        self.peer_run_service = PeerRunService(self.cli)
        self.project_init_service = ProjectInitService(self.cli)

        self._load_theme()
        self._build_ui()
        self._connect_signals()

    def _load_theme(self) -> None:
        font_dir = Path(__file__).resolve().parents[1] / "resources" / "fonts"
        for font_file in ["InterVariable.ttf", "JetBrainsMono-Regular.ttf"]:
            path = font_dir / font_file
            if path.exists():
                QFontDatabase.addApplicationFont(str(path))
        theme_path = Path(__file__).resolve().parents[1] / "resources" / "theme.qss"
        if theme_path.exists():
            self.setStyleSheet(theme_path.read_text(encoding="utf-8"))
        project_icon = Path(__file__).resolve().parents[3] / "quinkgl_logo.png"
        bundled_icon = Path(__file__).resolve().parents[1] / "resources" / "quinkgl_logo.png"
        icon_path = project_icon if project_icon.exists() else bundled_icon
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

    def _build_ui(self) -> None:
        root = QWidget()
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        self.sidebar = sidebar_frame

        # Brand header — prototype style
        brand_header = QFrame()
        brand_header.setObjectName("Topbar")
        brand_header.setFixedHeight(58)
        brand_header_layout = QHBoxLayout(brand_header)
        brand_header_layout.setContentsMargins(20, 0, 18, 0)
        brand_header_layout.setSpacing(8)

        brand_title = QLabel("QuinkGL")
        brand_title.setObjectName("BrandTitle")
        brand_subtitle = QLabel(f"Desktop \u00b7 v{self.app_state.app_version}")
        brand_subtitle.setObjectName("BrandSubtitle")
        brand_header_layout.addWidget(brand_title)
        brand_header_layout.addWidget(brand_subtitle)
        brand_header_layout.addStretch(1)
        sidebar_layout.addWidget(brand_header)

        # Project selector pill
        self.project_pill_container = QWidget()
        pill_layout = QVBoxLayout(self.project_pill_container)
        pill_layout.setContentsMargins(16, 12, 16, 0)
        pill_layout.setSpacing(0)
        self.sidebar_project_button = QPushButton()
        self.sidebar_project_button.setObjectName("ProjectPill")
        self.sidebar_project_button.setFixedHeight(42)
        self.sidebar_project_button.setCursor(Qt.PointingHandCursor)
        self.sidebar_project_button.clicked.connect(lambda: self.set_page("home"))
        pill_layout.addWidget(self.sidebar_project_button)
        sidebar_layout.addWidget(self.project_pill_container)

        # Visible home navigation is the project selector; keep this hidden entry
        # so navigation contracts can address every page by key.
        self.home_nav_button = QPushButton("Home")
        self.home_nav_button.setEnabled(True)
        self.home_nav_button.hide()
        self.nav_buttons["home"] = self.home_nav_button

        # Nav
        nav_container = QWidget()
        nav_container_layout = QVBoxLayout(nav_container)
        nav_container_layout.setContentsMargins(14, 22, 14, 0)
        nav_container_layout.setSpacing(10)
        self.workspace_label = QLabel(APP_COPY["workspace"].upper())
        self.workspace_label.setStyleSheet(
            f"font-size: 11px; letter-spacing: 0.24em; color: {TOKENS['textMute']}; font-weight: 700; text-transform: uppercase; padding-left: 4px; margin-bottom: 6px;"
        )
        nav_container_layout.addWidget(self.workspace_label)

        nav_list = QVBoxLayout()
        nav_list.setSpacing(4)
        for item in PAGES:
            if item.key == "home":
                continue
            button = SidebarNavItem(item.label, item.hint, item.icon)
            button.clicked.connect(lambda _checked=False, page=item.key: self.set_page(page))
            button.setProperty("label", item.label)
            button.setProperty("hint", item.hint)
            button.setProperty("icon_name", item.icon)
            self.nav_buttons[item.key] = button
            nav_list.addWidget(button)
        nav_container_layout.addLayout(nav_list)
        nav_container_layout.addStretch(1)
        sidebar_layout.addWidget(nav_container, 1)

        # Footer
        footer = QFrame()
        footer.setStyleSheet("background: transparent; border: none;")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(20, 14, 20, 18)
        footer_layout.setSpacing(8)

        self.footer_content = QWidget()
        footer_inner = QVBoxLayout(self.footer_content)
        footer_inner.setContentsMargins(0, 0, 0, 0)
        footer_inner.setSpacing(6)

        setup_row = QHBoxLayout()
        setup_row.setContentsMargins(0, 0, 0, 0)
        setup_label = QLabel(APP_COPY["setup"].upper())
        setup_label.setStyleSheet(f"font-size: 11px; color: {TOKENS['textMute']}; letter-spacing: 0.24em; text-transform: uppercase; font-weight: 700;")
        self.setup_count_label = QLabel("0/3")
        self.setup_count_label.setStyleSheet(f"font-size: 12px; color: {TOKENS['textDim']}; font-weight: 650;")
        setup_row.addWidget(setup_label)
        setup_row.addStretch(1)
        setup_row.addWidget(self.setup_count_label)
        footer_inner.addLayout(setup_row)

        self.sidebar_progress = QFrame()
        self.sidebar_progress.setObjectName("ProgressTrack")
        self.sidebar_progress.setFixedHeight(4)
        self.sidebar_progress_fill = QFrame(self.sidebar_progress)
        self.sidebar_progress_fill.setObjectName("ProgressFill")
        self.sidebar_progress_fill.setGeometry(0, 0, 1, 4)
        footer_inner.addWidget(self.sidebar_progress)

        self.peer_status_chip = QFrame()
        self.peer_status_chip.setObjectName("PeerStatusChip")
        self.peer_status_chip.setFixedHeight(28)
        chip_layout = QHBoxLayout(self.peer_status_chip)
        chip_layout.setContentsMargins(8, 0, 8, 0)
        chip_layout.setSpacing(6)
        self.peer_dot_label = QLabel("\u25cf")
        self.peer_dot_label.setStyleSheet(f"font-size: 7px; color: {TOKENS['textMute']};")
        self.peer_status_text = QLabel(f"{APP_COPY['peer']} \u00b7 {STATUS_LABELS['stopped'].lower()}")
        self.peer_status_text.setStyleSheet(f"font-size: 12px; color: {TOKENS['textDim']}; text-transform: capitalize; font-weight: 600;")
        chip_layout.addWidget(self.peer_dot_label)
        chip_layout.addWidget(self.peer_status_text)
        chip_layout.addStretch(1)
        footer_inner.addWidget(self.peer_status_chip)

        footer_layout.addWidget(self.footer_content)
        sidebar_layout.addWidget(footer)

        sidebar_frame.setFixedWidth(272)
        self.sidebar_frame = sidebar_frame

        # Collapse toggle
        self.collapse_button = QPushButton()
        self.collapse_button.setObjectName("CollapseToggle")
        self.collapse_button.setFixedSize(22, 22)
        self.collapse_button.setIcon(lucide_icon("chevron-left", 14, TOKENS["textDim"], stroke=1.9))
        self.collapse_button.setIconSize(QSize(14, 14))
        self.collapse_button.setCursor(Qt.PointingHandCursor)
        self.collapse_button.clicked.connect(self.toggle_sidebar)
        self.collapse_button.setParent(sidebar_frame)
        self.collapse_button.move(238, 122)

        # Content area
        content = QFrame()
        content.setObjectName("ContentRoot")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Topbar — prototype style
        topbar = QFrame()
        topbar.setObjectName("Topbar")
        topbar.setFixedHeight(58)
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(24, 0, 24, 0)
        topbar_layout.setSpacing(10)

        # Breadcrumb
        breadcrumb = QHBoxLayout()
        breadcrumb.setSpacing(6)
        projects_label = QLabel("Projects")
        projects_label.setStyleSheet(f"font-size: 14px; color: {TOKENS['textDim']}; font-weight: 600;")
        slash = QLabel("\u203a")
        slash.setStyleSheet(f"font-size: 15px; color: {TOKENS['textMute']};")
        self.project_label = QLabel(APP_COPY["no_project"])
        self.project_label.setStyleSheet(f"font-size: 14px; color: {TOKENS['text']}; font-weight: 700;")
        breadcrumb.addWidget(projects_label)
        breadcrumb.addWidget(slash)
        breadcrumb.addWidget(self.project_label)
        topbar_layout.addLayout(breadcrumb)
        topbar_layout.addStretch(1)

        # Search — functional prototype style
        search_container = QFrame()
        search_container.setObjectName("SearchBox")
        search_container.setFixedHeight(36)
        search_container.setFixedWidth(520)
        search_container.setCursor(Qt.PointingHandCursor)
        sc_layout = QHBoxLayout(search_container)
        sc_layout.setContentsMargins(8, 0, 6, 0)
        sc_layout.setSpacing(6)
        search_icon = QLabel()
        search_icon.setPixmap(lucide_icon("search", 13, COLORS["text_muted"]).pixmap(13, 13))
        self.search_text = QLineEdit()
        self.search_text.setPlaceholderText("Search anything\u2026")
        self.search_text.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {TOKENS['text']};
                font-size: 14px;
                padding: 0;
                min-height: 0px;
            }}
        """)
        self.search_text.textChanged.connect(self._on_search_text_changed)
        self.search_text.returnPressed.connect(self._on_search_return)
        self.search_text.installEventFilter(self)
        sc_layout.addWidget(search_icon)
        sc_layout.addWidget(self.search_text, 1)
        topbar_layout.addWidget(search_container)
        topbar_layout.addStretch(1)

        self.search_popup = SearchPopup(root)
        self.search_popup.result_selected.connect(self._on_search_result_selected)

        # Peer status badge
        self.peer_chip = QFrame()
        self.peer_chip.setObjectName("TopbarStatusPill")
        self.peer_chip.setFixedHeight(30)
        self.peer_chip.setMinimumWidth(96)
        chip_l = QHBoxLayout(self.peer_chip)
        chip_l.setContentsMargins(12, 0, 12, 0)
        chip_l.setSpacing(5)
        self.peer_chip_dot = QFrame()
        self.peer_chip_dot.setFixedSize(6, 6)
        self.peer_chip_dot.setStyleSheet(f"background: {TOKENS['textMute']}; border-radius: 3px;")
        self.peer_chip_text = QLabel(STATUS_LABELS["stopped"].lower())
        self.peer_chip_text.setStyleSheet(f"font-size: 12px; color: {TOKENS['textDim']}; font-weight: 650;")
        chip_l.addWidget(self.peer_chip_dot)
        chip_l.addWidget(self.peer_chip_text)
        chip_l.addStretch(1)
        topbar_layout.addWidget(self.peer_chip)

        # Change project
        self.change_project_button = QPushButton("Change Project")
        self.change_project_button.setIcon(lucide_icon("folder-input", 12, COLORS["text_body"]))
        self.change_project_button.setFixedHeight(34)
        self.change_project_button.setCursor(Qt.PointingHandCursor)
        self.change_project_button.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {TOKENS['border']};
                border-radius: 7px;
                color: {TOKENS['text']};
                font-size: 13px;
                font-weight: 700;
                padding: 0 13px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.03);
                border-color: {TOKENS['borderMid']};
            }}
        """)
        topbar_layout.addWidget(self.change_project_button)
        content_layout.addWidget(topbar)

        self.stack = ResponsiveStackedWidget()
        self.stack.setMinimumWidth(0)
        self.stack.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Ignored)
        self.project_picker = ProjectPickerPage(self.app_state.app_version)
        self.overview = OverviewPage()
        self.wizard = WizardPage()
        self.manifest = ManifestPage(self.key_service, self.manifest_service)
        self.telemetry = TelemetryPage(self.telemetry_service)
        self.run_peer = RunPeerPage(self.peer_run_service, self.process_manager)
        self.logs = LogsPage(self.process_manager)
        self.settings = SettingsPage(self.cli)

        self.project_picker.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        for key, page in [
            ("home", self.project_picker),
            ("overview", self.overview),
            ("wizard", self.wizard),
            ("manifest", self.manifest),
            ("telemetry", self.telemetry),
            ("run", self.run_peer),
            ("logs", self.logs),
            ("settings", self.settings),
        ]:
            page.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            self.stack.addWidget(page)
            self.page_index_by_key[key] = self.stack.indexOf(page)

        self.page_scroll = QScrollArea()
        self.page_scroll.setObjectName("PageScroll")
        self.page_scroll.setWidgetResizable(True)
        self.page_scroll.setFrameShape(QFrame.NoFrame)
        self.page_scroll.setWidget(self.stack)

        body_layout.addWidget(sidebar_frame)
        content_layout.addWidget(self.page_scroll, 1)
        body_layout.addWidget(content, 1)
        outer.addWidget(body, 1)
        self.setCentralWidget(root)
        root.installEventFilter(self)
        self.stack.setCurrentWidget(self.project_picker)
        self._refresh_chrome()

        # Toast container
        self.toast_widget: QFrame | None = None

    def _connect_signals(self) -> None:
        self.project_picker.project_selected.connect(self.open_project)
        self.project_picker.project_create_requested.connect(self.create_project)
        self.change_project_button.clicked.connect(lambda: self.set_page("home"))
        self.overview.navigate_requested.connect(self.navigate_to)
        self.wizard.navigate_requested.connect(self.navigate_to)
        self.wizard.wizard_progress_changed.connect(self._wizard_progress_changed)
        self.run_peer.navigate_requested.connect(self.navigate_to)
        self.manifest.config_changed.connect(self._save_config)
        self.telemetry.config_changed.connect(self._save_config)
        self.run_peer.config_changed.connect(self._save_config)
        self.manifest.log_requested.connect(self.logs.append_log)
        self.telemetry.log_requested.connect(self.logs.append_log)
        self.run_peer.log_requested.connect(self.logs.append_log)
        self.manifest.activity_recorded.connect(self._record_activity)
        self.telemetry.activity_recorded.connect(self._record_activity)
        self.run_peer.activity_recorded.connect(self._record_activity)
        self.process_manager.status_changed.connect(self._peer_status_changed)
        self.settings.binary_changed.connect(self._set_binary)
        self.settings.cli_changed.connect(self._set_cli_config)

    def _on_search_text_changed(self, text: str) -> None:
        if text.strip():
            container = self.search_text.parent()
            container_pos = container.mapTo(self.centralWidget(), container.rect().bottomLeft())
            popup_x = container_pos.x() - 8
            popup_y = container_pos.y() + 6
            self.search_popup.filter(text)
            self.search_popup.move(popup_x, popup_y)
            self.search_popup.show()
            self.search_popup.raise_()
        else:
            self.search_popup.hide()

    def _on_search_return(self) -> None:
        query = self.search_text.text().strip()
        if query and self.search_popup.isVisible():
            self.search_popup.select_current()

    def _on_search_result_selected(self, action: str, action_type: str) -> None:
        self.search_text.clear()
        if action_type == "page":
            self.set_page(action)
        elif action_type == "settings_section":
            self.set_page("settings")
        elif action_type == "project":
            self.open_project(action)

    def _record_activity(self, kind: str, label: str, meta: str) -> None:
        self.app_state.add_activity(kind, label, meta)
        if self.app_state.page == "overview":
            self._refresh_overview()

    def eventFilter(self, obj, event) -> bool:
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.MouseButtonPress and self.search_popup.isVisible():
            pos = event.globalPosition().toPoint()
            container = self.search_text.parent()
            in_container = container.rect().contains(container.mapFromGlobal(pos))
            in_popup = self.search_popup.rect().contains(self.search_popup.mapFromGlobal(pos))
            if not in_container and not in_popup:
                self.search_popup.hide()
        if obj is self.search_text and event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Down:
                self.search_popup.select_next()
                return True
            elif key == Qt.Key_Up:
                self.search_popup.select_previous()
                return True
            elif key == Qt.Key_Escape:
                if self.search_popup.isVisible():
                    self.search_popup.hide()
                    return True
        return super().eventFilter(obj, event)

    def notify(self, msg: str, duration_ms: int = 2000) -> None:
        """Show a toast notification in the bottom-right corner."""
        if self.toast_widget:
            self.toast_widget.deleteLater()
            self.toast_widget = None

        toast = QFrame(self.centralWidget())
        toast.setObjectName("Toast")
        toast.setStyleSheet(f"""
            QFrame#Toast {{
                background: {TOKENS['panel']};
                border: 1px solid {TOKENS['borderGold']};
                border-radius: 8px;
                color: {TOKENS['goldSoft']};
                font-size: 12.5px;
                font-weight: 500;
            }}
            QLabel {{
                background: transparent;
                color: {TOKENS['goldSoft']};
                font-size: 12.5px;
                font-weight: 500;
                padding: 10px 14px;
            }}
        """)
        layout = QHBoxLayout(toast)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(msg)
        layout.addWidget(label)
        toast.setFixedWidth(min(360, label.sizeHint().width() + 28))
        toast.adjustSize()

        # Position bottom-right
        parent = self.centralWidget()
        if parent:
            toast.move(
                parent.width() - toast.width() - 24,
                parent.height() - toast.height() - 24,
            )
        toast.show()
        toast.raise_()
        self.toast_widget = toast

        QTimer.singleShot(duration_ms, self._hide_toast)

    def _hide_toast(self) -> None:
        if self.toast_widget:
            self.toast_widget.deleteLater()
            self.toast_widget = None

    def set_page(self, page_key: str) -> None:
        if page_key in PAGE_BY_KEY:
            spec = PAGE_BY_KEY[page_key]
            if spec.requires_project and not self.config:
                return
            self.app_state.set_page(page_key)
            self.stack.setCurrentIndex(self.page_index_by_key[page_key])
            if page_key != "home" and self.config:
                self._record_activity("navigation", f"Navigated to {spec.label}", spec.hint)
            # Project picker should never scroll; other pages may need it
            from PySide6.QtCore import Qt
            self.page_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff if page_key == "home" else Qt.ScrollBarAsNeeded)
            self.page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            for key, button in self.nav_buttons.items():
                if key == "home":
                    continue
                active = key == page_key
                button.setChecked(active)
                icon_color = TOKENS["goldSoft"] if active else TOKENS["textMute"]
                button.setIcon(lucide_icon(PAGE_BY_KEY[key].icon, 16, icon_color, stroke=1.65))
            self._refresh_chrome()

    def navigate_to(self, page_name: str) -> None:
        self.set_page(PAGE_KEY_BY_LABEL.get(page_name, page_name))

    def open_project(self, workspace: str) -> None:
        workspace_path = Path(workspace).expanduser().resolve()
        workspace_path.mkdir(parents=True, exist_ok=True)
        self.store = ProjectStore(workspace_path)
        if self.store.path.exists():
            self.config = self.store.load()
        else:
            self.config = ProjectConfig(
                project_name=workspace_path.name,
                workspace_path=str(workspace_path),
            )
            self.store.save(self.config)
        self._bind_cli(self.config.cli)
        self.project_picker.remember_project(self.config)
        self._push_config()
        self.set_page("overview")
        self._record_activity("project", f"Opened project", workspace_path.name)

    def create_project(self, workspace: str, init_config) -> None:
        workspace_path = Path(workspace).expanduser().resolve()
        init_config.output_dir = str(workspace_path)
        result = self.project_init_service.init_project(workspace_path.parent, init_config)
        self.logs.append_log(f"$ {' '.join(result.command)}\n{result.stdout}{result.stderr}")
        if result.ok:
            self.open_project(str(workspace_path))
        else:
            self.notify("Project init failed")

    def show_project_picker(self) -> None:
        self.set_page("home")

    def toggle_sidebar(self) -> None:
        self.sidebar_collapsed = not self.sidebar_collapsed
        self.sidebar_frame.setFixedWidth(68 if self.sidebar_collapsed else 272)
        self.project_pill_container.setVisible(not self.sidebar_collapsed)
        self.workspace_label.setVisible(not self.sidebar_collapsed)
        self.footer_content.setVisible(not self.sidebar_collapsed)

        self.collapse_button.move(44 if self.sidebar_collapsed else 238, 122)
        icon_name = "chevron-right" if self.sidebar_collapsed else "chevron-left"
        self.collapse_button.setIcon(lucide_icon(icon_name, 14, TOKENS["textDim"], stroke=1.9))

        for key, button in self.nav_buttons.items():
            if key == "home":
                continue
            if hasattr(button, "setCollapsed"):
                button.setCollapsed(self.sidebar_collapsed)  # type: ignore[attr-defined]
            if self.sidebar_collapsed:
                button.setToolTip(f"{PAGE_BY_KEY[key].label} \u00b7 {PAGE_BY_KEY[key].hint}")
            else:
                label = button.property("label")
                button.setText(label)
                if hasattr(button, "setMeta"):
                    button.setMeta(button.property("hint"))  # type: ignore[attr-defined]
                button.setToolTip("")
        self._refresh_chrome()

    def _push_config(self) -> None:
        if not self.config:
            return
        self.app_state.project_name = self.config.project_name
        self.project_label.setText(self.config.project_name)
        self.manifest.set_config(self.config)
        self.telemetry.set_config(self.config)
        self.run_peer.set_config(self.config)
        self.settings.set_config(self.config)
        self._refresh_overview()

    def _save_config(self, config: ProjectConfig) -> None:
        self.config = config
        self._bind_cli(config.cli)
        if self.store:
            self.store.save(config)
        self._refresh_overview()

    def _refresh_overview(self) -> None:
        artifacts = ProjectArtifacts.from_config(self.config) if self.config else None
        self.overview.refresh(self.config, artifacts, self.peer_status, self.app_state.activity)
        if artifacts:
            ready_count = sum([artifacts.manifest_ready, artifacts.creator_key_ready, artifacts.telemetry_ready])
            self.app_state.readiness = {
                "creator": artifacts.creator_key_ready,
                "manifest": artifacts.manifest_ready,
                "telemetry": artifacts.telemetry_ready,
            }
        self._refresh_chrome()

    def _peer_status_changed(self, status: str) -> None:
        self.app_state.peer_state = PeerState(status) if status in {state.value for state in PeerState} else PeerState.FAILED
        self._refresh_overview()

    @property
    def peer_status(self) -> str:
        return self.app_state.peer_state.value

    def _refresh_chrome(self) -> None:
        project = self.app_state.project_name or APP_COPY["no_project"]
        self.project_label.setText(project)

        project_pill = project if self.config else APP_COPY["no_project_pill"]
        self.sidebar_project_button.setText(f"\u25cf  {project_pill}")

        done = len(self.app_state.wizard_completed)
        total = 6
        self.setup_count_label.setText(f"{done}/{total}")
        progress_width = self.sidebar_progress.width() or 232
        self.sidebar_progress_fill.setGeometry(0, 0, int(progress_width * (done / max(1, total))), 4)

        state = self.app_state.peer_state
        color = PEER_STATE_COLORS[state]
        self.peer_chip_dot.setStyleSheet(f"background: {color}; border-radius: 3px;")
        self.peer_chip_text.setText(STATUS_LABELS[state.value].lower())

        self.peer_dot_label.setStyleSheet(f"font-size: 7px; color: {color};")
        self.peer_status_text.setText(f"{APP_COPY['peer']} \u00b7 {STATUS_LABELS[state.value].lower()}")

        for key, button in self.nav_buttons.items():
            if key == "home":
                continue
            spec = PAGE_BY_KEY[key]
            locked = spec.requires_project and not self.config
            active = self.app_state.page == key
            button.setEnabled(not locked)
            if not self.sidebar_collapsed:
                label = button.property("label")
                button.setText(label)
                if hasattr(button, "setMeta"):
                    button.setMeta(button.property("hint"))  # type: ignore[attr-defined]
            icon_name = "lock" if locked else spec.icon
            icon_color = COLORS["text_disabled"] if locked else (TOKENS["goldSoft"] if active else TOKENS["textMute"])
            icon_sz = 14 if locked else 16
            button.setIcon(lucide_icon(icon_name, icon_sz, icon_color, stroke=1.7 if not locked else 1.5))

    def _set_binary(self, binary: str) -> None:
        if self.config:
            self.config.cli.binary = binary or "quinkgl"
            self._save_config(self.config)
        else:
            self._bind_cli(CliConfig(binary=binary or "quinkgl"))

    def _set_cli_config(self, cli_config: CliConfig) -> None:
        if self.config:
            self.config.cli = cli_config
            self._save_config(self.config)
        else:
            self._bind_cli(cli_config)

    def _bind_cli(self, cli_config: CliConfig | None = None) -> None:
        self.cli = QuinkGLCli(cli_config)
        self.key_service.cli = self.cli
        self.manifest_service.cli = self.cli
        self.telemetry_service.cli = self.cli
        self.peer_run_service.cli = self.cli
        self.project_init_service.cli = self.cli
        self.settings.set_cli(self.cli)

    def _wizard_progress_changed(self, completed: set, total: int) -> None:
        self.app_state.wizard_completed = sorted(completed)
        self._refresh_chrome()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.toast_widget:
            parent = self.centralWidget()
            if parent:
                self.toast_widget.move(
                    parent.width() - self.toast_widget.width() - 24,
                    parent.height() - self.toast_widget.height() - 24,
                )
