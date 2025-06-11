import sys
import os
import numpy as np
import rasterio, cv2
from rasterio.plot import show
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import(
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget,
    QLabel, QHBoxLayout, QScrollArea, QToolBar, QStatusBar,
    QDockWidget, QListWidget, QMessageBox, QSplitter, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem
)
from PyQt6.QtGui import QAction, QIcon, QPainter, QImage, QPixmap, QFont
from PyQt6.QtCore import Qt, QSize, QRectF, QEvent
from utils.log_transfer import LogTransfer

class TifViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TIF Viewer")
        
        self.current_path = None #Log Current Working Path
        
        self.vector_layers = {} #Store Layers
        self.active_vector_layers = set()
        self.log_transfer = LogTransfer()
        self.init_ui()
        
    def eventFilter(self, source, event):
        if(source is self.graphics_view.viewport()and event.type()==QEvent.Type.Wheel):
            self.wheelEvent(event)
            return True
        return super().eventFilter(source, event)
    
    def init_ui(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(2,2,2,2)
        
        self.init_layer_dock()
        
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.right_panel, stretch=5)
        
        self.init_graphics_view()
        self.init_mpl_canvas()
        
        self.create_toolbar()
        self.statusBar = QStatusBar() 
        self.setStatusBar(self.statusBar)
        
        self.info_label = QLabel("Open a TIF file")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.info_label.setWordWrap(True)
        self.right_layout.addWidget(self.info_label)
        
    def init_graphics_view(self):
        self.graphics_view = QGraphicsView()
        self.graphics_view.viewport().installEventFilter(self)
        self.graphics_view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.graphics_view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.graphics_view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.graphics_view.setMouseTracking(True)
        self.scene = QGraphicsScene(-10000, -10000, 20000, 20000)
        self.graphics_view.setScene(self.scene) 
        self.right_layout.addWidget(self.graphics_view, stretch=1)
        
        self.image_item = QGraphicsPixmapItem()
        self.scene.addItem(self.image_item)

    def init_mpl_canvas(self):
        self.mpl_figure = Figure(facecolor='none')
        self.mpl_canvas = FigureCanvas(self.mpl_figure)
        self.mpl_canvas.setVisible(False)
        
        self.mpl_proxy = self.scene.addWidget(self.mpl_canvas)
        self.mpl_proxy.setZValue(1)
        
    def init_layer_dock(self):
        dock = QDockWidget("Layer Control", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dock_widget = QWidget()
        dock_layout = QVBoxLayout(dock_widget) 
        
        self.vector_list=QListWidget()
        self.vector_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.vector_list.itemSelectionChanged.connect(self.handle_layer_selection)
        self.vector_list.setFont(QFont('Arial', 30))
        add_btn = QAction(QIcon.fromTheme("document-open"), "Add Layer", self)
        add_btn.triggered.connect(self.add_vector_layer)
        
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16,16))
        toolbar.addAction(add_btn)
        
        dock_layout.addWidget(QLabel("Layers:"))
        dock_layout.addWidget(toolbar)
        dock_layout.addWidget(self.vector_list)
        
        dock.setWidget(dock_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
  
    def create_toolbar(self):
        toolbar = QToolBar("Main Tool Bar")
        toolbar.setIconSize(QSize(24,24))
        self.addToolBar(toolbar)
        
        open_action = QAction(QIcon.fromTheme("document-open"), "Open TIF", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction(QIcon.fromTheme("document-save"),"Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        toolbar.addSeparator()
        
        zoom_in_action = QAction(QIcon.fromTheme("zoom-in"), "Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction(QIcon.fromTheme("zoom-out"), "Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        
        rest_view_action = QAction(QIcon.fromTheme("zoom-original"),"Reset", self)
        rest_view_action.triggered.connect(self.rest_view)
        toolbar.addAction(rest_view_action)
        
        toolbar.addSeparator()
            
    def open_file(self):
        file_pth, _ = QFileDialog.getOpenFileName(
            self, "","","TIF Files (*.tif *.tiff);;All (*)"
        )
        if file_pth:
            self.current_path = file_pth
            self.vector_layers.clear()
            self.vector_list.clear()
            self.active_vector_layers.clear()
            self.load_tif_file(file_pth)
            
    def save_file(self):
        filepath, filetype = QFileDialog.getSaveFileName(self, "",self.current_path, "TIFF Files(*tif)")
        print(filepath, filetype)
        if not filepath:
            return
        if not filepath.lower().endswith(('.tif','.tiff')):
            filepath+='.tif'
        try: 
            if not self.scene.items():
                raise ValueError("场景中没有图像")
            
            pixmap_item = self.scene.items()[0]
            qimage = self.image_item.pixmap().toImage()

            if qimage.format() not in (QImage.Format.Format_RGB888, QImage.Format.Format_RGBA8888):
                qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
            

            width = qimage.width()
            height = qimage.height()
            bytes_per_line = qimage.bytesPerLine()
            channels = 4 if qimage.hasAlphaChannel() else 3
            
            ptr = qimage.bits()
            ptr.setsize(height * bytes_per_line)
            arr = np.frombuffer(ptr, np.uint8)
            
            if bytes_per_line == width * channels:
                arr = arr.reshape((height, width, channels))
            else:
                arr = arr.reshape((height, bytes_per_line))[:, :width*channels]
                arr = arr.reshape((height, width, channels))

            if channels == 3:
                cv_image = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            elif channels == 4:
                cv_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
            else:
                cv_image = arr
            if not cv2.imwrite(filepath, cv_image):
                raise ValueError("Saving Filed")
                
            QMessageBox.information(self, "Success", f"图像已保存为:\n{filepath}")
            self.cwd = os.path.dirname(filepath)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"保存文件时出错:\n{str(e)}")

    def load_tif_file(self, pth):
        try:
            self.scene.clear()
            self.image_item=QGraphicsPixmapItem()
            self.scene.addItem(self.image_item)
            
            with rasterio.open(pth) as src:
                num_bands = src.count
                width = src.width
                height = src.height
                crs = src.crs
                transform = src.transform
                bounds = src.bounds
                info = (
                    f"<b>File:</b> {os.path.basename(pth)}<br>"
                    f"<b>Bands:</b> {num_bands}<br>"
                    f"<b>Size:</b> {width} × {height}<br>"
                    f"<b>Cor System:</b> {crs if crs else '无'}<br>"
                    f"<b>Bounds:</b> {bounds}"
                )
                
                self.info_label.setText(info)
                
                if num_bands >= 3:
                    red = src.read(1)
                    green = src.read(2)
                    blue = src.read(3)
                    img = np.dstack((red, green, blue))
                    img = (img*255.0 / img.max()).astype(np.uint8)

                    height, width,_ = img.shape
                    bytes_per_line = 3*width
                    qimage = QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_RGBA8888)
                    
                else:
                    img = src.read(1)
                    img = (img*255.0 / img.max()).astype(np.uint8)
                    height, width = img.shape
                    qimage=QImage(img.data, width, height, width, QImage.Format.Format_Grayscale8)
                    
                pixmap = QPixmap.fromImage(qimage)
                self.image_item.setPixmap(pixmap)
                
                self.current_transform = transform
                self.current_bounds = bounds
                reply = QMessageBox.question(self, 'Log', 'Create log layer?', QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
                
                if self.log_transfer.log_item is None and reply:
                    if num_bands>= 3:
                        img_arr = np.dstack((src.read(1), src.read(2), src.read(3)))
                    else:
                        img_arr = src.read(1)
                        
                    self.log_transfer.log_item = self.log_transfer.create_log_layer(self.scene, img_arr, src.width, src.height)
                    self.vector_list.addItem('Log Layer')
                self.init_mpl_canvas()
                self.statusBar.showMessage(f"Loaded: {pth}", 3000)
                
                self.graphics_view.fitInView(self.image_item, Qt.AspectRatioMode.KeepAspectRatio)
        
        except Exception as e:
            print(str(e))
            self.info_label.setText(f"<b>Error:</b> {str(e)}")
            self.statusBar.showMessage(f"Error: {str(e)}", 5000)
    
    def handle_layer_selection(self):
        selected = self.vector_list.selectedItems()
        log_layer_selected = "Log Layer" in [item.text() for item in selected]
        if self.log_transfer.log_item:
            self.log_transfer.log_item.setVisible(log_layer_selected)
    
    def add_vector_layer(self):
        pass
    
    def draw_vector_layers(self):
        pass

    def update_mpl_canvas_size(self):
        if not hasattr(self, 'mpl_proxy'):
            return
        view_rect = self.graphics_view.mapToScene(self.graphics_view.viewport().rect()).boundingRect()
        self.mpl_proxy.setPos(view_rect.center())
        self.mpl_proxy.setGeometry(QRectF(0,0,view_rect.width(), view_rect.height()))
        
    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.update_mpl_canvas_size()
        
    def zoom_out(self):
        center = self.graphics_view.mapToScene(self.graphics_view.viewport().rect().center())
        self.graphics_view.scale(1/1.2, 1/1.2)
        self.graphics_view.centerOn(center)
        self.update_mpl_canvas_size()
    
    def zoom_in(self):
        center = self.graphics_view.mapToScene(self.graphics_view.viewport().rect().center())
        self.graphics_view.scale(1.2, 1.2)
        self.graphics_view.centerOn(center)
        self.update_mpl_canvas_size()
    
    def rest_view(self):
        if hasattr(self, 'image_item'):
            self.graphics_view.fitInView(self.image_item, Qt.AspectRatioMode.KeepAspectRatio)
            self.update_mpl_canvas_size()
    
    def wheelEvent(self,event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
            old_pos = self.graphics_view.mapToScene(event.position().toPoint())
            
            self.graphics_view.scale(zoom_factor, zoom_factor)
            new_pos = self.graphics_view.mapToScene(event.position().toPoint())
            
            delta = new_pos-old_pos
            self.graphics_view.translate(delta.x(), delta.y())
            self.update_mpl_canvas_size()
            
            event.accept()
        else:
            super().wheelEvent(event)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = TifViewer()
    viewer.show()
    sys.exit(app.exec())
