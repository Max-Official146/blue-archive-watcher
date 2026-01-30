import sys
import time
import cv2

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
)
from PyQt5.QtCore import QThread, pyqtSignal

import frame_comparison as frmcp
import notification_n_sound as nns


# ---------------- WORKER THREAD ----------------
class MonitorThread(QThread):
    status = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False

    def run(self):
        self.running = True
        self.status.emit("Monitoring...")

        cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            cv2.imwrite("temp_frame_capture.png", frame)

            if frmcp.frame_comp():
                self.status.emit("Dialogue detected!")
                nns.alert()

            time.sleep(0.5)

        cap.release()
        self.status.emit("Stopped")

    def stop(self):
        self.running = False


# ---------------- MAIN WINDOW ----------------
class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("B.A Game Analysis")
        self.setGeometry(300, 300, 320, 220)

        self.label = QLabel("Idle")

        self.ref_btn = QPushButton("📌 Select Reference")
        self.start_btn = QPushButton("▶ Start Monitoring")
        self.stop_btn = QPushButton("⏹ Stop")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.ref_btn)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        self.setLayout(layout)

        self.thread = MonitorThread()

        # signals
        self.ref_btn.clicked.connect(self.select_reference)
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.thread.status.connect(self.label.setText)

    def select_reference(self):
        self.label.setText("Select reference...")
        frmcp.refrence_selector()
        self.label.setText("Reference saved")

    def start(self):
        if not self.thread.isRunning():
            self.thread.start()

    def stop(self):
        if self.thread.isRunning():
            self.thread.stop()


# ---------------- ENTRY ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
