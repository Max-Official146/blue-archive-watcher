import cv2

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage


class CameraProbeWorker(QThread):
    cameraIndicesReady = pyqtSignal(list)

    def __init__(self, max_devices=10):
        super().__init__()
        self.max_devices = max_devices

    def run(self):
        indices = []
        for index in range(self.max_devices):
            cap = cv2.VideoCapture(index)
            try:
                if cap.isOpened():
                    indices.append(index)
            finally:
                cap.release()
        self.cameraIndicesReady.emit(indices)


class CameraSnapshotWorker(QThread):
    snapshotReady = pyqtSignal(QImage)
    snapshotFailed = pyqtSignal(str)

    def __init__(self, camera_index):
        super().__init__()
        self.camera_index = camera_index

    def run(self):
        cap = cv2.VideoCapture(self.camera_index)
        try:
            if not cap.isOpened():
                self.snapshotFailed.emit(f"No signal from camera {self.camera_index}")
                return

            ok, frame = cap.read()
            if not ok:
                self.snapshotFailed.emit(f"No signal from camera {self.camera_index}")
                return

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            image = QImage(
                frame.data,
                w,
                h,
                ch * w,
                QImage.Format.Format_RGB888,
            ).copy()

            self.snapshotReady.emit(image)
        finally:
            cap.release()
