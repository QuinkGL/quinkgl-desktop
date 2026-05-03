from __future__ import annotations


APP_COPY = {
    "brand_name": "QuinkGL",
    "brand_product": "Desktop",
    "projects": "Projects",
    "select_project": "Select a project",
    "no_project": "No project selected",
    "change_project": "Change Project",
    "project_short": "Project",
    "search_placeholder": "Search anything…",
    "workspace": "Workspace",
    "setup": "Setup",
    "peer": "Peer",
    "no_project_pill": "No project · choose one",
    "slash": "/",
    "kbd_cmd_k": "⌘K",
    "expand": "Expand",
    "collapse": "Collapse",
}

STATUS_LABELS = {
    "stopped": "Stopped",
    "starting": "Starting",
    "running": "Running",
    "failed": "Failed",
}

PAGES_COPY = {
    "overview": {
        "label": "Overview",
        "hint": "Readiness",
        "eyebrow": "Workspace",
        "title": "Welcome back to {project}",
        "subtitle": "Configure your peer, sign a manifest, and launch a QuinkGL training run without touching the terminal.",
    },
    "wizard": {
        "label": "Wizard",
        "hint": "Guided setup",
        "eyebrow": "Guided setup",
        "title": "Setup Wizard",
        "subtitle": "Six small steps from an empty workspace to a running QuinkGL peer.",
    },
    "manifest": {
        "label": "Manifest",
        "hint": ".qgl",
        "eyebrow": "Configuration",
        "title": "Manifest",
        "subtitle": "Describe the swarm: dataset shape, model framework, aggregation strategy, and topology. We'll sign and emit a .qgl artifact.",
    },
    "telemetry": {
        "label": "Telemetry",
        "hint": "Dashboard",
        "eyebrow": "Connectivity",
        "title": "Telemetry",
        "subtitle": "Enroll the manifest with the dashboard backend so peer metrics, rounds, and run state can be observed remotely.",
    },
    "run": {
        "label": "Run Peer",
        "hint": "Launch",
        "eyebrow": "Launch",
        "title": "Run Peer",
        "subtitle": "Configure and start one local QuinkGL peer process. We'll stream logs to the Logs view.",
    },
    "logs": {
        "label": "Logs",
        "hint": "Console",
        "eyebrow": "Console",
        "title": "Logs",
        "subtitle": "Peer process output, structured by level and tag.",
    },
    "settings": {
        "label": "Settings",
        "hint": "Preferences",
        "eyebrow": "Preferences",
        "title": "Settings",
        "subtitle": "Configure how QuinkGL Desktop behaves on this machine. Project-level settings live in the Manifest.",
    },
}

# ---------------------------------------------------------------------------
# Overview page
# ---------------------------------------------------------------------------
OVERVIEW_COPY = {
    "continue_setup": "Continue setup",
    "launch_peer": "Launch Peer",
    "readiness_eyebrow": "Project readiness",
    "ready_suffix": "prerequisites complete",
    "complete_guidance": "Everything looks good. You can launch your peer when ready.",
    "incomplete_guidance": "Complete the remaining steps to enable the peer launch.",
    "launch_unavailable": "Available once setup is complete",
    "configure": "Configure",
    "review": "Review",
    "quick_actions": "Quick actions",
    "quick_actions_subtitle": "Jump directly to common tasks.",
    "recent_activity": "Recent activity",
    "last_24h": "last 24h",
    "step": "Step",
    "readiness": [
        ("Creator key", "Generate or load creator.key for signing", "manifest"),
        ("Manifest", "Describe the swarm and produce a signed .qgl", "manifest"),
        ("Telemetry", "Enroll the manifest with the dashboard backend", "telemetry"),
    ],
    "quick_items": [
        ("wizard", "Setup Wizard", "Step through the full guided flow"),
        ("manifest", "Edit Manifest", "Tune topology, aggregation, dataset"),
        ("telemetry", "Enroll Telemetry", "Connect to dashboard backend"),
        ("logs", "Open Logs", "Inspect peer process output"),
    ],
    "activity_empty": [
        ("Manifest signed", "missing"),
        ("Telemetry enrolled", "pending"),
        ("Creator key", "missing"),
        ("Peer runtime", "stopped"),
    ],
}

# ---------------------------------------------------------------------------
# Wizard page
# ---------------------------------------------------------------------------
WIZARD_COPY = {
    "progress": "Progress",
    "open_full_page": "Open full page",
    "promise": "Detailed configuration for this step lives on its own page. The wizard tracks completion and unlocks the next step. You can revisit steps any time.",
    "promise_items": [
        "Inputs validate before completion",
        "Required prerequisites are auto-checked",
        "Configuration is saved per project",
    ],
    "back": "Back",
    "skip": "Skip",
    "mark_complete": "Mark complete",
    "finish_setup": "Finish setup",
    "now": "NOW",
    "step_of": "Step {step} of {total}",
}

