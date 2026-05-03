from __future__ import annotations

from enum import Enum


class PeerState(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    FAILED = "failed"


# Premium dark + gold design system tokens shared by QSS and PySide widgets.
TOKENS = {
    "bg": "#080808",
    "bgDeep": "#070707",
    "topbar": "#080808",
    "panel": "#141414",
    "panelHi": "#101010",
    "panelHover": "#181818",
    "input": "#050505",
    "code": "#050505",
    "border": "rgba(255,255,255,0.07)",
    "borderMid": "rgba(255,255,255,0.10)",
    "borderHover": "rgba(255,255,255,0.14)",
    "borderGold": "rgba(224,184,77,0.35)",
    "gold": "#E0B84D",
    "goldSoft": "#E8C75A",
    "goldDim": "#B9973A",
    "goldSurface": "rgba(224,184,77,0.10)",
    "text": "#F3F3F3",
    "textDim": "#A8A8A8",
    "textMute": "#707070",
    "textDisabled": "#444444",
    "good": "#43D17A",
    "warn": "#E0B84D",
    "bad": "#EF6A6A",
    "info": "#63D9F5",
    "neutral": "#888888",
    "launchIconBgStopped": "rgba(224,184,77,0.10)",
    "launchIconBorderStopped": "rgba(224,184,77,0.30)",
    "launchIconBgRunning": "rgba(67,209,122,0.10)",
    "launchIconBorderRunning": "rgba(67,209,122,0.26)",
    "launchPanelStartRunning": "#0E1811",
    "launchPanelStartStopped": "#151208",
    "navHoverBg": "rgba(255,255,255,0.035)",
    "navCheckedBg": "rgba(224,184,77,0.10)",
    "wizardProgressText": "#F3F3F3",
    "wizardStepLabel": "#C6C6C6",
    "wizardStepDesc": "#858585",
}

# Backwards-compatible alias mapping
COLORS = {
    "bg_app": TOKENS["bg"],
    "bg_sidebar": TOKENS["bgDeep"],
    "bg_surface_start": TOKENS["panel"],
    "bg_surface_end": TOKENS["panelHi"],
    "bg_input": TOKENS["input"],
    "bg_card_hover": TOKENS["panelHi"],
    "border_default": TOKENS["border"],
    "border_hover": TOKENS["borderHover"],
    "border_strong": TOKENS["borderMid"],
    "text_primary": TOKENS["text"],
    "text_body": TOKENS["text"],
    "text_muted": TOKENS["textMute"],
    "text_dim": TOKENS["textDim"],
    "text_faint": TOKENS["textMute"],
    "text_disabled": TOKENS["textDisabled"],
    "gold": TOKENS["gold"],
    "gold_bright": TOKENS["goldSoft"],
    "gold_pale": TOKENS["goldSoft"],
    "gold_deep": TOKENS["goldDim"],
    "status_ok": TOKENS["good"],
    "status_warn": TOKENS["warn"],
    "status_error": TOKENS["bad"],
    "launch_icon_bg_stopped": TOKENS["launchIconBgStopped"],
    "launch_icon_border_stopped": TOKENS["launchIconBorderStopped"],
    "launch_icon_bg_running": TOKENS["launchIconBgRunning"],
    "launch_icon_border_running": TOKENS["launchIconBorderRunning"],
    "launch_panel_start_running": TOKENS["launchPanelStartRunning"],
    "launch_panel_start_stopped": TOKENS["launchPanelStartStopped"],
    "nav_hover_bg": TOKENS["navHoverBg"],
    "nav_checked_bg": TOKENS["navCheckedBg"],
    "wizard_progress_text": TOKENS["wizardProgressText"],
    "wizard_step_label": TOKENS["wizardStepLabel"],
    "wizard_step_desc": TOKENS["wizardStepDesc"],
}

LEVEL_COLORS = {
    "info": TOKENS["info"],
    "warn": TOKENS["warn"],
    "error": TOKENS["bad"],
    "ok": TOKENS["good"],
    "debug": TOKENS["textMute"],
}

RADII = {
    "control": 8,
    "inner": 10,
    "card": 14,
    "hero": 14,
}

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 20,
    "card_x": 22,
    "card_y": 20,
    "page": 44,
    "page_x": 44,
    "page_y": 40,
}

TYPE_SCALE = {
    "eyebrow": 11,
    "meta": 12,
    "body": 14,
    "card_title": 16,
    "page_title": 30,
}

PEER_STATE_COLORS = {
    PeerState.RUNNING: COLORS["status_ok"],
    PeerState.STARTING: COLORS["status_warn"],
    PeerState.STOPPED: COLORS["text_faint"],
    PeerState.FAILED: COLORS["status_error"],
}

PEER_STATE_BADGES = {
    PeerState.RUNNING: "green",
    PeerState.STARTING: "amber",
    PeerState.STOPPED: "neutral",
    PeerState.FAILED: "red",
}

DEFAULTS = {
    "node_id": "peer-1",
    "port": 7001,
    "script_path": "peer_script.py",
    "rounds": 20,
    "trust_policy": "tofu",
    "script_args": {"peer_index": "1", "data_root": "./data"},
    "manifest_name": "custom-swarm",
    "task_type": "class",
    "input_shape": "3,32,32",
    "output_shape": "10",
    "label_type": "integer",
    "model_framework": "pytorch",
    "aggregation": "FedAvg",
    "topology": "AffinityTopology",
    "output_path": "custom.qgl",
    "dashboard_url": "https://141-147-36-24.sslip.io",
    "creator_key_path": "creator.key",
    "device": "cuda:0",
    "workers": "4",
    "log_level": "info",
}
