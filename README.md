# QuinkGL Desktop

A Python desktop application that wraps the QuinkGL CLI in a focused, dark-themed PySide6 GUI. It helps new users set up, enroll, and run QuinkGL peers without memorizing command-line arguments.

> **Status:** MVP — single-peer launcher and project dashboard.

## Features

- **Project Picker** — Create or open a local QuinkGL workspace.
- **Setup Wizard** — Step-by-step onboarding (workspace, creator key, manifest, telemetry, peer config).
- **Creator Key Management** — Generate keys securely without exposing contents in the UI.
- **Manifest Builder** — Create signed `.qgl` manifests from GUI fields.
- **Telemetry Enrollment** — Enroll swarms and track `.telemetry.qglkey` status.
- **Peer Runner** — Configure and launch a single peer with live stdout/stderr streaming.
- **Log Console** — Terminal-style log panel with automatic dashboard-code detection (`Dashboard code: QGL-....-....`).
- **Security-First** — Sensitive tokens and keys are redacted from logs; private key material is never stored in project state.

## Requirements

- Python >= 3.11
- `quinkgl` CLI installed and available in your `PATH`

## Installation

```bash
git clone <repository-url>
cd quinkgl-desktop
pip install -e ".[dev]"
```

## Running the App

### Installed entry point

```bash
quinkgl-desktop
```

### Direct module run

```bash
python -m quinkgl_desktop
```

## Development

### Run tests

```bash
pytest -q
```

## Building Standalone Executables

This project uses [PyInstaller](https://pyinstaller.org/) to create standalone executables for macOS, Windows, and Linux.

### Local build (current platform)

```bash
pip install -e ".[build]"

# macOS / Linux
pyinstaller \
  --name "QuinkGL Desktop" \
  --windowed \
  --add-data "src/quinkgl_desktop/resources:quinkgl_desktop/resources" \
  src/quinkgl_desktop/main.py

# Windows
pyinstaller ^
  --name "quinkgl-desktop" ^
  --windowed ^
  --add-data "src/quinkgl_desktop/resources;quinkgl_desktop/resources" ^
  src/quinkgl_desktop/main.py
```

Output:
- **macOS**: `dist/QuinkGL Desktop.app`
- **Windows/Linux**: `dist/quinkgl-desktop`

### GitHub Actions (all platforms)

A CI workflow is included in `.github/workflows/build.yml`. It automatically builds for all three platforms and attaches artifacts to releases.

**Trigger manually:**
1. Go to **Actions → Build**
2. Click **Run workflow**

**Trigger on tag:**
```bash
git tag v0.1.0
git push origin v0.1.0
```

This creates a GitHub release with downloadable files:
- `QuinkGL-Desktop-macos.zip`
- `QuinkGL-Desktop-windows.zip`
- `QuinkGL-Desktop-linux.tar.gz`

### Project structure

```text
quinkgl-desktop/
├── pyproject.toml
├── src/quinkgl_desktop/
│   ├── core/          # Models, CLI adapter, process manager, log parser, store
│   ├── services/      # Business logic (keys, manifests, telemetry, peers)
│   ├── ui/            # PySide6 pages, components, theme, and state
│   └── resources/     # Fonts, model presets, theme.qss, logo
├── tests/             # Pytest suite (no PySide6 headless smoke tests included)
└── docs/              # Architecture spec and implementation plans
```

## Architecture

The app is a GUI orchestration layer over the existing `quinkgl` CLI:

```text
PySide6 UI  →  Application Services  →  CLI Adapter / Process Manager
                     ↓
              Project Store (JSON under .quinkgl-desktop/project.json)
```

- **Short CLI commands** use `subprocess.run` (keygen, manifest create, telemetry enroll).
- **Long-running peers** use `QProcess` with live log streaming and dashboard-code extraction.
- **Project state** is saved inside the selected workspace under `.quinkgl-desktop/project.json`.

## Security Notes

- `creator.key` contents are never displayed.
- `.telemetry.qglkey` ingest tokens are never displayed.
- Token-like strings (`qgl_live_*`, `qgl_view_*`) are automatically redacted from the log console.
- The workspace is treated as user-controlled local data.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
