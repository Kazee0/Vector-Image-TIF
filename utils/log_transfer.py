import numpy as np
from PyQt6.QtGui import QImage, QPixmap
class LogTransfer:
    def __init__(self):
        self.log_item = None
        self.log_visible = None
        self.log_layer = None
        
    def apply_log_transfer(self, img_arr):
        c = 255.0 / np.log(1+np.max(img_arr)) if np.max(img_arr) != 0 else 255.0
        log_img = c * np.log(1+img_arr)
        return log_img.astype(np.uint8)
    
    def create_log_layer(self, scene, img_arr, width, height):
        log_img_arr = self.apply_log_transfer(img_arr)
        
        if len(img_arr.shape) == 3:
            qimge = QImage(
                log_img_arr.data,
                width,
                height,
                3*width,
                QImage.Format.Format_RGB888
            )
        else:
            qimge = QImage(
                log_img_arr.data,
                width,
                height,
                width,
                QImage.Format.Format_Grayscale8
            )
        
        pixmap = QPixmap.fromImage(qimge)
        log_item = scene.addPixmap(pixmap)
        log_item.setVisible(False)
        return log_item, qimge
    
    def toggle_visibility(self, log_item):
        log_item.setVisible(not log_item.isVisible())
        return log_item.isVisible()
