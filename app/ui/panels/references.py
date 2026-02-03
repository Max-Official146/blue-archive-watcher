from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel
)
import os

from app.ui.panel_header import PanelHeader
from app.app_state import app_state
from core.profiles import get_profile_dirs


class ReferencesPanel(QWidget):
    def __init__(self, nav):
        super().__init__()
        self.nav = nav

        header = PanelHeader("References", nav)

        self.body_layout = QVBoxLayout()

        self.refresh_references()

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addLayout(self.body_layout)

        self.setLayout(layout)

    def refresh_references(self):
        # clear old entries
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        profile = app_state.active_profile
        if not profile:
            self.body_layout.addWidget(QLabel("No profile selected"))
            return

        dirs = get_profile_dirs(profile)
        ref_dir = dirs["references"]

        refs = [
            f for f in os.listdir(ref_dir)
            if f.lower().endswith(".png")
        ]

        if not refs:
            self.body_layout.addWidget(QLabel("No references found"))
            return

        for ref_name in refs:
            btn = QPushButton(ref_name)
            btn.clicked.connect(
                lambda _, r=ref_name: self.open_reference(r)
            )
            self.body_layout.addWidget(btn)

    def open_reference(self, ref_name):
        # just select the reference, do NOT crop it
        app_state.selected_reference = ref_name

        # store selected reference in global state
        app_state.selected_reference = ref_name
