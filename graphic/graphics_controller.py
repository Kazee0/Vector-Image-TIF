from PyQt6.QtCore import Qt, QPointF, QRectF

class GraphicsController:
    def __init__(self, main_window):
        self.main_window = main_window
        
    def zoom_in(self):
        center = self.main_window.graphics_view.mapToScene(
            self.main_window.graphics_view.viewport().rect().center()
        )
        self.main_window.graphics_view.scale(1.2, 1.2)
        self.main_window.graphics_view.centerOn(center)
        self.update_mpl_canvas_size()
    
    def zoom_out(self):
        center = self.main_window.graphics_view.mapToScene(
            self.main_window.graphics_view.viewport().rect().center()
        )
        self.main_window.graphics_view.scale(1/1.2, 1/1.2)
        self.main_window.graphics_view.centerOn(center)
        self.update_mpl_canvas_size()
    
    def reset_view(self):
        if hasattr(self.main_window, 'image_item'):
            self.main_window.graphics_view.fitInView(
                self.main_window.image_item, 
                Qt.AspectRatioMode.KeepAspectRatio
            )
            self.update_mpl_canvas_size()
    
    def fit_view_to_image(self):
        if hasattr(self.main_window, 'image_item'):
            self.main_window.graphics_view.fitInView(
                self.main_window.image_item, 
                Qt.AspectRatioMode.KeepAspectRatio
            )
    
    def update_mpl_canvas_size(self):
        if not hasattr(self.main_window, 'mpl_proxy'):
            return
            
        view_rect = self.main_window.graphics_view.mapToScene(
            self.main_window.graphics_view.viewport().rect()
        ).boundingRect()
        
        self.main_window.mpl_proxy.setPos(view_rect.center())
        self.main_window.mpl_proxy.setGeometry(QRectF(0, 0, view_rect.width(), view_rect.height()))