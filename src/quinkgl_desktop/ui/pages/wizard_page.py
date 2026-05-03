from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from quinkgl_desktop.ui.i18n import PAGES_COPY, WIZARD_COPY
from quinkgl_desktop.ui.icons import lucide_icon
from quinkgl_desktop.ui.pages.base import card, card_header, page_header, progress_bar
from quinkgl_desktop.ui.tokens import COLORS
from quinkgl_desktop.ui.wizard import WIZARD_STEPS


class WizardPage(QWidget):
    navigate_requested = Signal(str)
    wizard_progress_changed = Signal(set, int)  # completed indices, total

    def __init__(self) -> None:
        super().__init__()
        self.current = 0
        self.completed: set[int] = set()
        self.step_rows: list[tuple[QFrame, QLabel, QFrame, QFrame]] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 40, 44, 44)
        layout.setSpacing(18)
        page_copy = PAGES_COPY["wizard"]
        layout.addWidget(page_header(
            page_copy["title"],
            page_copy["subtitle"],
            eyebrow=page_copy["eyebrow"],
        )[0])

        body = QHBoxLayout()
        body.setSpacing(22)

        # Left rail
        rail, rail_layout = card(margins=(0, 0, 0, 0))
        rail.setFixedWidth(326)
        rail_header = QVBoxLayout()
        rail_header.setContentsMargins(22, 20, 22, 16)
        rail_header.setSpacing(8)
        progress_eyebrow = QLabel(WIZARD_COPY["progress"])
        progress_eyebrow.setObjectName("CardTitle")
        progress_text = QLabel(f"{len(self.completed)} of {len(WIZARD_STEPS)} steps complete")
        progress_text.setStyleSheet(f"font-size: 13px; color: {COLORS['wizard_progress_text']};")
        rail_header.addWidget(progress_eyebrow)
        rail_header.addWidget(progress_text)
        self.progress_slot = QVBoxLayout()
        self.progress_slot.setContentsMargins(0, 8, 0, 8)
        rail_header.addLayout(self.progress_slot)
        rail_layout.addLayout(rail_header)

        steps_container = QVBoxLayout()
        steps_container.setContentsMargins(12, 0, 12, 14)
        steps_container.setSpacing(0)
        for i, step in enumerate(WIZARD_STEPS):
            row = QFrame()
            row.setObjectName("WizardStepRow")
            row.setMinimumHeight(56)
            row.setMaximumHeight(56)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(7)

            marker_col = QVBoxLayout()
            marker_col.setContentsMargins(0, 2, 0, 0)
            marker_col.setSpacing(0)
            marker = QLabel()
            marker.setObjectName("WizardStepCircle")
            marker.setFixedSize(22, 22)
            marker.setAlignment(Qt.AlignCenter)
            line = QFrame()
            line.setObjectName("WizardStepLine")
            line.setFixedWidth(1)
            marker_col.addWidget(marker, 0, Qt.AlignHCenter)
            marker_col.addWidget(line, 1, Qt.AlignHCenter)

            btn = QFrame()
            btn.setObjectName("WizardStepButton")
            btn.setMinimumHeight(48)
            btn.setCursor(Qt.PointingHandCursor)
            btn.mousePressEvent = lambda event, idx=i: self.set_current(idx)  # type: ignore[method-assign]
            btn_layout = QVBoxLayout(btn)
            btn_layout.setContentsMargins(10, 6, 10, 6)
            btn_layout.setSpacing(2)
            lbl = QLabel(step.label)
            lbl.setStyleSheet(f"font-size: 12.5px; color: {COLORS['wizard_step_label']};")
            desc = QLabel(step.description)
            desc.setStyleSheet(f"font-size: 11px; color: {COLORS['wizard_step_desc']};")
            desc.setWordWrap(True)
            btn_layout.addWidget(lbl)
            btn_layout.addWidget(desc)

            row_layout.addLayout(marker_col)
            row_layout.addWidget(btn, 1)
            self.step_rows.append((row, marker, line, btn))
            steps_container.addWidget(row)
        rail_layout.addLayout(steps_container)
        body.addWidget(rail)

        # Right panel
        panel, panel_layout = card()
        self.step_eyebrow = QLabel()
        self.step_eyebrow.setObjectName("CardEyebrow")
        self.step_title = QLabel()
        self.step_title.setObjectName("PageTitle")
        self.step_title.setStyleSheet("font-size: 18px;")
        self.step_desc = QLabel()
        self.step_desc.setObjectName("PageSubtitle")
        self.step_desc.setWordWrap(True)

        header_row = QHBoxLayout()
        text_col = QVBoxLayout()
        text_col.addWidget(self.step_eyebrow)
        text_col.addWidget(self.step_title)
        text_col.addWidget(self.step_desc)
        header_row.addLayout(text_col, 1)
        self.open_button = QPushButton(f"{WIZARD_COPY['open_full_page']}  →")
        self.open_button.setProperty("ghost", True)
        self.open_button.clicked.connect(self.open_full_page)
        header_row.addWidget(self.open_button, 0, Qt.AlignTop)
        panel_layout.addLayout(header_row)

        info = QFrame()
        info.setObjectName("InfoCallout")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(18, 16, 18, 16)
        info_layout.setSpacing(12)
        info_label = QLabel(WIZARD_COPY["promise"])
        info_label.setObjectName("WizardInfoText")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        for text in WIZARD_COPY["promise_items"]:
            item = QHBoxLayout()
            item.setSpacing(8)
            check = QLabel("✓")
            check.setStyleSheet(f"color: {COLORS['gold']}; font-size: 12px;")
            txt = QLabel(text)
            txt.setStyleSheet(f"color: {COLORS['text_body']}; font-size: 13px;")
            item.addWidget(check)
            item.addWidget(txt, 1)
            info_layout.addLayout(item)
        panel_layout.addWidget(info)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {COLORS['border_default']};")
        panel_layout.addWidget(sep)
        panel_layout.addStretch(1)

        controls = QHBoxLayout()
        self.back_button = QPushButton(f"←  {WIZARD_COPY['back']}")
        self.back_button.setProperty("ghost", True)
        self.back_button.clicked.connect(lambda: self.set_current(max(0, self.current - 1)))
        self.skip_button = QPushButton(WIZARD_COPY["skip"])
        self.skip_button.setObjectName("WizardSkipButton")
        self.skip_button.setProperty("secondary", True)
        self.skip_button.setFixedSize(88, 38)
        self.skip_button.clicked.connect(lambda: self.set_current(min(len(WIZARD_STEPS) - 1, self.current + 1)))
        self.done_button = QPushButton(f"{WIZARD_COPY['mark_complete']}  →")
        self.done_button.setObjectName("WizardDoneButton")
        self.done_button.setProperty("primary", True)
        self.done_button.setFixedSize(148, 38)
        self.done_button.clicked.connect(self.mark_done)
        controls.addWidget(self.back_button)
        controls.addStretch(1)
        controls.addWidget(self.skip_button)
        controls.addWidget(self.done_button)
        panel_layout.addLayout(controls)
        body.addWidget(panel, 1)
        layout.addLayout(body)
        layout.addStretch(1)
        self.render()
        self.wizard_progress_changed.emit(self.completed.copy(), len(WIZARD_STEPS))

    def set_current(self, index: int) -> None:
        self.current = max(0, min(len(WIZARD_STEPS) - 1, index))
        self.render()

    def mark_done(self) -> None:
        self.completed.add(self.current)
        if self.current < len(WIZARD_STEPS) - 1:
            self.current += 1
        self.wizard_progress_changed.emit(self.completed.copy(), len(WIZARD_STEPS))
        self.render()

    def open_full_page(self) -> None:
        self.navigate_requested.emit(WIZARD_STEPS[self.current].target_page)

    def render(self) -> None:
        while self.progress_slot.count():
            item = self.progress_slot.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.progress_slot.addWidget(progress_bar(len(self.completed) / len(WIZARD_STEPS)))

        for i, (row_widget, marker, line, btn) in enumerate(self.step_rows):
            step = WIZARD_STEPS[i]
            is_done = i in self.completed
            is_current = i == self.current
            row_widget.setProperty("active", is_current)
            marker.setText("✓" if is_done else str(i + 1))
            marker.setProperty("done", is_done)
            marker.setProperty("current", is_current)
            line.setVisible(i < len(WIZARD_STEPS) - 1)
            line.setProperty("done", is_done)
            for widget in (row_widget, marker, line):
                widget.style().unpolish(widget)
                widget.style().polish(widget)
            btn.setProperty("active", is_current)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            # Rebuild button contents
            btn_layout = btn.layout()
            if btn_layout is None:
                btn_layout = QVBoxLayout(btn)
            else:
                while btn_layout.count():
                    item = btn_layout.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
                    elif item.layout():
                        while item.layout().count():
                            sub = item.layout().takeAt(0)
                            if sub.widget():
                                sub.widget().setParent(None)
            btn_layout.setContentsMargins(10, 6, 10, 6)
            btn_layout.setSpacing(2)
            lbl = QLabel(step.label)
            desc = QLabel(step.description)
            desc.setWordWrap(True)
            if is_current:
                lbl.setStyleSheet(f"font-size: 13px; color: {COLORS['text_primary']}; font-weight: 700;")
                desc.setStyleSheet(f"font-size: 11px; color: {COLORS['text_dim']};")
                now = QLabel(WIZARD_COPY["now"])
                now.setStyleSheet(f"font-size: 10px; color: {COLORS['gold_bright']}; background: rgba(224,184,77,0.10); border: 1px solid rgba(224,184,77,0.26); border-radius: 5px; padding: 1px 6px; letter-spacing: 1.2px; font-weight: 700;")
                row = QHBoxLayout()
                row.setSpacing(8)
                row.addWidget(lbl)
                row.addWidget(now)
                row.addStretch(1)
                btn_layout.addLayout(row)
            elif is_done:
                lbl.setStyleSheet(f"font-size: 12.5px; color: {COLORS['text_body']};")
                desc.setStyleSheet(f"font-size: 11px; color: {COLORS['text_dim']};")
                btn_layout.addWidget(lbl)
            else:
                lbl.setStyleSheet(f"font-size: 12.5px; color: {COLORS['text_muted']};")
                desc.setStyleSheet(f"font-size: 11px; color: {COLORS['text_dim']};")
                btn_layout.addWidget(lbl)
            btn_layout.addWidget(desc)

        step = WIZARD_STEPS[self.current]
        self.step_eyebrow.setText(WIZARD_COPY["step_of"].format(step=self.current + 1, total=len(WIZARD_STEPS)).upper())
        self.step_title.setText(step.label)
        self.step_desc.setText(step.description)
        self.back_button.setEnabled(self.current > 0)
        self.skip_button.setEnabled(self.current < len(WIZARD_STEPS) - 1)
        self.done_button.setText(WIZARD_COPY["finish_setup"] if self.current == len(WIZARD_STEPS) - 1 else WIZARD_COPY["mark_complete"] + "  →")
