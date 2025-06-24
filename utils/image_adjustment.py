from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import numpy as np


class ImageAdjustment:
    def __init__(self, parent):
        self.parent = parent
        self.original_image = None
        self.log_img = None
        self.current_layers = []
        
    def create_adjustment_panel(self):
        self.adjust_panel = QWidget()
        layout = QVBoxLayout(self.adjust_panel)

        self.brightness_label = QLabel("Brightness: 0")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.update_brightness_value)
        self.brightness_slider.valueChanged.connect(self.adjust_image)
        
        self.contrast_label = QLabel("Contrast: 1.0")
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(0, 200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.update_contrast_value)
        self.contrast_slider.valueChanged.connect(self.adjust_image)
        
        self.min_label = QLabel("Minimum: 0.0")
        self.min_slider = QSlider(Qt.Orientation.Horizontal)
        self.min_slider.setRange(0, 100)
        self.min_slider.setValue(0)
        self.min_slider.valueChanged.connect(self.update_min_value)
        self.min_slider.valueChanged.connect(self.adjust_image)
        
        self.max_label = QLabel("Maximum: 1.0")
        self.max_slider = QSlider(Qt.Orientation.Horizontal)
        self.max_slider.setRange(0, 100)
        self.max_slider.setValue(100)
        self.max_slider.valueChanged.connect(self.update_max_value)
        self.max_slider.valueChanged.connect(self.adjust_image)
        
        self.rest = QPushButton("Rest")
        self.auto = QPushButton("Auto")
        self.rest.clicked.connect(self.rest_change_orginal)
        
        layout.addWidget(self.rest)
        layout.addWidget(self.auto)
        layout.addWidget(QLabel("Brightness:"))
        layout.addWidget(self.brightness_slider)
        layout.addWidget(self.brightness_label)
        layout.addWidget(QLabel("Contrast:"))
        layout.addWidget(self.contrast_slider)
        layout.addWidget(self.contrast_label)
        layout.addWidget(QLabel("Minimum:"))
        layout.addWidget(self.min_slider)
        layout.addWidget(self.min_label)
        layout.addWidget(QLabel("Maximum:"))
        layout.addWidget(self.max_slider)
        layout.addWidget(self.max_label)
        
        return self.adjust_panel
    
    def rest_change_orginal(self):
        if self.original_image is None:
            return
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(100)
        self.min_slider.setValue(0)
        self.max_slider.setValue(100)
        
        self.brightness_label.setText("Brightness: 0")
        self.contrast_label.setText("Contrast: 1.0")
        self.min_label.setText("Minimum: 0.0")
        self.max_label.setText("Maximum: 1.0")
        
        self.update_display(self.original_image)
        self.parent.log_transfer.log_item.setPixmap(QPixmap.fromImage(self.log_img))
        
    def update_brightness_value(self):
        self.brightness_label.setText(f"Brightness: {self.brightness_slider.value()}")
    
    def update_contrast_value(self):
        self.contrast_label.setText(f"Contrast: {self.contrast_slider.value()/100.0:.2f}")
        
    def update_min_value(self):
        self.min_label.setText(f"Minimum: {self.min_slider.value()}")

    def update_max_value(self):
        self.max_label.setText(f"Maximum: {self.max_slider.value()}")

    def set_original_image(self, image):
        self.original_image = image.copy()
        
    def set_log_image(self, image):
        self.log_img = image.copy()

    def handle_selected_layer(self):
        selected_items = self.parent.vector_list.selectedItems()
        self.current_layers = [item.text() for item in selected_items]
        #self.adjust_image()
            
    def adjust_image(self):
        if not hasattr(self.parent, 'image_item') or self.parent.image_item is None:
            return
        if not hasattr(self, 'brightness_slider'):
            return
        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value() / 100.0
        min_val = self.min_slider.value() / 100.0
        max_val = self.max_slider.value() / 100.0

        if not self.current_layers: 
            if self.original_image is None:
                return
            img = self.apply_adjustments(
                self.original_image.copy(),
                brightness,
                contrast,
                min_val,
                max_val
            )
            self.update_display(img)
        else:
            for layer_name in self.current_layers:
                if layer_name == "Log Layer" and hasattr(self.parent.log_transfer, 'log_item'):
                    log_item = self.parent.log_transfer.log_item
                    if log_item:
                        img = self.qimage_to_numpy(self.log_img)
                        adjusted_img = self.apply_adjustments(img, brightness, contrast, min_val, max_val)
                        log_item.setPixmap(QPixmap.fromImage(self.numpy_to_qimage(adjusted_img)))

    def apply_adjustments(self, img, brightness, contrast, min_val, max_val):
        img = img.astype(np.float32)
        img = (img - img.min()) / (img.max() - img.min())
        if min_val > 0 or max_val < 1 and min_val!=max_val:
            img = np.clip((img - min_val) / (max_val - min_val), 0, 1)
        img = img * 255 * contrast + brightness
        return np.clip(img, 0, 255).astype(np.uint8)

    def update_display(self, img):
        if img is None or img.size == 0:
            return
        qimg = self.numpy_to_qimage(img)
        self.parent.image_item.setPixmap(QPixmap.fromImage(qimg))

    def numpy_to_qimage(self, img):
        height, width = img.shape[:2]
        if len(img.shape) == 3:
            bytes_per_line = 3 * width
            fmt = QImage.Format.Format_RGB888
            if img.shape[2] == 4:
                bytes_per_line = 4*width
                fmt = QImage.Format.Format_RGBA8888

        else:
            bytes_per_line = width
            fmt = QImage.Format.Format_Grayscale8
        data = img.tobytes()
        qimage = QImage(data, width, height, bytes_per_line, fmt)
        return qimage.copy()

    def qimage_to_numpy(self, qimage):
        width = qimage.width()
        height = qimage.height()
        bytes_per_line = qimage.bytesPerLine()

        if qimage.format() == QImage.Format.Format_RGB32:
            qimage = qimage.convertToFormat(QImage.Format.Format_RGBA8888)
        elif qimage.format() == QImage.Format.Format_ARGB32:
            qimage = qimage.convertToFormat(QImage.Format.Format_RGBA8888)
        elif qimage.format() == QImage.Format.Format_RGB888:
            qimage = qimage.convertToFormat(QImage.Format.Format_RGBA8888)

        ptr = qimage.bits()
        ptr.setsize(qimage.sizeInBytes())

        if qimage.format() == QImage.Format.Format_RGBA8888:
            arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, bytes_per_line // 4, 4))
            arr = arr[:, :width, :4] 
            return arr[..., [2, 1, 0, 3]]
        elif qimage.format() == QImage.Format.Format_RGB888:
            arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, bytes_per_line // 3, 3))
            arr = arr[:, :width, :3]
            return arr[..., [2, 1, 0]]
        elif qimage.format() == QImage.Format.Format_Grayscale8:
            arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, bytes_per_line))
            return arr[:, :width]
        else:
            raise ValueError(f"Unsupported image format: {qimage.format()}")
    
