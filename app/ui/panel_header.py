from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout


class PanelHeader(QWidget):
    def __init__(self, title, nav):
        super().__init__()
        self.nav = nav

        back_btn = QPushButton("⬅")
        back_btn.setFixedWidth(40)
        back_btn.clicked.connect(self.nav.pop)

        title_lbl = QLabel(title)

        layout = QHBoxLayout()
        layout.addWidget(back_btn)
        layout.addWidget(title_lbl)
        layout.addStretch()

        self.setLayout(layout)