# ---------------------------------------------------------------------------
# Manifest page
# ---------------------------------------------------------------------------
MANIFEST_COPY = {
    "preset_title": "Start from a preset",
    "preset_subtitle": "Templates pre-fill compatible shapes and tasks. You can always customize after.",
    "recommended": "Recommended",
    "dataset_title": "Dataset",
    "dataset_subtitle": "Shape and label type for the training data",
    "model_title": "Model",
    "model_subtitle": "Framework and architecture",
    "topology_title": "Aggregation & topology",
    "topology_subtitle": "How peers combine and connect",
    "signing_title": "Signing",
    "signing_subtitle": "The manifest is signed with creator.key for swarm membership",
    "create": "Create Manifest",
    "validate": "Validate",
    "preview": "Preview",
    "copy": "Copy",
    "command_result": "Command result",
    "output_label": "Output: {file}",
    "creator_key_ready": "creator.key ready",
    "ed25519": "ed25519",
    "generate_key": "Generate creator.key",
    "hash_script": "Hash peer_script.py",
    "framework_label": "Framework",
    "arch_hash_label": "Architecture hash",
    "arch_hash_hint": "auto-generated if empty",
    "aggregation_label": "Aggregation",
    "topology_label": "Topology",
    "manifest_name_label": "Manifest name",
    "task_type_label": "Task type",
    "input_shape_label": "Input shape",
    "input_shape_hint": "C,H,W",
    "output_shape_label": "Output shape",
    "label_type_label": "Label type",
    "output_file_label": "Output file",
}

# ---------------------------------------------------------------------------
# Run Peer page
# ---------------------------------------------------------------------------
RUN_COPY = {
    "preflight": [
        ("Manifest", "missing"),
        ("Telemetry", "pending"),
        ("Script", "peer_script.py"),
    ],
    "identity_title": "Identity",
    "identity_subtitle": "How this peer is addressable on the swarm",
    "script_title": "Training script",
    "script_subtitle": "Python entrypoint executed each round",
    "runtime_title": "Runtime",
    "ready_title": "Ready to launch",
    "ready_desc": "Pre-flight checks passed. You can start the peer.",
    "running_title": "Peer is running",
    "running_desc": "Streaming logs and round telemetry",
    "start": "Start Peer",
    "stop": "Stop Peer",
    "generated_command": "Generated command",
    "terminal_hint": "Same command runs in your terminal — no GUI required.",
    "trust_advisory": "Trust policy <b>{policy}</b> pins the first peer key seen. Use strict for production.",
    "node_id_label": "Node ID",
    "port_label": "Port",
    "port_hint": "TCP",
    "script_path_label": "Script path",
    "rounds_label": "Rounds",
    "trust_policy_label": "Trust policy",
    "script_args_label": "Script args",
    "script_args_hint": "appended after --",
    "device_label": "Device",
    "workers_label": "Workers",
    "log_level_label": "Log level",
}

# ---------------------------------------------------------------------------
# Logs page
# ---------------------------------------------------------------------------
LOGS_COPY = {
    "filter_placeholder": "Filter logs… (msg, tag)",
    "pause": "Pause",
    "resume": "Resume",
    "no_wrap": "No wrap",
    "wrap": "Wrap",
    "copy": "Copy",
    "export": "Export",
    "clear": "Clear",
    "lines_fmt": "{count} lines · filter: {filter}",
    "lines_fmt_paused": "{count} lines · filter: {filter} · paused",
    "peer_fmt": "{node_id} :{port}",
    "eof": "eof",
    "live": "live",
    "empty_running": "Waiting for matching log lines…",
    "empty_stopped": "Peer is stopped — start it from Run Peer to see logs here.",
}

# ---------------------------------------------------------------------------
# Telemetry page
# ---------------------------------------------------------------------------
TELEMETRY_COPY = {
    "backend_title": "Dashboard backend",
    "backend_subtitle": "Where this swarm publishes runtime telemetry.",
    "dashboard_url_label": "Dashboard URL",
    "dashboard_url_hint": "Your QuinkGL telemetry dashboard endpoint",
    "dashboard_code_label": "Dashboard code",
    "dashboard_code_hint": "One-time enrollment code",
    "enroll": "Enroll Telemetry",
    "request_code": "Request new code",
    "trust_title": "Trust & verification",
    "trust_subtitle": "Enrollment uses creator.key to prove ownership of the manifest.",
    "status": "Status",
    "pending": "pending",
    "enrolled": "enrolled",
    "manifest_signed": "Manifest signed",
    "creator_key": "Creator key",
    "backend_reachable": "Backend reachable",
    "endpoint": "Endpoint",
    "local_key": "Local key",
    "last_enrolled": "Last enrolled",
    "manifest": "Manifest",
    "telemetry_note": "Telemetry only publishes round-level metadata. Model weights and private gradients never leave the peer.",
    "tls": "TLS 1.3",
    "ed25519": "ed25519",
}

