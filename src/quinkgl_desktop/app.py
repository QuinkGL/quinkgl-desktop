def run_app() -> int:
    from PySide6.QtWidgets import QApplication

    from quinkgl_desktop.ui.main_window import MainWindow

    app = QApplication([])
    window = MainWindow()
    screen = app.primaryScreen()
    if screen is not None:
        available = screen.availableGeometry()
        window.setMinimumSize(min(1100, available.width()), min(720, available.height()))
        width = min(1600, available.width())
        height = min(1000, available.height())
        window.resize(width, height)
        window.move(
            available.x() + max(0, (available.width() - width) // 2),
            available.y() + max(0, (available.height() - height) // 2),
        )
    window.show()
    return app.exec()
