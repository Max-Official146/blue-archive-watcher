from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)

import os
import cv2

from app.ui.panel_header import PanelHeader
from app.app_state import app_state
from core.profiles import get_profile_dirs


class CropPanel(QWidget):
    def __init__(self, nav):
        super().__init__()
        self.nav = nav

        header = PanelHeader("Crop Reference", nav)

        self.info_label = QLabel(
            "Crop a base frame to create a reference"
        )

        add_crop_btn = QPushButton("➕ Add Crop")
        add_crop_btn.clicked.connect(self.add_crop)

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(self.info_label)
        layout.addWidget(add_crop_btn)

        self.setLayout(layout)

    def add_crop(self):
        profile = app_state.active_profile
        if not profile:
            self.info_label.setText("No profile selected")
            return

        dirs = get_profile_dirs(profile)
        frames_dir = dirs["frames"]
        refs_dir = dirs["references"]

        # list available base frames
        frames = [
            f for f in os.listdir(frames_dir)
            if f.lower().endswith(".png")
        ]

        if not frames:
            self.info_label.setText("No base frames found in frames/")
            return

        # TEMP: pick first frame (we add selector UI later)
        frame_name = frames[0]
        frame_path = os.path.join(frames_dir, frame_name)

        img = cv2.imread(frame_path)
        if img is None:
            self.info_label.setText("Failed to load frame")
            return

        roi = cv2.selectROI(
            "Select reference region (ENTER to confirm, ESC to cancel)",
            img,
            fromCenter=False,
            showCrosshair=True
        )

        x, y, w, h = roi
        if w <= 0 or h <= 0:
            cv2.destroyAllWindows()
            return

        crop = img[y:y+h, x:x+w]

        # generate unique reference name
        base = os.path.splitext(frame_name)[0]
        existing = [
            f for f in os.listdir(refs_dir)
            if f.startswith(base)
        ]

        ref_name = f"{base}_ref{len(existing)+1}.png"
        ref_path = os.path.join(refs_dir, ref_name)

        cv2.imwrite(ref_path, crop)
        cv2.destroyAllWindows()

        self.info_label.setText(
            f"Reference created:\n{ref_name}"
        )