# ---------------------------------------------------------------------------
# Settings page
# ---------------------------------------------------------------------------
SETTINGS_COPY = {
    "cli_title": "QuinkGL CLI",
    "cli_subtitle": "Path or alias for the quinkgl binary used to spawn peers.",
    "binary_label": "Binary",
    "default_port_label": "Default port",
    "detect": "Detect",
    "not_found": "not found",
    "found_version": "v{version} found",
    "behavior": "Behavior",
    "behavior_subtitle": "How the app reacts at launch and during peer runs.",
    "autostart_label": "Auto-start last peer on app open",
    "autostart_desc": "Resume the previous run when QuinkGL Desktop opens",
    "analytics_label": "Send anonymous usage analytics",
    "analytics_desc": "Helps prioritize which features to improve",
    "updates_label": "Check for updates automatically",
    "updates_desc": "Notify me when a new desktop version ships",
    "notifications_title": "Notifications",
    "notifications_subtitle": "Native desktop notifications for peer events.",
    "notify_success_label": "Round complete",
    "notify_success_desc": "Notify on each successful round",
    "notify_errors_label": "Errors and crashes",
    "notify_errors_desc": "Always alert on peer process errors",
    "shortcuts_title": "Keyboard shortcuts",
    "shortcuts_subtitle": "Quickly move around without leaving the keyboard.",
    "appearance_title": "Appearance",
    "appearance_subtitle": "Visual preferences for QuinkGL Desktop.",
    "theme_label": "Theme",
    "theme_desc": "Dark gold is the default",
    "theme_value": "Dark · Gold",
    "density_label": "Density",
    "density_desc": "Comfortable spacing",
    "density_value": "Comfortable",
    "reduce_motion_label": "Reduce motion",
    "reduce_motion_desc": "Disables non-essential animation",
    "workspace_title": "Workspace",
    "workspace_subtitle": "Where projects and run artifacts live on disk.",
    "default_folder_label": "Default projects folder",
    "default_folder_hint": "Used by Create Project",
    "logs_retention_label": "Run logs retention",
    "logs_retention_hint": "days",
    "advanced_title": "Advanced",
    "advanced_subtitle": "For power users. Changes apply on next peer launch.",
    "verbose_logging_label": "Verbose logging",
    "verbose_logging_desc": "Include debug-level lines in console",
    "strict_trust_label": "Strict trust policy by default",
    "strict_trust_desc": "Reject unknown peer keys (overrides tofu)",
    "storage_title": "Storage",
    "storage_subtitle": "Local cache and per-project artifacts.",
    "cache_label": "Cache",
    "run_logs_label": "Run logs",
    "manifests_label": "Manifests",
    "clear_cache": "Clear cache",
    "about_title": "About QuinkGL Desktop",
    "version_label": "Version",
    "cli_version_label": "QuinkGL CLI",
    "channel_label": "Channel",
    "license_label": "License",
}

# ---------------------------------------------------------------------------
# Project picker page
# ---------------------------------------------------------------------------
PROJECT_PICKER_COPY = {
    "title": "QuinkGL Desktop",
    "eyebrow": "QuinkGL Desktop · v{version}",
    "headline_a": "Launch a federated peer",
    "headline_b": "without touching the terminal.",
    "subtitle": "Configure manifests, enroll telemetry, and start QuinkGL peers from a guided desktop workflow built for ML researchers.",
    "body": [
        "Prepare and launch a QuinkGL peer without typing the full CLI sequence.",
        "The desktop app keeps your creator key, manifest, telemetry key, and run logs organized inside your local workspace.",
        "Choose an existing playground folder or create a new project workspace to begin.",
    ],
    "create": "Create Project",
    "open": "Open Project",
    "recent_title": "Recent projects",
    "recent_filter": "Filter projects",
    "templates_title": "Start from a template",
    "first_time_title": "First time?",
    "first_time_subtitle": "Five minutes from empty folder to a running peer.",
    "first_time_guide_title": "Quickstart Guide",
    "first_time_guide_text": (
        "1. Create or open a workspace folder.\n"
        "2. Generate a creator key (kept hidden).\n"
        "3. Build a manifest describing your model and dataset.\n"
        "4. Enroll telemetry to connect to the dashboard.\n"
        "5. Launch a peer and watch live logs.\n\n"
        "The app will guide you through each step."
    ),
    "first_time_about_title": "What is QuinkGL?",
    "first_time_about_text": (
        "QuinkGL is a federated learning framework for training machine learning models "
        "across decentralized peers without sharing raw data.\n\n"
        "Peers exchange model updates (gradients) over a secure gossip protocol, "
        "aggregate them using configurable strategies like FedAvg, and produce a shared global model.\n\n"
        "QuinkGL Desktop is a standalone launcher that wraps the CLI in a visual workflow."
    ),
    "first_time_community_url": "https://github.com/quinkgl/quinkgl",
    "resources": [
        ("Quickstart guide", "book-open", "guide"),
        ("What is QuinkGL?", "graduation-cap", "about"),
        ("Join the community", "message-circle", "community"),
    ],
}
