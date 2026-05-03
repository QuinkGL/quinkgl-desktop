from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QProcess, Signal

from quinkgl_desktop.core.log_parser import extract_dashboard_code, redact_sensitive_text


class PeerProcessManager(QObject):
    log_line = Signal(str)
    dashboard_code = Signal(str)
    status_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._process: QProcess | None = None

    def is_running(self) -> bool:
        return self._process is not None and self._process.state() != QProcess.NotRunning

    def start(self, command: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
        if self.is_running():
            raise RuntimeError("A peer process is already running.")
        process = QProcess(self)
        process.setWorkingDirectory(str(cwd))
        process.setProgram(command[0])
        process.setArguments(command[1:])
        from PySide6.QtCore import QProcessEnvironment

        process_env = QProcessEnvironment.systemEnvironment()
        if env is not None:
            for key, value in env.items():
                process_env.insert(key, value)
        process_env.insert("PYTHONUNBUFFERED", "1")
        process.setProcessEnvironment(process_env)
        process.readyReadStandardOutput.connect(self._read_stdout)
        process.readyReadStandardError.connect(self._read_stderr)
        process.finished.connect(self._finished)
        self._process = process
        process.start()
        self.status_changed.emit("running")

    def stop(self) -> None:
        if not self._process:
            return
        self._process.terminate()
        if not self._process.waitForFinished(3000):
            self._process.kill()

    def _read_stdout(self) -> None:
        self._read_stream(standard_error=False)

    def _read_stderr(self) -> None:
        self._read_stream(standard_error=True)

    def _read_stream(self, standard_error: bool) -> None:
        if not self._process:
            return
        raw = self._process.readAllStandardError() if standard_error else self._process.readAllStandardOutput()
        for line in bytes(raw).decode(errors="replace").splitlines():
            safe_line = redact_sensitive_text(line)
            self.log_line.emit(safe_line)
            code = extract_dashboard_code(safe_line)
            if code:
                self.dashboard_code.emit(code)

    def _finished(self, exit_code: int) -> None:
        self.status_changed.emit("stopped" if exit_code == 0 else "failed")
        self._process = None
