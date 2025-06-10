import os
import numpy as np
import rasterio
from PyQt6.QtWidgets import QFileDialog,QGraphicsPixmapItem
from PyQt6.QtGui import QImage, QPixmap

class FileHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        
    def open_file(self):
        file_pth, _ = QFileDialog.getOpenFileName(
            self.main_window, "", "", "TIF Files (*.tif *.tiff);;All (*)"
        )
        if file_pth:
            self.main_window.current_path = file_pth
            self.main_window.vector_layers.clear()
            self.main_window.vector_list.clear()
            self.main_window.active_vector_layers.clear()
            self.load_tif_file(file_pth)
            
    def load_tif_file(self, pth):
        try:
            self.main_window.scene.clear()
            self.main_window.image_item = QGraphicsPixmapItem()
            self.main_window.scene.addItem(self.main_window.image_item)
            
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
                
                self.main_window.info_label.setText(info)
                
                if num_bands >= 3:
                    red = src.read(1)
                    green = src.read(2)
                    blue = src.read(3)
                    img = np.dstack((red, green, blue))
                    img = (img * 255.0 / img.max()).astype(np.uint8)

                    height, width, _ = img.shape
                    bytes_per_line = 3 * width
                    qimage = QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_RGBA8888)
                    
                else:
                    img = src.read(1)
                    img = (img * 255.0 / img.max()).astype(np.uint8)
                    height, width = img.shape
                    qimage = QImage(img.data, width, height, width, QImage.Format.Format_Grayscale8)
                    
                pixmap = QPixmap.fromImage(qimage)
                self.main_window.image_item.setPixmap(pixmap)
                
                self.main_window.current_transform = transform
                self.main_window.current_bounds = bounds
                
                self.main_window.ui_initializer.setup_mpl_canvas()  # 重新初始化Matplotlib画布
                self.main_window.statusBar.showMessage(f"Loaded: {pth}", 3000)
                
                self.main_window.graphics_controller.fit_view_to_image()
        
        except Exception as e:
            print(str(e))
            self.main_window.info_label.setText(f"<b>Error:</b> {str(e)}")
            self.main_window.statusBar.showMessage(f"Error: {str(e)}", 5000)