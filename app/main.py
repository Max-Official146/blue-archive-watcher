import sys
from PyQt6.QtWidgets import QApplication

from app.ui.app_shell import AppShell


def main():
    app = QApplication(sys.argv)
    shell = AppShell()
    shell.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
