import os
import sys
import rasterio
from rasterio.plot import show
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl
from PyQt6.QtGui import QGuiApplication, QImage, QPixmap
from PyQt6.QtQml import QQmlApplicationEngine

class TifViewerBackend(QObject):
    imageLoaded = pyqtSignal(str, str)
    errorOccurred = pyqtSignal(str)
    infoUpdated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.temp_image_path = os.path.join(os.path.dirname(__file__), "temp.png")