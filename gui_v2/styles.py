STYLES = """
QMainWindow, QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}
QLineEdit, QTextEdit, QSpinBox, QListWidget {
    background-color: #3b3b3b;
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 5px;
    color: #ffffff;
    selection-background-color: #3d8ec9;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #3d8ec9;
}
QPushButton {
    background-color: #3d8ec9;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 15px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #4da3df;
}
QPushButton:pressed {
    background-color: #2b6a94;
}
QTabWidget::pane {
    border: 1px solid #444;
    border-radius: 5px;
}
QTabBar::tab {
    background: #3b3b3b;
    border: 1px solid #444;
    padding: 8px 12px;
    margin-right: 2px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}
QTabBar::tab:selected {
    background: #3d8ec9;
    color: white;
}
QGroupBox {
    border: 1px solid #555;
    border-radius: 5px;
    margin-top: 20px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
}
"""
