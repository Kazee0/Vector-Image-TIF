from PyQt6.QtWidgets import QListWidget, QDockWidget, QWidget, QVBoxLayout, QToolBar, QLabel, QGraphicsView, QGraphicsRectItem, QFileDialog, QMessageBox
from PyQt6.QtGui import QIcon, QFont, QAction,QPen,QColor, QBrush
from PyQt6.QtCore import Qt, QSize
import matplotlib.patches as patches


class TagHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tags = {}  # {id: {'rect': patch, 'coords': (x,y,w,h), 'label': str}}
        self.tag_layer= None
        self.tag_list = None
        self.tag_dock = None
        self.drawing = False
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

        # Connect our handlers
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
            self.current_rect = QGraphicsRectItem()
            self.current_rect.setPen(QPen(QColor(255, 0, 0,), 2))
            self.current_rect.setBrush(QBrush(QColor(255, 0, 0, 50)))
            self.current_rect.setPos(self.start_pos)
            self.main_window.scene.addItem(self.current_rect)
            
        else:
            QGraphicsView.mousePressEvent(self.main_window.graphics_view, event)
    
    def mouse_move_event(self, event):
        if self.drawing and self.current_rect is not None:
            end_pos = self.main_window.graphics_view.mapToScene(event.pos()) 
            width = end_pos.x() - self.start_pos.x()
            height = end_pos.y() - self.start_pos.y()
            
            size = min(abs(width), abs(height))
            width = size if width >= 0 else -size
            height = size if height >= 0 else -size
            
            self.current_rect.setRect(0,0,width, height)
        else:
            QGraphicsView.mouseMoveEvent(self.main_window.graphics_view, event)
    
    def mouse_release_event(self, event):
        if self.drawing and self.current_rect and event.button()== Qt.MouseButton.LeftButton:
            end_pos = self.main_window.graphics_view.mapToScene(event.pos())
            width = end_pos.x() - self.start_pos.x()
            height = end_pos.y() - self.start_pos.y()
            
            size = min(abs(width), abs(height))
            width = size if width >= 0 else -size
            height = size if height >= 0 else -size
            
            self.current_rect.setRect(0,0,width, height)
            
            tag_id = len(self.tags) + 1
            self.tags[tag_id] = {
                'rect': self.current_rect,
                'coords': (self.start_pos.x(), self.start_pos.y(), width, height),
                'label': f"Tag-{tag_id}"
            }
            
            self.tag_list.addItem(f"Tag-{tag_id}")
            
            self.start_pos = None
            self.current_rect = None
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
                    x,y,w,h = tag_data['cords']
                    id = tag_data['label']
                    
                    rect_item = QGraphicsRectItem(0, 0, w, h)
                    rect_item.setPos(x,y)
                    rect_item.setPen(QPen(QColor(255,0,0), 2))
                    rect_item.setBrush(QBrush(QColor(255,0,0,50)))
                    self.main_window.scene.addItem(rect_item)
                    
                    self.tags[int(tag_id)] = {
                        'rect':rect_item,
                        'cords':(x,y,w,h),
                        'label':id
                    }
                    self.tag_list.addItem(label)
                
                self.main_window.statusBar.showMessage(f"Loaded {len(data)} tags from {file_path}", 3000)
            
            except Exception as e:
                QMessageBox.critical(self.main_window, "Error", f"Failed to load tags:{str(e)}")
    
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
                    data[tag_info] ={
                        'cords': tag_info['cords'],
                        'label':tag_info['label']
                    }
                
                with open(file_pth, "w") as f:
                    import json
                    json.dump(data, f, indent=2)
                    self.main_window.statusBar.showMessage(f"Saved {len(data)} tags to {file_pth}", 3000)
            except Exception as e:
                QMessageBox.critical(self.main_window, "Error", f"Failed to save tags: {str(e)}")
                
    def delete_selected_tag(self):
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
            self.main_window.graphics_view.setCursor(Qt.CursorShape.CrossCursor)
            self.main_window.statusBar.showMessage("Drawing mode enabled. Click to draw a tag", 2000)
        else:
            self.main_window.graphics_view.setCursor(Qt.CursorShape.ArrowCursor)
            self.main_window.statusBar.showMessage("Drawing mode disabled", 2000)
            self.drawing = False
            if self.current_rect:
                self.main_window.scene.removeItem(self.current_rect)
                self.current_rect = None
            self.start_pos = None
            
            
    def start_drawing(self):
        if self.tag_layer is None:
            self.main_window.vector_list.addItem("Tag Layer")
            self.tag_layer= True
        self.drawing=True
        self.main_window.statusBar.showMessage("Click to draw a tag", 2000)
    
    def handle_tag_selection(self):
        selected_items = self.tag_list.selectedItems()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        tag_text = selected_item.text()
        
        for tag_id, tag_info in self.tags.items():
            if tag_info['label'] == tag_text:
                tag_info['rect'].setPen(QPen(QColor(0, 255, 0), 2))
                
                self.main_window.graphics_view.centerOn(tag_info['rect'])
                
            else:
                tag_info['rect'].setPen(QPen(QColor(255, 0, 0), 2))
        