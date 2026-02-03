from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout

from core import detector as dect
from core.profiles import list_profiles

from app.app_state import app_state
from app.services.monitor_service import MonitorService
from app.controllers.monitor_controller import MonitorController


class DashboardPanel(QWidget):
    """
    Main dashboard panel.
    Responsibilities:
    - Show current profile
    - Show monitoring state
    - Start / stop monitoring
    - Entry point to other panels
    """

    def __init__(self, nav):
        super().__init__()
        self.nav = nav

        # ---- status labels ----
        self.profile_label = QLabel("Profile: None")
        self.monitor_label = QLabel("Monitoring: Stopped")
        self.label = QLabel("Status: Idle")

        # ---- action buttons ----
        #self.profile_btn = QPushButton("👤 Select Profile")
        #self.ref_btn = QPushButton("📌 Select Reference")
        self.start_btn = QPushButton("▶ Start Monitoring")
        self.stop_btn = QPushButton("⏹ Stop")

        # ---- layout ----
        layout = QVBoxLayout()
        layout.addWidget(self.profile_label)
        layout.addWidget(self.monitor_label)
        layout.addWidget(self.label)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        self.setLayout(layout)

        # ---- services ----
        self.monitor = MonitorService()
        self.monitor.status.connect(self.label.setText)

        # ---- controllers ----
        self.monitor_controller = MonitorController(self.monitor)

        # ---- signals ----
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)

    def select_profile(self):
        profiles = list_profiles()
        if not profiles:
            self.label.setText("No profiles found")
            return

        app_state.active_profile = profiles[0]
        self.profile_label.setText(f"Profile: {profiles[0]}")
        self.label.setText("Profile selected")

    def select_reference(self):
        if not app_state.active_profile:
            self.label.setText("Select a profile first")
            return

        self.label.setText("Select reference region…")
        dect.refrence_selector(app_state.active_profile)

        # 🔍 show result clearly
        from core.profiles import get_profile_dirs
        import os

        refs = os.listdir(get_profile_dirs(app_state.active_profile)["references"])
        if refs:
            self.label.setText(f"Reference added: {refs[-1]}")
        else:
            self.label.setText("No reference saved")

    def start(self):
        if not self.monitor.isRunning():
            msg = self.monitor_controller.start()
            if msg:
                self.label.setText(msg)
        else:
            self.label.setText("Monitoring already running")

        self.refresh()

    def stop(self):
        # Stop ONLY if the monitor thread is actually running
        if self.monitor.isRunning():
            msg = self.monitor_controller.stop()
            if msg:
                self.label.setText(msg)
        else:
            self.label.setText("Monitoring already stopped")

        # Update UI after stopping
        self.refresh()

    def close(self):
        self.monitor_controller.stop()

    def refresh(self):
        profile = app_state.active_profile

        if profile:
            self.profile_label.setText(f"Profile: {profile}")
        else:
            self.profile_label.setText("Profile: None")

        if self.monitor.isRunning():
            self.monitor_label.setText("Monitoring: Running")
        else:
            self.monitor_label.setText("Monitoring: Stopped")