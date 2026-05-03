from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from quinkgl_desktop.ui.icons import lucide_icon
from quinkgl_desktop.ui.tokens import COLORS, RADII, SPACING, TOKENS


def muted_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setProperty("muted", True)
    label.setWordWrap(True)
    return label


def accent_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setProperty("accent", True)
    label.setWordWrap(True)
    return label


def refresh_style(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def card(
    padded: bool = True,
    margins: tuple[int, int, int, int] = (
        SPACING["card_x"],
        SPACING["card_y"],
        SPACING["card_x"],
        SPACING["card_y"],
    ),
) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setProperty("card", True)
    layout = QVBoxLayout(frame)
    if padded:
        layout.setContentsMargins(*margins)
    else:
        layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(14)
    return frame, layout


def panel(
    padded: bool = True,
    margins: tuple[int, int, int, int] = (
        SPACING["card_x"],
        SPACING["card_y"],
        SPACING["card_x"],
        SPACING["card_y"],
    ),
) -> tuple[QFrame, QVBoxLayout]:
    """Panel primitive matching prototype Panel."""
    return card(padded=padded, margins=margins)


def page_header(title: str, subtitle: str, eyebrow: str | None = None, actions: QWidget | None = None) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("PageHeader")
    outer = QHBoxLayout(frame)
    outer.setContentsMargins(0, 0, 0, 20)
    outer.setSpacing(16)
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    if eyebrow:
        eyebrow_label = QLabel(eyebrow.upper())
        eyebrow_label.setObjectName("PageEyebrow")
        layout.addWidget(eyebrow_label)
    title_label = QLabel(title)
    title_label.setObjectName("PageTitle")
    subtitle_label = muted_label(subtitle)
    subtitle_label.setObjectName("PageSubtitle")
    layout.addWidget(title_label)
    layout.addWidget(subtitle_label)
    outer.addLayout(layout, 1)
    if actions:
        outer.addWidget(actions, 0, Qt.AlignTop)
    return frame, layout


def card_header(title: str, subtitle: str | None = None, eyebrow: str | None = None, action: QWidget | None = None) -> QFrame:
    frame = QFrame()
    frame.setObjectName("TransparentFrame")
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    text_layout = QVBoxLayout()
    text_layout.setContentsMargins(0, 0, 0, 0)
    text_layout.setSpacing(5)
    if eyebrow:
        eyebrow_label = QLabel(eyebrow.upper())
        eyebrow_label.setObjectName("CardEyebrow")
        text_layout.addWidget(eyebrow_label)
    title_label = QLabel(title)
    title_label.setObjectName("CardTitle")
    text_layout.addWidget(title_label)
    if subtitle:
        subtitle_label = muted_label(subtitle)
        subtitle_label.setObjectName("CardSubtitle")
        text_layout.addWidget(subtitle_label)
    layout.addLayout(text_layout, 1)
    if action:
        layout.addWidget(action, 0, Qt.AlignTop)
    return frame


def section_label(text: str) -> QLabel:
    label = QLabel(text.upper())
    label.setObjectName("SectionLabel")
    return label


def pill(text: str, tone: str = "neutral") -> QLabel:
    label = QLabel(text)
    label.setProperty("badge", tone)
    return label


def badge(text: str, tone: str = "neutral") -> QLabel:
    return pill(text, tone)


def icon_button(text: str, primary: bool = False, danger: bool = False, ghost: bool = False) -> QPushButton:
    button = QPushButton(text)
    if primary:
        button.setProperty("primary", True)
    if danger:
        button.setProperty("danger", True)
    if ghost:
        button.setProperty("ghost", True)
    return button


def styled_button(
    text: str = "",
    variant: str = "secondary",
    size: str = "md",
    icon: str | None = None,
    icon_size: int = 14,
    icon_color: str = COLORS["text_muted"],
    parent: QWidget | None = None,
) -> QPushButton:
    """Create a button matching reference Button primitive."""
    btn = QPushButton(text, parent)
    btn.setProperty(variant, True)
    heights = {"sm": 32, "md": 36, "lg": 40}
    btn.setFixedHeight(heights.get(size, 36))
    if icon:
        btn.setIcon(lucide_icon(icon, icon_size, icon_color))
    return btn


def gold_button(
    text: str = "",
    variant: str = "primary",
    size: str = "md",
    icon: str | None = None,
    icon_size: int = 13,
    parent: QWidget | None = None,
) -> QPushButton:
    """GoldButton primitive matching prototype."""
    btn = QPushButton(text, parent)
    heights = {"sm": 32, "md": 36, "lg": 40}
    btn.setFixedHeight(heights.get(size, 36))
    if variant == "primary":
        btn.setProperty("primary", True)
    elif variant == "outline":
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {TOKENS['borderMid']};
                border-radius: {RADII['control']}px;
                color: {TOKENS['text']};
                font-size: 13px;
                font-weight: 650;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.03);
                border-color: rgba(255,255,255,0.15);
            }}
        """)
    elif variant == "soft":
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {TOKENS['goldSurface']};
                border: 1px solid {TOKENS['borderGold']};
                border-radius: {RADII['control']}px;
                color: {TOKENS['goldSoft']};
                font-size: 13px;
                font-weight: 700;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background: rgba(224,184,77,0.14);
                border-color: rgba(224,184,77,0.45);
            }}
        """)
    elif variant == "ghost":
        btn.setProperty("ghost", True)
    if icon:
        btn.setIcon(lucide_icon(icon, icon_size, COLORS["text_disabled"] if variant == "primary" else COLORS["text_muted"]))
    return btn


