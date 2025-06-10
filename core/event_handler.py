from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QWheelEvent

class EventHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        
    def connect_signals(self):
        self.main_window.open_action.triggered.connect(self.main_window.file_handler.open_file)
        self.main_window.zoom_in_action.triggered.connect(self.main_window.graphics_controller.zoom_in)
        self.main_window.zoom_out_action.triggered.connect(self.main_window.graphics_controller.zoom_out)
        self.main_window.reset_view_action.triggered.connect(self.main_window.graphics_controller.reset_view)
        

        self.main_window.vector_list.itemSelectionChanged.connect(
            self.main_window.updata_vecotr_visilibity
        )
        
    def eventFilter(self, source, event):
        if (source is self.main_window.graphics_view.viewport() 
            and event.type() == QEvent.Type.Wheel):
            self.wheelEvent(event)
            return True
        return super(self.main_window, self.main_window).eventFilter(source, event)
    
    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
            old_pos = self.main_window.graphics_view.mapToScene(event.position().toPoint())
            
            self.main_window.graphics_view.scale(zoom_factor, zoom_factor)
            new_pos = self.main_window.graphics_view.mapToScene(event.position().toPoint())
            
            delta = new_pos - old_pos
            self.main_window.graphics_view.translate(delta.x(), delta.y())
            self.main_window.graphics_controller.update_mpl_canvas_size()
            
            event.accept()
        else:
            super(self.main_window, self.main_window).wheelEvent(event)
    
    def resizeEvent(self, event):
        super(self.main_window, self.main_window).resizeEvent(event)
        self.main_window.graphics_controller.update_mpl_canvas_size()