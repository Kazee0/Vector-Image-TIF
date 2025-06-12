from PyQt6.QtWidgets import QListWidget, QDockWidget, QWidget, QVBoxLayout, QToolBar, QLabel, QMessageBox, QFileDialog
from PyQt6.QtGui import QIcon, QFont, QAction
from PyQt6.QtCore import Qt, QSize
import matplotlib.pyplot as plt


class TagHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tags = {}  
        self.tag_list = None
        self.tag_dock = None
        self.drawing = False
        self.current_rect = None
        self.start_pos = None

        self.ax = None
        self.init_tag_layer()
        
    def init_tag_layer(self):
        if not self.main_window.mpl_canvas:
            self.main_window.init_mpl_canvas()
            
        self.ax = self.main_window.mpl_figure.add_subplot(111)
        self.ax.set_aspect('equal')
        self.ax.axis('off') 
        
        self.main_window.mpl_canvas.setVisible(True)
        
        self.create_tag_dock()
        
        self.connect_events()
        
    def create_tag_dock(self):
        self.tag_dock = QDockWidget("Tag Control", self.main_window)
        self.tag_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        
        dock_widget = QWidget()
        dock_layout = QVBoxLayout(dock_widget)

        self.tag_list = QListWidget()
        self.tag_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.tag_list.itemSelectionChanged.connect(self.handle_tag_selection)
        self.tag_list.setFont(QFont('Arial', 10))
        
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        
        add_tag_action = QAction(QIcon.fromTheme("edit-select-rectangle"), "Add Tag", self.main_window)
        add_tag_action.triggered.connect(self.start_drawing)
        
        delete_tag_action = QAction(QIcon.fromTheme("edit-delete"), "Delete Tag", self.main_window)
        delete_tag_action.triggered.connect(self.delete_selected_tag)
        
        save_tags_action = QAction(QIcon.fromTheme("document-save"), "Save Tags", self.main_window)
        save_tags_action.triggered.connect(self.save_tags)
        
        load_tags_action = QAction(QIcon.fromTheme("document-open"), "Load Tags", self.main_window)
        load_tags_action.triggered.connect(self.load_tags)
        
        toolbar.addAction(add_tag_action)
        toolbar.addAction(delete_tag_action)
        toolbar.addSeparator()
        toolbar.addAction(save_tags_action)
        toolbar.addAction(load_tags_action)
        
        # 添加组件到布局
        dock_layout.addWidget(QLabel("Tags:"))
        dock_layout.addWidget(toolbar)
        dock_layout.addWidget(self.tag_list)
        
        self.tag_dock.setWidget(dock_widget)
        self.main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.tag_dock)
        
    def load_tags(self):
        pass
    
    def save_tags(self):
        pass
    
    def delete_selected_tag(self):
        pass
    
    def start_drawing(self):
        pass
    
    def handle_tag_selection(self):
        pass
    def connect_events(self):
        pass
    def update_canvas_size(self):
        pass