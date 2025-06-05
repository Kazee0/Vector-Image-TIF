import os
import sys
import rasterio
from rasterio.plot import show
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np

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

    @pyqtSlot(str)
    def loadTifFile(self, file_path):
        try:
            with rasterio.open(file_path) as src:
                num_bands = src.count
                width = src.width
                height = src.height
                crs = src.crs
                transform = src.transform
                bounds = src.bounds
                
                fig = Figure(figsize=(width/100, height/100), dpi=100)
                canvas = FigureCanvasAgg(fig)
                ax = fig.add_subplot(111)
                
                if num_bands >=3:
                    red = src.read(1)
                    green = src.read(2)
                    blue = src.read(3)
                    img = np.dstack((red, green, blue))
                    show(img, ax=ax, transform=transform)
                else:
                    img = src.read(1)
                    show(img, ax=ax, transform=transform, cmap = 'gray')
                canvas.print_figure(self.temp_image_path, bbox_inches='tight', pad_inches=0)
            
                self.current_file = file_path
                self.imageLoaded.emit(os.path.basename(file_path), self.temp_image_path)
                
                info_text = (
                    f"File: {os.path.basename(file_path)}\n"
                    f"band: {num_bands}\n"
                    f"size: {width} x {height}\n"
                    f"bounds: {bounds}"
                )
                self.infoUpdated.emit(info_text)
        except Exception as e:
            self.errorOccurred.emit(f"Load file error: {str(e)}")
    
    @pyqtSlot
    def openFileDialog(self):
        pass
    
    
if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    
    engine = QQmlApplicationEngine()
    
    backend = TifViewerBackend()
    
    engine.rootContext().setContextProperty("backend", backend)
    
    qml_file = os.path.join(os.path.dirname(__name__), "qml", "main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))
    
    if not engine.rootObjects():
        sys.exit(-1)
        
    sys.exit(app.exec())