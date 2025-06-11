import base64
from PyQt6.QtGui import QPixmap, QIcon

def icon_from_base64(b64data):
    pixmap = QPixmap()
    pixmap.loadFromData(base64.b64decode(b64data))
    return QIcon(pixmap)

def convert_file_to_base64(file_path):
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return encoded