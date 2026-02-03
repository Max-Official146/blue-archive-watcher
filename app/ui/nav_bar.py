from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout


class NavBar(QWidget):
    def __init__(self):
        super().__init__()

        self.profile_btn = QPushButton("👤 Profile")
        self.frames_btn = QPushButton("🖼 Frames")
        self.refs_btn = QPushButton("✂ References")
        self.debug_btn = QPushButton("🐞 Debug")

        layout = QVBoxLayout()
        layout.addWidget(self.profile_btn)
        layout.addWidget(self.frames_btn)
        layout.addWidget(self.refs_btn)
        layout.addWidget(self.debug_btn)
        layout.addStretch()

        self.setLayout(layout)
        self.setFixedWidth(140)
