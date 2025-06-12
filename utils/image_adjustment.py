from PyQt6.QtWidgets import QDialog, QSlider, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import numpy as np

class ImageAdjustment:
    def __init__(self, parent):
        self.parent = parent
        self.original_image = None
        
    def create_adjustment_panel(self):
        self.adjust_panel = QWidget()
        layout = QVBoxLayout(self.adjust_panel)
        
        self.brightness_label = QLabel("Brightness: 0")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100,100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.adjust_image)
        self.brightness_slider.valueChanged.connect(self.update_brightness_value)
        
        self.contrast_label = QLabel("Contrast: 1.0")
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(0,200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.adjust_image)
        self.contrast_slider.valueChanged.connect(self.update_contrast_value)
        self.contrast_slider    
        
        layout.addWidget(QLabel("Brightness:"))
        layout.addWidget(self.brightness_slider)
        layout.addWidget(self.brightness_label)
        layout.addWidget(QLabel("Contrast:"))
        layout.addWidget(self.contrast_slider)
        layout.addWidget(self.contrast_label)
        
        self.minimum_label = QLabel("Minimum: 0")
        self.minimum_slider = QSlider(Qt.Orientation.Horizontal)
        self.minimum_slider.setRange(0, 100)
        self.minimum_slider.setValue(0)
        self.minimum_slider.valueChanged.connect(self.adjust_image)
        self.minimum_slider.valueChanged.connect(self.update_minimum_value)
        
        self.maximum_label = QLabel("Maximum: 100")
        self.maximum_slider =  QSlider(Qt.Orientation.Horizontal)
        self.maximum_slider.setRange(0,100)
        self.maximum_slider.setValue(100)
        self.maximum_slider.valueChanged.connect(self.adjust_image)
        self.maximum_slider.valueChanged.connect(self.update_maximum_value)
        
        layout.addWidget(QLabel("Maximum"))
        layout.addWidget(self.maximum_slider)
        layout.addWidget(self.maximum_label)
        layout.addWidget(QLabel("Minimum"))
        layout.addWidget(self.minimum_slider)
        layout.addWidget(self.minimum_label)
        
        return self.adjust_panel
    
    def update_brightness_value(self):
        self.brightness_label.setText(f"Brightness: {self.brightness_slider.value()}")
    
    def update_contrast_value(self):
        self.contrast_label.setText(f"Contrast:{(self.contrast_slider.value()/ 100.0):.2f}")
        
    def update_maximum_value(self):
        self.maximum_label.setText(f"Maxinimum: {self.maximum_slider.value()}")

    def update_minimum_value(self):
        self.minimum_label.setText(f"Minimum: {self.minimum_slider.value()}")

    def set_original_image(self, image):
        self.original_image = image.copy()
        
    def adjust_image(self):
        self.minimum_label.setText(f"Minimum: {self.minimum_slider.value()}")
        self.minimum_label.update()
        if self.original_image is None or not hasattr(self.parent, "image_item"):
            return
        
        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value() / 100.0
        max_val = self.maximum_slider.value()/ 100.0
        min_val = self.minimum_slider.value()/ 100.0
        
        img = self.original_image.copy().astype(np.float32)
        img = (img-img.min()) / (img.max()- img.min())
        
        if min_val > 0 or max_val < 1 and min_val!=max_val:
            img = np.clip((img-min_val)/(max_val-min_val), 0, 1)
            
        img = (img*255).astype(np.uint8)
        img = np.clip(img.astype(np.float32)*contrast+brightness, 0 , 255.0).astype(np.uint8)
        
        height, width = img.shape[:2]
        if len(img.shape) == 3:
            bytes_per_line = 3 * width
            fmt = QImage.Format.Format_RGB888
            if img.shape[4] == 4:
                bytes_per_line = 4*width
                fmt = QImage.Format.Format_RGBA8888
            else: 
                bytes_per_line = width
                fmt = QImage.Format.Format_Grayscale8
            qimage = QImage(img.data, width, height, bytes_per_line, fmt)
            self.parent.image_item.setPixmap(QPixmap.fromImage(qimage))