import sys
import os
import numpy as np
import rasterio
from rasterio.plot import show
import geopandas as gpd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import(
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget,
    QLabel, QHBoxLayout, QScrollArea, QToolBar, QStatusBar,
    QDockWidget, QListWidget, QMessageBox, QSplitter
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QSize


class TifViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TIF Viewer")
        
        self.current_path = None #Log Current Working Path
        
        self.vector_layers = {} #Store Layers
        self.active_vector_layers = set()
        
        self.init_ui()
    
    def init_ui(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(5,5,5,5)
        
        self.init_layer_dock()
        
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.main_layout.addWidget(self.right_panel, stretch=3)
        
        self.create_toolbar()
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.init_image_display()
        
        self.info_label = QLabel("Open a TIF file")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.info_label.setWordWrap(True)
        self.right_layout.addWidget(self.info_label)
        
    def init_layer_dock(self):
        dock = QDockWidget("Layer Control", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dock_widget = QWidget()
        dock_layout = QVBoxLayout(dock_widget) 
        
        self.vector_list=QListWidget()
        self.vector_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.vector_list.itemSelectionChanged.connect(self.updata_vecotr_visilibity)
        
        add_btn = QAction(QIcon.fromTheme("document-open"), "Add Layer", self)
        
        dock.setWidget(dock_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        
    def init_image_display(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.right_layout.addWidget(self.scroll_area, stretch=1)
        
        self.figure = Figure(figsize=(8,6), dpi=100)
        self.canvas=FigureCanvas(self.figure)
        self.scroll_area.setWidget(self.canvas)
        
        self.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.canvas.setMouseTracking(True)
        
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        
        self.scroll_area.setWidget(self.canvas)
        
    def on_scroll(self, event):
        if event.key == 'control':
            print('on-scroll')
            x = event.xdata
            y = event.ydata
            
            if x is None or y is None:
                ax = self.figure.gca()
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                x = (xlim[0]+xlim[1])/2
                y = (ylim[0]+ylim[1])/2
            
            zoom_factor = 0.9 if event.step > 0 else 1.1
            self.zoom_at_point(x, y, zoom_factor)
            
    def zoom_at_point(self, x, y, zoom_factor):
        if not hasattr(self,'ax'):
            return
        
        ax = self.ax
        
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        new_width=(xlim[1]-ylim[0])*zoom_factor
        new_height=(ylim[1]-ylim[0])*zoom_factor
        
        new_xlim = [
            x - (x-xlim[0])* zoom_factor,
            x+(xlim[1]-x) * zoom_factor
        ]
        new_ylim = [
            y-(y-ylim[0])*zoom_factor,
            y+(ylim[1]-y)*zoom_factor
        ]
        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)
        
        self.canvas.draw()
    
    def create_toolbar(self):
        toolbar = QToolBar("Main Tool Bar")
        toolbar.setIconSize(QSize(24,24))
        self.addToolBar(toolbar)
        
        open_action = QAction(QIcon.fromTheme("document-open"), "Open TIF", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        zoom_in_action = QAction(QIcon.fromTheme("zoom-in"), "Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction(QIcon.fromTheme("zoom-out"), "Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        toolbar.addSeparator()
        
        rest_view_action = QAction(QIcon.fromTheme("zoom-orginal"),"Rest", self)
        rest_view_action.triggered.connect(self.rest_view)
        toolbar.addAction(rest_view_action)
    
    def open_file(self):
        file_pth, _ = QFileDialog.getOpenFileName(
            self, "","","TIF Files (*.tif *.tiff);;All (*)"
        )
        if file_pth:
            self.current_path = file_pth
            self.vector_layers.clear()
            self.vector_list.clear()
            self.active_vector_layers.clear()
            self.display_tif(file_pth)

    def display_tif(self, pth):
        try:
            self.figure.clear()
            with rasterio.open(pth) as src:
                num_bands = src.count
                width = src.width
                height = src.height
                crs = src.crs
                transform = src.transform
                bounds = src.bounds
                
                info=(
                     f"<b>文件:</b> {os.path.basename(pth)}<br>"
                    f"<b>波段数:</b> {num_bands}<br>"
                    f"<b>尺寸:</b> {width} × {height}<br>"
                    f"<b>坐标系统:</b> {crs if crs else '无'}<br>"
                    f"<b>范围:</b> {bounds}"
                )
                self.info_label.setText(info)
                
                self.ax = self.figure.add_subplot(111)
                if num_bands >=3:
                    red = src.read(1)
                    green = src.read(2)
                    blue = src.read(3)
                    img = np.dstack((red, green, blue))
                    show(img, ax =self.ax, transform=transform)
                else:
                    img = src.read(1)
                    show(img, ax=self.ax, transform=transform, cmap="gray")
                    
                self.current_transform = transform
                self.current_bound = bounds
                
                self.draw_vector_layers()
                
                self.canvas.draw()
                
                self.status_bar.showMessage(f"Loaded: {pth}", 3000)
        except Exception as e:
            self.info_label.setText(f"<b>Error:</b> {str(e)}")
            self.status_bar.showMessage(f"Error: {str(e)}", 5000)

    def draw_vector_layers(self):
        pass
    
    def updata_vecotr_visilibity(self):
        pass
    def zoom_out(self):
        if hasattr(self, 'ax'):
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            self.ax.set_xlim([x*1.1 for x in xlim])
            self.ax.set_ylim([y*1.1 for y in ylim])
            self.canvas.draw()
    
    def zoom_in(self):
        if hasattr(self, 'ax'):
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            self.ax.set_xlim([x*0.9 for x in xlim])
            self.ax.set_ylim([y*0.9 for y in ylim]) 
            self.canvas.draw()
    
    def rest_view(self):
        pass
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = TifViewer()
    viewer.show()
    sys.exit(app.exec())
        