def input_field(
    value: str = "",
    placeholder: str = "",
    mono: bool = False,
    prefix: QWidget | None = None,
    suffix: QWidget | None = None,
    parent: QWidget | None = None,
) -> QFrame:
    """Create an input with optional prefix/suffix matching reference Input primitive."""
    frame = QFrame()
    frame.setObjectName("InputFrame")
    frame.setStyleSheet(f"""
        QFrame#InputFrame {{
            background: {TOKENS['input']};
            border: 1px solid {TOKENS['border']};
            border-radius: {RADII['control']}px;
        }}
        QFrame#InputFrame:focus-within {{
            border-color: {TOKENS['borderGold']};
        }}
    """)
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(8, 0, 8, 0)
    layout.setSpacing(6)
    if prefix:
        layout.addWidget(prefix)
    edit = QLineEdit(value, parent)
    edit.setPlaceholderText(placeholder)
    edit.setStyleSheet(f"""
        QLineEdit {{
            background: transparent;
            border: none;
            color: {TOKENS['text']};
            font-size: 13px;
            padding: 6px 0px;
        }}
    """)
    if mono:
        edit.setStyleSheet(edit.styleSheet() + "font-family: 'JetBrains Mono', 'SFMono-Regular', monospace; letter-spacing: -0.3px;")
    layout.addWidget(edit, 1)
    if suffix:
        layout.addWidget(suffix)
    frame.edit = edit  # type: ignore[attr-defined]
    return frame


def field(label: str, widget: QWidget, hint: str | None = None) -> QFrame:
    frame = QFrame()
    frame.setObjectName("TransparentFrame")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    title = QLabel(label)
    title.setObjectName("FieldLabel")
    row.addWidget(title)
    row.addStretch(1)
    if hint:
        hint_label = QLabel(hint)
        hint_label.setObjectName("FieldHint")
        row.addWidget(hint_label)
    layout.addLayout(row)
    layout.addWidget(widget)
    return frame


def progress_bar(percent: float) -> QFrame:
    percent = max(0.0, min(1.0, percent))
    track = QFrame()
    track.setObjectName("ProgressTrack")
    track.setFixedHeight(5)
    layout = QHBoxLayout(track)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    fill = QFrame()
    fill.setObjectName("ProgressFill")
    fill.setFixedHeight(5)
    fill.setMinimumWidth(0)
    layout.addWidget(fill, max(1, int(percent * 1000)))
    spacer = QFrame()
    spacer.setStyleSheet("background: transparent;")
    layout.addWidget(spacer, max(1, int((1 - percent) * 1000)))
    return track


def separator() -> QFrame:
    line = QFrame()
    line.setFixedHeight(1)
    line.setStyleSheet(f"background: {TOKENS['border']};")
    return line


