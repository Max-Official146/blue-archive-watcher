from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea
)
import os

from app.ui.panel_header import PanelHeader
from app.app_state import app_state
from core.profiles import get_profile_dirs


class DebugPanel(QWidget):
    def __init__(self, nav):
        super().__init__()
        self.nav = nav

        header = PanelHeader("Debug Frames", nav)

        self.body_layout = QVBoxLayout()
        self.refresh_debug()

        delete_btn = QPushButton("🗑 Delete All Debug Frames")
        delete_btn.clicked.connect(self.delete_all)

        container = QWidget()
        container.setLayout(self.body_layout)

        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(scroll)
        layout.addWidget(delete_btn)

        self.setLayout(layout)

    def refresh_debug(self):
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        profile = app_state.active_profile
        if not profile:
            self.body_layout.addWidget(QLabel("No profile selected"))
            return

        dirs = get_profile_dirs(profile)
        debug_dir = dirs["debug"]

        files = sorted(
            f for f in os.listdir(debug_dir)
            if f.lower().endswith(".png")
        )

        if not files:
            self.body_layout.addWidget(QLabel("No debug frames found"))
            return

        for f in files:
            self.body_layout.addWidget(QLabel(f))

    def delete_all(self):
        profile = app_state.active_profile
        if not profile:
            return

        dirs = get_profile_dirs(profile)
        debug_dir = dirs["debug"]

        # SAFETY CHECKS
        if not os.path.exists(debug_dir):
            return

        if not os.path.isdir(debug_dir):
            return

        # only delete png files in THIS directory
        for name in os.listdir(debug_dir):
            path = os.path.join(debug_dir, name)

            if (
                os.path.isfile(path)
                and name.lower().endswith(".png")
                and path.startswith(os.path.abspath(debug_dir))
            ):
                os.remove(path)

        self.refresh_debug()
