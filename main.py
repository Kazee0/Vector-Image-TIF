import sys
from PyQt6.QtWidgets import QApplication
from tif_viewer import TifViewer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = TifViewer()
    viewer.show()
    sys.exit(app.exec())