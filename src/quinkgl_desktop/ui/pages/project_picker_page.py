from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from quinkgl_desktop.core.models import ProjectConfig, ProjectInitConfig
from quinkgl_desktop.core.recent_projects_store import load_recent_projects, save_recent_projects
from quinkgl_desktop.ui.i18n import PROJECT_PICKER_COPY
from quinkgl_desktop.ui.icons import lucide_icon
from quinkgl_desktop.ui.pages.base import badge, card, muted_label
from quinkgl_desktop.ui.tokens import COLORS


class ProjectPickerPage(QWidget):
    project_selected = Signal(str)
    project_create_requested = Signal(str, object)

    def __init__(self, app_version: str = "0.1") -> None:
        super().__init__()
        self.app_version = app_version
        self.recent_projects: list[dict[str, str]] = load_recent_projects()
        self.recent_frame: QFrame | None = None
        self.recent_rows_layout: QVBoxLayout | None = None
        self.empty_recent_label: QLabel | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 40, 44, 44)
        layout.setSpacing(20)

        layout.addWidget(self._hero())

        lower = QHBoxLayout()
        lower.setSpacing(18)
        lower.addWidget(self._recent_projects(), 1, Qt.AlignTop)
        rail = QVBoxLayout()
        rail.setSpacing(14)
        rail.addWidget(self._first_time())
        rail.addStretch(1)
        rail_widget = QWidget()
        rail_widget.setObjectName("FirstTimeRail")
        rail_widget.setLayout(rail)
        rail_widget.setMinimumWidth(560)
        rail_widget.setMaximumWidth(620)
        rail_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        lower.addWidget(rail_widget, 9, Qt.AlignTop)
        layout.addLayout(lower)
        layout.addStretch(1)

    def _logo_path(self) -> Path:
        project_logo = Path(__file__).resolve().parents[4] / "quinkgl_logo.png"
        bundled_logo = Path(__file__).resolve().parents[2] / "resources" / "quinkgl_logo.png"
        return project_logo if project_logo.exists() else bundled_logo

    def _icon(self, name: str, size: int = 13, color: str = COLORS["gold_bright"]) -> QLabel:
        label = QLabel()
        label.setPixmap(lucide_icon(name, size, color).pixmap(size, size))
        label.setFixedSize(size, size)
        return label

    def _hero(self) -> QFrame:
        hero = QFrame()
        hero.setObjectName("HeroCard")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(32, 24, 28, 24)
        hero_layout.setSpacing(36)

        text = QVBoxLayout()
        text.setSpacing(16)
        eyebrow_row = QHBoxLayout()
        eyebrow_row.setSpacing(8)
        eyebrow_row.addWidget(self._icon("sparkles", 13))
        eyebrow = QLabel(PROJECT_PICKER_COPY["eyebrow"].format(version=self.app_version).upper())
        eyebrow.setObjectName("PageEyebrow")
        eyebrow_row.addWidget(eyebrow)
        eyebrow_row.addStretch(1)
        text.addLayout(eyebrow_row)

        title_a = QLabel(PROJECT_PICKER_COPY["headline_a"])
        title_a.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 46px; font-weight: 760;")
        title_b = QLabel(PROJECT_PICKER_COPY["headline_b"])
        title_b.setStyleSheet(f"color: {COLORS['gold_bright']}; font-size: 42px; font-weight: 760;")
        text.addWidget(title_a)
        text.addWidget(title_b)
        subtitle = muted_label(PROJECT_PICKER_COPY["subtitle"])
        subtitle.setMaximumWidth(520)
        text.addWidget(subtitle)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        create_button = QPushButton(PROJECT_PICKER_COPY["create"])
        create_button.setIcon(lucide_icon("plus", 13, COLORS["text_disabled"]))
        create_button.setProperty("primary", True)
        create_button.setFixedHeight(40)
        create_button.clicked.connect(lambda: self._create_project("minimal"))
        open_button = QPushButton(PROJECT_PICKER_COPY["open"])
        open_button.setIcon(lucide_icon("folder-open", 13, COLORS["text_body"]))
        open_button.setFixedHeight(40)
        open_button.clicked.connect(self._select_directory)
        actions.addWidget(create_button)
        actions.addWidget(open_button)
        actions.addStretch(1)
        text.addLayout(actions)
        hero_layout.addLayout(text, 7)

        medallion = QFrame()
        medallion.setObjectName("LogoBackdrop")
        medallion.setFixedSize(220, 220)
        medallion_layout = QVBoxLayout(medallion)
        medallion_layout.setContentsMargins(12, 12, 12, 12)
        ring = QFrame()
        ring.setObjectName("LogoRing")
        ring_layout = QVBoxLayout(ring)
        ring_layout.setContentsMargins(20, 20, 20, 20)
        logo = QLabel()
        logo.setObjectName("BrandLogo")
        logo.setAlignment(Qt.AlignCenter)
        logo.setPixmap(QPixmap(str(self._logo_path())).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        ring_layout.addWidget(logo, alignment=Qt.AlignCenter)
        medallion_layout.addWidget(ring)
        hero_layout.addWidget(medallion, 0, Qt.AlignRight | Qt.AlignVCenter)
        return hero

    def _recent_projects(self) -> QFrame:
        frame, layout = card(padded=False)
        frame.setObjectName("RecentProjectsCard")
        frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.recent_frame = frame
        header = QHBoxLayout()
        header.setContentsMargins(20, 14, 20, 12)
        header.setSpacing(8)
        header.addWidget(self._icon("clock", 13))
        title = QLabel(PROJECT_PICKER_COPY["recent_title"])
        title.setObjectName("CardTitle")
        header.addWidget(title)
        header.addStretch(1)
        search = QLineEdit()
        search.setObjectName("RecentProjectFilter")
        search.setPlaceholderText(PROJECT_PICKER_COPY["recent_filter"])
        search.setMinimumWidth(180)
        search.setMaximumWidth(276)
        search.setFixedHeight(34)
        search.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.recent_search = search
        header.addWidget(search)
        layout.addLayout(header)

        self.recent_rows_layout = QVBoxLayout()
        self.recent_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_rows_layout.setSpacing(0)
        layout.addLayout(self.recent_rows_layout)
        self._render_recent_projects()
        return frame

    def remember_project(self, config: ProjectConfig) -> None:
        manifest = config.manifest_path or config.manifest.output_path or "-"
        status = "ready" if config.manifest_path else "draft"
        item = {
            "name": config.project_name,
            "path": config.workspace_path,
            "manifest": manifest,
            "status": status,
        }
        self.recent_projects = [
            project for project in self.recent_projects
            if Path(project["path"]).expanduser() != Path(config.workspace_path).expanduser()
        ]
        self.recent_projects.insert(0, item)
        self.recent_projects = self.recent_projects[:5]
        save_recent_projects(self.recent_projects)
        self._render_recent_projects()

    def _render_recent_projects(self) -> None:
        if self.recent_rows_layout is None:
            return

        while self.recent_rows_layout.count():
            item = self.recent_rows_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        if not self.recent_projects:
            self.empty_recent_label = muted_label("Open a project to add it here.")
            self.empty_recent_label.setStyleSheet(f"font-size: 13px; color: {COLORS['text_muted']}; padding: 8px 20px 18px 20px;")
            self.recent_rows_layout.addWidget(self.empty_recent_label)
            self.recent_search.hide()
            self._sync_recent_card_height()
            return

        self.empty_recent_label = None
        self.recent_search.show()
        for project in self.recent_projects:
            row = QFrame()
            row.setObjectName("ProjectRow")
            row.setCursor(Qt.PointingHandCursor)
            row.setMinimumHeight(76)
            row.setMaximumHeight(76)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(20, 8, 16, 8)
            row_layout.setSpacing(12)
            copy = QVBoxLayout()
            copy.setSpacing(4)
            title = QLabel(project["name"])
            title.setStyleSheet(f"font-size: 14px; color: {COLORS['text_primary']}; font-weight: 720;")
            meta = QLabel(f"{project['path']} \u00b7 {project['manifest']}")
            meta.setStyleSheet(f"font-size: 12px; color: {COLORS['text_muted']}; font-family: 'JetBrains Mono';")
            meta.setWordWrap(False)
            meta.setToolTip(meta.text())
            meta.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
            copy.addWidget(title)
            copy.addWidget(meta)
            row_layout.addLayout(copy, 1)
            status = project["status"]
            status_badge = badge(status, "green" if status == "ready" else "neutral")
            status_badge.setFixedHeight(24)
            row_layout.addWidget(status_badge, 0, Qt.AlignVCenter)
            remove_btn = QPushButton()
            remove_btn.setFixedSize(28, 28)
            remove_btn.setCursor(Qt.ArrowCursor)
            remove_btn.setIcon(lucide_icon("x", 13, COLORS["text_muted"]))
            remove_btn.setStyleSheet(
                f"QPushButton {{ background: transparent; border: none; padding: 4px; }}"
                f"QPushButton:hover {{ background: {COLORS['bg_input']}; border-radius: 6px; }}"
            )
            remove_btn.clicked.connect(lambda _checked=False, path=project["path"]: self._remove_project(path))
            row_layout.addWidget(remove_btn, 0, Qt.AlignVCenter)
            row.mousePressEvent = lambda event, path=project["path"]: self.project_selected.emit(str(Path(path).expanduser()))  # type: ignore[method-assign]
            self.recent_rows_layout.addWidget(row)
        self._sync_recent_card_height()

    def _sync_recent_card_height(self) -> None:
        if self.recent_frame is None:
            return
        row_count = len(self.recent_projects)
        height = 120 if row_count == 0 else 74 + (row_count * 76)
        self.recent_frame.setMinimumHeight(height)
        self.recent_frame.setMaximumHeight(height)

    def _first_time(self) -> QFrame:
        frame, layout = card()
        frame.setObjectName("FirstTimeCard")
        header = QHBoxLayout()
        header.setSpacing(8)
        header.addWidget(self._icon("zap", 14))
        title_col = QVBoxLayout()
        title = QLabel(PROJECT_PICKER_COPY["first_time_title"])
        title.setObjectName("CardTitle")
        title_col.addWidget(title)
        title_col.addWidget(muted_label(PROJECT_PICKER_COPY["first_time_subtitle"]))
        header.addLayout(title_col)
        layout.addLayout(header)
        for label, icon, action_key in PROJECT_PICKER_COPY["resources"]:
            link = QPushButton(label)
            link.setObjectName("NavButton")
            link.setIcon(lucide_icon(icon, 13, COLORS["gold_deep"]))
            if action_key == "guide":
                link.clicked.connect(self._show_quickstart_guide)
            elif action_key == "about":
                link.clicked.connect(self._show_about_quinkgl)
            elif action_key == "community":
                link.clicked.connect(self._open_community)
            layout.addWidget(link)
        return frame

    def _show_quickstart_guide(self) -> None:
        msg = QMessageBox(self)
        msg.setWindowTitle(PROJECT_PICKER_COPY["first_time_guide_title"])
        msg.setText(PROJECT_PICKER_COPY["first_time_guide_text"])
        msg.setIcon(QMessageBox.Information)
        msg.exec()

    def _show_about_quinkgl(self) -> None:
        msg = QMessageBox(self)
        msg.setWindowTitle(PROJECT_PICKER_COPY["first_time_about_title"])
        msg.setText(PROJECT_PICKER_COPY["first_time_about_text"])
        msg.setIcon(QMessageBox.Information)
        msg.exec()

    def _open_community(self) -> None:
        url = PROJECT_PICKER_COPY.get("first_time_community_url", "https://github.com/QuinkGL")
        QDesktopServices.openUrl(url)

    def _remove_project(self, path: str) -> None:
        self.recent_projects = [
            p for p in self.recent_projects
            if Path(p["path"]).expanduser() != Path(path).expanduser()
        ]
        save_recent_projects(self.recent_projects)
        self._render_recent_projects()

    def _select_directory(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select QuinkGL workspace")
        if path:
            self.project_selected.emit(path)

    def _create_project(self, template: str) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Create QuinkGL workspace", "quinkgl-project")
        if path:
            init_config = ProjectInitConfig(output_dir=path, template=template)
            self.project_create_requested.emit(path, init_config)
