from PyQt6.QtWidgets import QMainWindow
from core import UIInitializer
from utils import FileHandler
from graphic import GraphicsController
from core import EventHandler

class TifViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_path = None
        self.vector_layers = {}
        self.active_vector_layers = set()
        
        self.ui_initializer = UIInitializer(self)
        self.ui_initializer.setup_ui()

        self.file_handler = FileHandler(self)
        self.graphics_controller = GraphicsController(self)
        self.event_handler = EventHandler(self)
        
        self.event_handler.connect_signals()