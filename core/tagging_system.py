from PyQt6.QtWidgets import QListWidget, QDockWidget, QWidget, QVBoxLayout, QToolBar, QLabel, QGraphicsView, QGraphicsRectItem, QFileDialog, QMessageBox
from PyQt6.QtGui import QIcon, QFont, QAction,QPen,QColor
from PyQt6.QtCore import Qt, QSizeF, QRectF, QPoint, QPointF,QSize


class ResizeRect(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        
        self.normal_pen = QPen(QColor(255, 0, 0), 2)
        self.selected_pen = QPen(QColor(0, 255, 0), 3)  
        self.setPen(self.normal_pen)
        
        self.resize_handles = {
            'top_left': QRectF(0, 0, 10, 10),
            'top_right': QRectF(0, 0, 10, 10),
            'bottom_left': QRectF(0, 0, 10, 10),
            'bottom_right': QRectF(0, 0, 10, 10)
        }
        self.active_resize_handle = None
        self.original_rect = QRectF()
        self.original_pos = QPointF()
        self.original_mouse_pos = QPointF()
        self.is_moving = False
        
        self.cursor_shapes = {
            'top_left': Qt.CursorShape.SizeFDiagCursor,
            'top_right': Qt.CursorShape.SizeBDiagCursor,
            'bottom_left': Qt.CursorShape.SizeBDiagCursor,
            'bottom_right': Qt.CursorShape.SizeFDiagCursor
        }
    
    def update_resize_handles(self):
        """Update handle positions relative to the current rectangle"""
        rect = self.rect()
        handle_size = 10
        half_handle = handle_size / 2
        
        # Calculate handle positions in local coordinates
        self.resize_handles['top_left'] = QRectF(
            rect.left() - half_handle, 
            rect.top() - half_handle, 
            handle_size, 
            handle_size
        )
        self.resize_handles['top_right'] = QRectF(
            rect.right() - half_handle, 
            rect.top() - half_handle, 
            handle_size, 
            handle_size
        )
        self.resize_handles['bottom_left'] = QRectF(
            rect.left() - half_handle, 
            rect.bottom() - half_handle, 
            handle_size, 
            handle_size
        )
        self.resize_handles['bottom_right'] = QRectF(
            rect.right() - half_handle, 
            rect.bottom() - half_handle, 
            handle_size, 
            handle_size
        )
    
    def hoverMoveEvent(self, event):
        if not self.isSelected():
            self.setCursor(Qt.CursorShape.ArrowCursor)
            super().hoverMoveEvent(event)
            return
            
        pos = event.pos()
        for handle_name, handle_rect in self.resize_handles.items():
            if handle_rect.contains(pos):
                self.setCursor(self.cursor_shapes[handle_name])
                event.accept()
                return
        
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        super().hoverMoveEvent(event)
    
    def paint(self, painter, option, widget):
        if self.isSelected():
            self.setPen(self.selected_pen)
        else:
            self.setPen(self.normal_pen)    
        super().paint(painter, option, widget)

        if self.isSelected():
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.setBrush(QColor(255, 255, 0))

            self.update_resize_handles()

            for handle in self.resize_handles.values():
                painter.drawRect(handle)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.isSelected():
                self.setSelected(True)
            
            pos = event.pos()

            for handle_name, handle_rect in self.resize_handles.items():
                if handle_rect.contains(pos):
                    self.active_resize_handle = handle_name
                    self.original_rect = self.rect()
                    self.original_pos = self.pos()
                    self.original_mouse_pos = self.mapToScene(event.pos())
                    event.accept()
                    return
            
            self.is_moving = True
            self.original_pos = self.pos()
            self.original_mouse_pos = self.mapToScene(event.pos())
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.active_resize_handle:
            current_mouse_pos = self.mapToScene(event.pos())
            delta = current_mouse_pos - self.original_mouse_pos
            
            new_rect = QRectF(self.original_rect)
            new_pos = QPointF(self.original_pos)
            
            if self.active_resize_handle == 'top_left':
                width = self.original_rect.width()-delta.x()
                height = self.original_rect.height()- delta.y()
                
                if width > 0 and height > 0:
                    new_rect.setWidth(width)
                    new_rect.setHeight(height)
                    new_pos = self.original_pos + delta
                    self.setRect(new_rect)
                    self.setPos(new_pos)
            
            elif self.active_resize_handle == 'top_right':
                new_height = self.original_rect.height() - delta.y()
                if new_height > 0:
                    new_rect.setHeight(new_height)
                    new_rect.setWidth(self.original_rect.width() + delta.x())
                    self.setRect(new_rect)
                    self.setPos(self.original_pos.x(), self.original_pos.y() + delta.y())
            
            elif self.active_resize_handle == 'bottom_left':
                new_width = self.original_rect.width() - delta.x()
                if new_width > 0:
                    new_rect.setWidth(new_width)
                    new_rect.setHeight(self.original_rect.height() + delta.y())
                    self.setRect(new_rect)
                    self.setPos(self.original_pos.x() + delta.x(), self.original_pos.y())
            
            elif self.active_resize_handle == 'bottom_right':
                new_rect.setWidth(self.original_rect.width() + delta.x())
                new_rect.setHeight(self.original_rect.height() + delta.y())
                self.setRect(new_rect)
            
            event.accept()
        
        elif self.is_moving:
            current_mouse_pos = self.mapToScene(event.pos())
            delta = current_mouse_pos - self.original_mouse_pos
            self.setPos(self.original_pos + delta)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.active_resize_handle = None
            self.is_moving = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def focusInEvent(self, event):
        self.setSelected(True)
        super().focusInEvent(event)
    
    def focusOutEvent(self, event):
        self.setSelected(False)
        super().focusOutEvent(event)           
class TagHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tags = {}  # {id: {'rect': patch, 'coords': (x,y,w,h), 'label': str}}
        self.tag_layer= None
        self.tag_list = None
        self.tag_dock = None
        self.drawing = False
        self.is_dirty = False
        self.current_rect = None
        self.start_pos = None
        self.tag_scene = None
        
        self.init_tag_layer()
        
    def init_tag_layer(self):
        self.create_tag_dock()
        self.conntect_events()
        
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
        add_tag_action.setShortcut('T')
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
        
        dock_layout.addWidget(QLabel("Tags:"))
        dock_layout.addWidget(toolbar)
        dock_layout.addWidget(self.tag_list)
        
        self.tag_dock.setWidget(dock_widget)
        self.main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.tag_dock)
    
    def conntect_events(self):
        self.original_mouse_press = self.main_window.graphics_view.mousePressEvent
        self.original_mouse_move = self.main_window.graphics_view.mouseMoveEvent 
        self.original_mouse_release = self.main_window.graphics_view.mouseReleaseEvent
        self.original_key_press = self.main_window.keyPressEvent

        self.main_window.graphics_view.mousePressEvent = self.mouse_press_event
        self.main_window.graphics_view.mouseMoveEvent = self.mouse_move_event
        self.main_window.graphics_view.mouseReleaseEvent = self.mouse_release_event
        self.main_window.keyPressEvent = self.key_press_event
    
    def key_press_event(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.drawing:
                self.drawing = False
                if self.current_rect:
                    self.main_window.scene.removeItem(self.current_rect)
                    self.current_rect = None
                self.start_pos = None
                self.main_window.statusBar.showMessage("Tag drawing cancelled", 2000)
        else:
            self.original_key_press(event)
            
    def mouse_press_event(self, event):
        if self.drawing and event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = self.main_window.graphics_view.mapToScene(event.pos())
            self.current_rect = ResizeRect()
            self.current_rect.setPen(QPen(QColor(255, 0, 0,), 2))
            self.current_rect.setPos(self.start_pos)
            self.main_window.scene.addItem(self.current_rect)
            
        else:
            QGraphicsView.mousePressEvent(self.main_window.graphics_view, event)
    
    def mouse_move_event(self, event):
        if self.drawing and self.current_rect is not None:
            end_pos = self.main_window.graphics_view.mapToScene(event.pos()) 
            width = end_pos.x() - self.start_pos.x()
            height = end_pos.y() - self.start_pos.y()
            
            self.current_rect.setRect(0,0,width, height)
        else:
            QGraphicsView.mouseMoveEvent(self.main_window.graphics_view, event)
    
    def mouse_release_event(self, event):
        if self.drawing and self.current_rect and event.button()== Qt.MouseButton.LeftButton:
            end_pos = self.main_window.graphics_view.mapToScene(event.pos())
            width = end_pos.x() - self.start_pos.x()
            height = end_pos.y() - self.start_pos.y()
            
            self.current_rect.setRect(0,0,width, height)
            
            tag_id = len(self.tags) + 1
            self.tags[tag_id] = {
                'rect': self.current_rect,
                'coords': (self.start_pos.x(), self.start_pos.y(), width, height),
                'label': f"Tag-{tag_id}"
            }
            
            self.tag_list.addItem(f"Tag-{tag_id}")
            
            self.is_dirty = True
            self.start_pos = None
            self.current_rect = None
            self.drawing = False
            self.main_window.graphics_view.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        else:
            QGraphicsView.mouseReleaseEvent(self.main_window.graphics_view, event)
    
    def load_tags(self):
        options = QFileDialog.Option.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Load Tags",
            "",
            "JSON Files(*.json);;All Files (*)",
            options=options
        )
        if file_path:
            try:
                with open(file_path, "r") as f:
                    import json
                    data = json.load(f)
                
                self.clear_tags()
                
                for tag_id, tag_data in data.items():
                    x,y,w,h = tag_data['coords']
                    id = tag_data['label']
                    
                    rect_item = QGraphicsRectItem(0, 0, w, h)
                    rect_item.setPos(x,y)
                    rect_item.setPen(QPen(QColor(255,0,0), 2))
                    self.main_window.scene.addItem(rect_item)
                    
                    self.tags[int(tag_id)] = {
                        'rect':rect_item,
                        'coords':(x,y,w,h),
                        'label':id
                    }
                    self.tag_list.addItem(label)
                
                self.main_window.statusBar.showMessage(f"Loaded {len(data)} tags from {file_path}", 3000)
                self.is_dirty = False
            except Exception as e:
                QMessageBox.critical(self.main_window, "Error", f"Failed to load tags:{str(e)}")
    
    def check_if_dirty(self):
        return self.is_dirty
    
    def save_tags(self):
        if not self.tags:
            QMessageBox.warning(self.main_window, "Warning", "No tags to save")
            return
        options = QFileDialog.Option.ReadOnly
        file_pth, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save Tags",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options
        )
        if file_pth:
            try:
                if not file_pth.lower().endswith('.json'):
                    file_pth+='.json'
                    
                data = {}
                for tag_id, tag_info in self.tags.items():
                    data[str(tag_info)] ={
                        'coords': tag_info['coords'],
                        'label':tag_info['label']
                    }

                with open(file_pth, "w") as f:
                    import json
                    json.dump(data, f, indent=2)
                    self.main_window.statusBar.showMessage(f"Saved {len(data)} tags to {file_pth}", 3000)
                self.is_dirty = False
            except Exception as e:
                QMessageBox.critical(self.main_window, "Error", f"Failed to save tags: {str(e)}")
                
    def delete_selected_tag(self):
        self.is_dirty = True
        selected_items = self.tag_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self.main_window, "Warning", "No tag selected to delete")
            return
        
        selected_item = selected_items[0]
        tag_text = selected_item.text()
        
        tag_to_remove = None
        for tag_id, tag_info in self.tags.items():
            if tag_info['label'] == tag_text:
                tag_to_remove = tag_id
                break
        
        if tag_to_remove is not None:
            self.main_window.scene.removeItem(self.tags[tag_to_remove]['rect'])
            del self.tags[tag_to_remove]
            self.tag_list.takeItem(self.tag_list.row(selected_item))
            self.main_window.statusBar.showMessage(f"Deleted tag: {tag_text}", 2000)

    def clear_tags(self):
        for tag_id, tag_info in self.tags.items():
            self.main_window.scene.removeItem(tag_info['rect'])
        self.tags.clear()
        self.tag_list.clear()
        self.main_window.statusBar.showMessage("All tags cleared", 2000)
    
    def set_tag_action(self, action):
        self.tag_aciton = action

    def set_drawing_mode(self, mode):
        if self.tag_aciton:
            self.tag_aciton.setChecked(mode)
            if mode:
                self.tag_aciton.setIcon(QIcon.fromTheme("edit-select-rectangle"))
            else:
                self.tag_aciton.setIcon(QIcon.fromTheme("edit-select-rectangle-outline"))
            
        if mode:
            self.main_window.statusBar.showMessage("Drawing mode enabled. Click to draw a tag", 2000)
        else:
            self.main_window.graphics_view.viewport().setCursor(Qt.CursorShape.ArrowCursor)
            self.main_window.statusBar.showMessage("Drawing mode disabled", 2000)
            self.drawing = False
            if self.current_rect:
                self.main_window.scene.removeItem(self.current_rect)
                self.current_rect = None
            self.start_pos = None

    def set_tags_visible(self, visible):
        for tag_id, tag_info in self.tags.items():
            tag_info['rect'].setVisible(visible)
        if visible:
            self.main_window.statusBar.showMessage("Tags are now visible", 2000)
        else:
            self.main_window.statusBar.showMessage("Tags are now hidden", 2000)

    def start_drawing(self):
        self.main_window.graphics_view.viewport().setCursor(Qt.CursorShape.CrossCursor)
        if self.tag_layer is None:
            self.main_window.vector_list.addItem("Tag Layer")
            self.tag_layer= True
        self.drawing=True
        self.main_window.statusBar.showMessage("Click to draw a tag", 2000)
    
    def handle_tag_selection(self):
        selected_items = self.tag_list.selectedItems()
        if not selected_items:
            # Deselect all tags when nothing is selected
            for tag_id, tag_info in self.tags.items():
                tag_info['rect'].setSelected(False)
            return
            
        selected_item = selected_items[0]
        tag_text = selected_item.text()
        
        for tag_id, tag_info in self.tags.items():
            if tag_info['label'] == tag_text:
                tag_info['rect'].setSelected(True)
                self.main_window.graphics_view.centerOn(tag_info['rect'])
            else:
                tag_info['rect'].setSelected(False)
    
    def clear_tag_layer(self):
        if self.tag_layer:
            for tag_id, tag_info in self.tags.items():
                self.main_window.scene.removeItem(tag_info['rect'])
            self.tags.clear()
            self.tag_list.clear()
            self.tag_layer = None
            self.main_window.statusBar.showMessage("Tag layer cleared", 2000)
        else:
            QMessageBox.warning(self.main_window, "Warning", "No tag layer to clear")

    