import sys
import os
import numpy as np
import cv2
from PyQt6.QtWidgets import(
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget,
    QLabel, QHBoxLayout, QToolBar, QStatusBar,
    QDockWidget, QListWidget, QMessageBox, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem
)
from PyQt6.QtGui import QAction, QIcon, QPainter, QImage, QPixmap, QFont
from PyQt6.QtCore import Qt, QSize, QEvent
from utils.log_transfer import LogTransfer
from core.tagging_system import TagHandler
from utils.image_adjustment import ImageAdjustment


class TifViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TIF Viewer")
        
        self.current_path = None
        self.folder = None
        self.files = None
        self.vector_layers = {}
        self.active_vector_layers = set()
        self.log_transfer = LogTransfer()
        self.adjust_dock = None
        self.adjustment = ImageAdjustment(self)
        
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
        self.tag_handler = TagHandler(self)
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
        
    def init_layer_dock(self):
        dock = QDockWidget("Layer Control", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dock_widget = QWidget()
        dock_layout = QVBoxLayout(dock_widget) 
        
        self.vector_list=QListWidget()
        self.vector_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.vector_list.itemSelectionChanged.connect(self.handle_layer_selection)
        self.vector_list.itemSelectionChanged.connect(self.adjustment.handle_selected_layer)
        self.vector_list.setFont(QFont('Arial', 25))
        
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16,16))
        
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
        
        open_folder = QAction(QIcon.fromTheme("folder-open"), "Open Folder", self)
        open_folder.setShortcut("Ctrl+Shift+O")
        open_folder.triggered.connect(self.open_folder)
        toolbar.addAction(open_folder)

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
        adjust_action = QAction(QIcon.fromTheme("color-management"), "Adjust Image", self)
        adjust_action.setShortcut("Ctrl+E")
        adjust_action.triggered.connect(self.toggle_adjustment)
        
        toolbar.addAction(adjust_action)
        toolbar.addSeparator()
        
        exit_action = QAction(QIcon.fromTheme("application-exit"), "Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(QApplication.quit)
        toolbar.addAction(exit_action)
        toolbar.addSeparator()
        
        prev_action = QAction(QIcon.fromTheme("go-previous"), "Previous Image", self)
        prev_action.setShortcut("Ctrl+Left")
        prev_action.triggered.connect(self.prev_image)
        toolbar.addAction(prev_action)
        
        next_action = QAction(QIcon.fromTheme("go-next"), "Next Image", self)
        next_action.setShortcut("Ctrl+Right")
        next_action.triggered.connect(self.next_image)
        toolbar.addAction(next_action)
        
        toolbar.addSeparator()
        
    def toggle_adjustment(self):

        if self.adjust_dock is None:
            self.adjust_dock = QDockWidget("Image Adjustments", self)
            self.adjust_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea|Qt.DockWidgetArea.LeftDockWidgetArea)
            self.adjust_dock.setWidget(self.adjustment.create_adjustment_panel())
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.adjust_dock)
            self.adjust_dock.setVisible(True)
        else:
            self.adjust_dock.setVisible(not self.adjust_dock.isVisible())

    def open_folder(self):
        folder_pth = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_pth:
            self.folder = folder_pth
            self.current_file = None
            self.vector_layers.clear()
            self.vector_list.clear()
            self.active_vector_layers.clear()
            self.statusBar.showMessage(f"Opened folder: {folder_pth}", 3000)
            self.files = [f for f in os.listdir(self.folder) if f.lower().endswith(('.tif', '.tiff'))]
            self.current_index = 0
            if not self.files:
                QMessageBox.information(self, "Info", "No TIF files found in the folder.")
                return
            self.next_image()
        
    def next_image(self):
        if not self.folder or not os.path.isdir(self.folder) or not self.files:
            QMessageBox.information(self, "Info", "Please open a folder first.")
            return
        
        if self.log_transfer.log_item:
            print("Clearing log layer and vector list")
            self.log_transfer.clear_log_layer()
            self.vector_list.clear()
            self.log_transfer.log_item = None
            self.adjustment.log_img = None
            
        if self.current_index >= len(self.files):
            QMessageBox.information(self, "Info", "No more images available.")
            return
        
        next_file = os.path.join(self.folder, self.files[self.current_index])
        self.load_tif_file(next_file)
        self.current_index+=1
        
    def prev_image(self):
        if not self.folder or not os.path.isdir(self.folder) or not self.files:
            QMessageBox.information(self, "Info", "Please open a folder first.")
            return
        self.current_index -= 1
        if self.current_index <= 0:
            QMessageBox.information(self, "Info", "No previous image available.")
            return
        prev_file = os.path.join(self.folder, self.files[self.current_index])
        self.load_tif_file(prev_file)

    def open_file(self):
        file_pth, _ = QFileDialog.getOpenFileName(
            self, "","","TIF Files (*.tif *.tiff);;All (*)"
        )
        if file_pth:
            self.current_path = file_pth
            self.folder = os.path.dirname(file_pth)
            self.current_file = os.path.basename(file_pth)
            self.vector_layers.clear()
            self.vector_list.clear()
            self.active_vector_layers.clear()
            self.load_tif_file(file_pth)

    def load_tif_file(self, pth):
        try:
            self.scene.clear()
            self.image_item = QGraphicsPixmapItem()
            self.scene.addItem(self.image_item)
            
            img = cv2.imread(pth, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
            
            if img is None:
                raise ValueError("Failed to load image. Check if the file is corrupted or unsupported.")
            
            height, width = img.shape[:2]
            num_channels = img.shape[2] if len(img.shape) == 3 else 1
            
            info = (
                f"<b>File:</b> {os.path.basename(pth)}<br>"
                f"<b>Channels:</b> {num_channels}<br>"
                f"<b>Size:</b> {width} × {height}<br>"
            )
            
            self.info_label.setText(info)
            
            if num_channels >= 3:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                if img_rgb.dtype != np.uint8:
                    img_rgb = cv2.normalize(img_rgb, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                
                bytes_per_line = 3 * width
                qimage = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            else:
                if img.dtype != np.uint8:
                    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                
                qimage = QImage(img.data, width, height, width, QImage.Format.Format_Grayscale8)
            
            self.adjustment.set_original_image(img)
            
            pixmap = QPixmap.fromImage(qimage)
            self.image_item.setPixmap(pixmap)
            reply = QMessageBox.question(self, 'Log', 'Create log layer?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if self.log_transfer.log_item is None and reply == QMessageBox.StandardButton.Yes:
                img_arr = img_rgb if num_channels >= 3 else img
                self.log_transfer.log_item, log_i = self.log_transfer.create_log_layer(
                    self.scene, img_arr, width, height)
                self.adjustment.set_log_image(log_i)
                self.vector_list.addItem('Log Layer')
            
            self.statusBar.showMessage(f"Loaded: {pth}", 3000)
            self.graphics_view.fitInView(self.image_item, Qt.AspectRatioMode.KeepAspectRatio)
            
        except Exception as e:
            print(str(e))
            self.info_label.setText(f"<b>Error:</b> {str(e)}")
            self.statusBar.showMessage(f"Error: {str(e)}", 5000)
            

    def handle_layer_selection(self):
        selected = self.vector_list.selectedItems()
        selected_texts = [item.text() for item in selected]
        log_layer_selected = "Log Layer" in selected_texts
        tag_layer_selected = "Tag Layer" in selected_texts
        if self.log_transfer.log_item:
            self.log_transfer.log_item.setVisible(log_layer_selected)
        
        if self.tag_handler.tag_list is not None:
            self.tag_handler.set_tags_visible(tag_layer_selected)
            
    def zoom_out(self):
        center = self.graphics_view.mapToScene(self.graphics_view.viewport().rect().center())
        self.graphics_view.scale(1/1.2, 1/1.2)
        self.graphics_view.centerOn(center)

    def zoom_in(self):
        center = self.graphics_view.mapToScene(self.graphics_view.viewport().rect().center())
        self.graphics_view.scale(1.2, 1.2)
        self.graphics_view.centerOn(center)

    def rest_view(self):
        if hasattr(self, 'image_item'):
            self.graphics_view.fitInView(self.image_item, Qt.AspectRatioMode.KeepAspectRatio)
    
    def wheelEvent(self,event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
            old_pos = self.graphics_view.mapToScene(event.position().toPoint())
            
            self.graphics_view.scale(zoom_factor, zoom_factor)
            new_pos = self.graphics_view.mapToScene(event.position().toPoint())
            
            delta = new_pos-old_pos
            self.graphics_view.translate(delta.x(), delta.y())
            
            event.accept()
        else:
            super().wheelEvent(event)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = TifViewer()
    viewer.show()
    sys.exit(app.exec())
