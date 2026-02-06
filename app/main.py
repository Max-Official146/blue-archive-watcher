import sys
from pathlib import Path

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from app.ui.app_shell import AppShell


LIGHT_THEME_STYLESHEET = """
QWidget {
    background-color: #ffffff;
    color: #111111;
}

QLabel {
    background-color: #ffffff;
    color: #111111;
}

QPushButton {
    background-color: #ffffff;
    color: #111111;
    border: 1px solid #d6d6d6;
    border-radius: 8px;
    padding: 6px 10px;
}

QPushButton:hover {
    background-color: #f7f7f7;
    border-color: #cdcdcd;
}

QPushButton:pressed {
    background-color: #eeeeee;
    border-color: #c6c6c6;
}

QLineEdit,
QTextEdit,
QPlainTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox,
QDateEdit,
QDateTimeEdit,
QTimeEdit {
    background-color: #ffffff;
    color: #111111;
    border: 1px solid #d6d6d6;
    border-radius: 6px;
    padding: 4px 8px;
    selection-background-color: #e6e6e6;
    selection-color: #111111;
}

QComboBox::drop-down,
QDateEdit::drop-down,
QDateTimeEdit::drop-down,
QTimeEdit::drop-down {
    background-color: #ffffff;
    border: 0;
}

QScrollArea,
QFrame,
QListWidget,
QTreeWidget,
QTableWidget,
QListView,
QTreeView,
QTableView,
QGraphicsView,
QStackedWidget,
QToolBox,
QSplitter,
QScrollBar,
QGroupBox,
QTabWidget::pane,
QTabBar::tab,
QStatusBar,
QMenuBar,
QMenu,
QDialog,
QMainWindow,
QDockWidget,
QToolBar {
    background-color: #ffffff;
    color: #111111;
    border: 1px solid #d6d6d6;
    border-radius: 8px;
}

QTabBar::tab:selected,
QTabBar::tab:hover,
QMenu::item:selected {
    background-color: #f3f3f3;
    color: #111111;
}

QHeaderView::section {
    background-color: #ffffff;
    color: #111111;
    border: 1px solid #d6d6d6;
    padding: 4px;
}

QScrollBar:vertical,
QScrollBar:horizontal {
    background-color: #ffffff;
    border: 1px solid #d6d6d6;
    margin: 0;
}

QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background-color: #efefef;
    border: 1px solid #d6d6d6;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover {
    background-color: #e7e7e7;
}

QScrollBar::add-line,
QScrollBar::sub-line,
QScrollBar::add-page,
QScrollBar::sub-page {
    background-color: #ffffff;
    border: none;
}

QCheckBox,
QRadioButton {
    background-color: #ffffff;
    color: #111111;
}

QCheckBox::indicator,
QRadioButton::indicator {
    background-color: #ffffff;
    border: 1px solid #d6d6d6;
}

QCheckBox::indicator:checked,
QRadioButton::indicator:checked {
    background-color: #f0f0f0;
}

QToolTip {
    background-color: #ffffff;
    color: #111111;
    border: 1px solid #d6d6d6;
}
"""


def main():
    QCoreApplication.setOrganizationName("Frame Trace")
    QCoreApplication.setApplicationName("Frame Trace")
    app = QApplication(sys.argv)
    app.setApplicationName("Frame Trace")

    icon_path = Path(__file__).resolve().parent.parent / "assets" / "app_icon.png"
    app_icon = QIcon(str(icon_path))
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    app.setStyleSheet(LIGHT_THEME_STYLESHEET)

    shell = AppShell()
    if not app_icon.isNull():
        shell.setWindowIcon(app_icon)
    shell.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
