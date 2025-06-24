import numpy as np
from PyQt6.QtGui import QImage, QPixmap

class LogTransfer:
    def __init__(self):
        self.log_item = None
        self.log_visible = False
        self.log_layer = None
        
    def apply_log_transfer(self, img_arr):
        img_arr = img_arr.astype(np.float32)
        
        img_max = np.max(img_arr)
        if img_max <= 1e-10:
            return np.zeros_like(img_arr, dtype=np.uint8)
        
        if img_max > 1e10:
            img_arr = img_arr / img_max * 1000
            img_max = 1000
        c = 255.0 / np.log(1 + img_max + 1e-10)
        log_img = np.zeros_like(img_arr)
        valid_mask = img_arr > 0
        log_img[valid_mask] = c * np.log(1 + img_arr[valid_mask])
        log_img = np.nan_to_num(log_img, nan=0.0, posinf=255.0, neginf=0.0)

        return np.clip(log_img, 0, 255).astype(np.uint8)
    
    def create_log_layer(self, scene, img_arr, width, height):
        log_img_arr = self.apply_log_transfer(img_arr)
        
        if len(img_arr.shape) == 3:
            qimage = QImage(
                log_img_arr.data,
                width,
                height,
                3 * width, 
                QImage.Format.Format_RGB888
            )
        else:
            qimage = QImage(
                log_img_arr.data,
                width,
                height,
                width,  
                QImage.Format.Format_Grayscale8
            )
        
        pixmap = QPixmap.fromImage(qimage)
        log_item = scene.addPixmap(pixmap)
        log_item.setVisible(self.log_visible)

        self.log_item = log_item
        self.log_layer = log_img_arr
        
        return log_item, qimage
    
    def toggle_visibility(self):
        if self.log_item:
            self.log_visible = not self.log_visible
            self.log_item.setVisible(self.log_visible)
        return self.log_visible
    
    def clear_log_layer(self):
        if self.log_item:
            self.log_item.setVisible(False)
            self.log_item = None
            self.log_layer = None
            self.log_visible = False
        return self.log_visible