def metric_chip(title: str, value: str, tone: str = "neutral") -> QFrame:
    frame = QFrame()
    frame.setObjectName("MetricChip")
    frame.setProperty("tone", tone)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(10, 8, 10, 8)
    layout.setSpacing(2)
    title_label = QLabel(title.upper())
    title_label.setObjectName("MetricTitle")
    value_label = QLabel(value)
    value_label.setObjectName("MetricValue")
    layout.addWidget(title_label)
    layout.addWidget(value_label)
    return frame


def step_card(index: int, title: str, body: str, status: str, tone: str = "neutral") -> QFrame:
    frame, layout = card()
    header = QHBoxLayout()
    number = QLabel(f"{index:02d}")
    number.setObjectName("StepNumber")
    title_label = QLabel(title)
    title_label.setObjectName("CardTitle")
    status_label = pill(status, tone)
    header.addWidget(number)
    header.addWidget(title_label)
    header.addStretch(1)
    header.addWidget(status_label)
    layout.addLayout(header)
    layout.addWidget(muted_label(body))
    return frame


def row_card(title: str, body: str, marker: str = "\u2022") -> QFrame:
    frame, layout = card()
    header = QHBoxLayout()
    mark = QLabel(marker)
    mark.setObjectName("CardMarker")
    title_label = QLabel(title)
    title_label.setObjectName("CardTitle")
    header.addWidget(mark)
    header.addWidget(title_label)
    header.addStretch(1)
    layout.addLayout(header)
    layout.addWidget(muted_label(body))
    return frame


def segmented(
    options: list[tuple[str, str]],
    current: str,
    callback: Callable[[str], None],
    parent: QWidget | None = None,
) -> QFrame:
    """Segmented toggle matching reference Segmented primitive."""
    frame = QFrame()
    frame.setObjectName("Segmented")
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(3, 3, 3, 3)
    layout.setSpacing(0)
    for value, label in options:
        btn = QPushButton(label)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setChecked(value == current)
        btn.setObjectName("SegmentedButton")
        btn.setProperty("active", value == current)
        btn.setFixedHeight(30)
        btn.clicked.connect(lambda _checked=False, v=value: callback(v))
        layout.addWidget(btn)
    return frame


def toggle(on: bool, callback: Callable[[bool], None], label: str | None = None, parent: QWidget | None = None) -> QWidget:
    """Toggle switch matching reference Toggle primitive."""
    root = QWidget(parent)
    state = {"on": on}
    layout = QHBoxLayout(root)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    track = QFrame()
    track.setFixedSize(36, 20)
    track.setObjectName("ToggleTrack")
    track.setProperty("on", state["on"])
    thumb = QFrame(track)
    thumb.setObjectName("ToggleThumb")
    thumb.setProperty("on", state["on"])
    thumb.setFixedSize(14, 14)
    thumb.move(19 if state["on"] else 3, 3)
    btn = QPushButton()
    btn.setFixedSize(36, 20)
    btn.setStyleSheet("background: transparent; border: none;")

    def toggle_state() -> None:
        state["on"] = not state["on"]
        track.setProperty("on", state["on"])
        thumb.setProperty("on", state["on"])
        thumb.move(19 if state["on"] else 3, 3)
        refresh_style(track)
        refresh_style(thumb)
        callback(state["on"])

    btn.clicked.connect(toggle_state)
    track_layout = QHBoxLayout(track)
    track_layout.setContentsMargins(0, 0, 0, 0)
    track_layout.addWidget(btn)
    layout.addWidget(track)
    if label:
        lbl = QLabel(label)
        lbl.setObjectName("ToggleLabel")
        layout.addWidget(lbl)
    layout.addStretch(1)
    return root


def kbd(text: str, parent: QWidget | None = None) -> QLabel:
    label = QLabel(text, parent)
    label.setObjectName("KBD")
    label.setAlignment(Qt.AlignCenter)
    return label


def gold_icon_box(icon_name: str, icon_size: int = 13) -> QFrame:
    """Gold icon box used in quick actions."""
    box = QFrame()
    box.setObjectName("GoldIconBox")
    box.setFixedSize(32, 32)
    layout = QVBoxLayout(box)
    layout.setContentsMargins(0, 0, 0, 0)
    icon = QLabel()
    icon.setPixmap(lucide_icon(icon_name, icon_size, TOKENS["goldSoft"]).pixmap(icon_size, icon_size))
    icon.setAlignment(Qt.AlignCenter)
    layout.addWidget(icon)
    return box
