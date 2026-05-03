from quinkgl_desktop.core.log_parser import extract_dashboard_code, redact_sensitive_text


def test_extract_dashboard_code_from_run_output():
    line = "Dashboard code: QGL-NIST-3YP6"

    assert extract_dashboard_code(line) == "QGL-NIST-3YP6"


def test_redacts_quinkgl_tokens():
    text = "ingest_token=qgl_live_secretvalue"

    assert "qgl_live_secretvalue" not in redact_sensitive_text(text)
    assert "<redacted-token>" in redact_sensitive_text(text)
