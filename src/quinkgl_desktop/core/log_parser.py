from __future__ import annotations

import re


DASHBOARD_CODE_RE = re.compile(r"Dashboard code:\s*(QGL-[A-Z0-9]{4}-[A-Z0-9]{4})")
TOKEN_RE = re.compile(r"qgl_(?:live|view)_[A-Za-z0-9._-]+")


def extract_dashboard_code(line: str) -> str | None:
    match = DASHBOARD_CODE_RE.search(line)
    return match.group(1) if match else None


def redact_sensitive_text(text: str) -> str:
    return TOKEN_RE.sub("<redacted-token>", text)
