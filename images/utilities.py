import base64
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QApplication

def icon_from_base64(b64data):
    pixmap = QPixmap()
    pixmap.loadFromData(base64.b64decode(b64data))
    return QIcon(pixmap)

def convert_file_to_base64(file_path):
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return encoded

def is_dark_theme():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    palette = app.palette()
    bg_color = palette.window().color()
    return bg_color.lightness() < 128


def select_theme_icon(light_b64, dark_b64):
    return dark_b64 if is_dark_theme() else light_b64
