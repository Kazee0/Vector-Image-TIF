from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QToolBar, 
    QStatusBar, QDockWidget, QListWidget, QGraphicsView, 
    QGraphicsScene, QGraphicsPixmapItem, 
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtGui import QIcon, QPainter, QAction
from PyQt6.QtCore import Qt, QSize, QRectF
from matplotlib.figure import Figure

class UIInitializer:
    def __init__(self, main_window) -> None:
        self.main_window=main_window
        
    def setup_ui(self):
        self.main_window.setWindowTitle("TIF Viewer")
        
        self.setup_main_widget()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_info_label()
        self.setup_graphics_view()
        self.setup_mpl_canvas()
    
        self.setup_layer_dock()
        
    def setup_main_widget(self):
        self.main_window.main_widget = QWidget()
        self.main_window.setCentralWidget(self.main_window.main_widget)
        
        self.main_window.main_layout = QHBoxLayout(self.main_window.main_widget)
        self.main_window.main_layout.setContentsMargins(2, 2, 2, 2)
        
        self.setup_right_panel()
        
    def setup_right_panel(self):
        self.main_window.right_panel = QWidget()
        self.main_window.right_layout = QVBoxLayout(self.main_window.right_panel)
        self.main_window.right_layout.setContentsMargins(0, 0, 0, 0)
        self.main_window.main_layout.addWidget(self.main_window.right_panel, stretch=5)
        
    def setup_graphics_view(self):
        self.main_window.graphics_view = QGraphicsView()
        self.main_window.graphics_view.viewport().installEventFilter(self.main_window)
        self.main_window.graphics_view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.main_window.graphics_view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.main_window.graphics_view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.main_window.graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.main_window.graphics_view.setMouseTracking(True)
        
        self.main_window.scene = QGraphicsScene(-10000, -10000, 20000, 20000)
        self.main_window.graphics_view.setScene(self.main_window.scene)
        self.main_window.right_layout.addWidget(self.main_window.graphics_view, stretch=1)
        
        self.main_window.image_item = QGraphicsPixmapItem()
        self.main_window.scene.addItem(self.main_window.image_item)
        
    def setup_mpl_canvas(self):
        self.main_window.mpl_figure = Figure(facecolor='none')
        self.main_window.mpl_canvas = FigureCanvas(self.main_window.mpl_figure)
        self.main_window.mpl_canvas.setVisible(False)
        
        self.main_window.mpl_proxy = self.main_window.scene.addWidget(self.main_window.mpl_canvas)
        self.main_window.mpl_proxy.setZValue(1)
        
    def setup_layer_dock(self):
        dock = QDockWidget("Layer Control", self.main_window)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dock_widget = QWidget()
        dock_layout = QVBoxLayout(dock_widget)
        
        self.main_window.vector_list = QListWidget()
        self.main_window.vector_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        add_btn = QAction(QIcon.fromTheme("document-open"), "Add Layer", self.main_window)
        
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        toolbar.addAction(add_btn)
        
        dock_layout.addWidget(QLabel("Vector Layer:"))
        dock_layout.addWidget(toolbar)
        dock_layout.addWidget(self.main_window.vector_list)
        
        dock.setWidget(dock_widget)
        self.main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        
    def setup_toolbar(self):
        toolbar = QToolBar("Main Tool Bar")
        toolbar.setIconSize(QSize(24, 24))
        self.main_window.addToolBar(toolbar)
        
        open_action = QAction(QIcon.fromTheme("document-open"), "Open TIF", self.main_window)
        open_action.setShortcut("Ctrl+O")
        self.main_window.open_action = open_action
        
        zoom_in_action = QAction(QIcon.fromTheme("zoom-in"), "Zoom In", self.main_window)
        zoom_in_action.setShortcut("Ctrl++")
        self.main_window.zoom_in_action = zoom_in_action
        
        zoom_out_action = QAction(QIcon.fromTheme("zoom-out"), "Zoom Out", self.main_window)
        zoom_out_action.setShortcut("Ctrl+-")
        self.main_window.zoom_out_action = zoom_out_action
        
        reset_view_action = QAction(QIcon.fromTheme("zoom-original"), "Reset", self.main_window)
        self.main_window.reset_view_action = reset_view_action
        
        toolbar.addAction(open_action)
        toolbar.addSeparator()
        toolbar.addAction(zoom_in_action)
        toolbar.addAction(zoom_out_action)
        toolbar.addSeparator()
        toolbar.addAction(reset_view_action)
        
    def setup_statusbar(self):
        self.main_window.statusBar = QStatusBar()
        self.main_window.setStatusBar(self.main_window.statusBar)
        
    def setup_info_label(self):
        self.main_window.info_label = QLabel("Open a TIF file")
        self.main_window.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.main_window.info_label.setWordWrap(True)
        self.main_window.right_layout.addWidget(self.main_window.info_label)