import sys
import os
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QPushButton, QLabel, QFileDialog, QSplitter, 
                             QScrollArea, QMessageBox, QFrame, QAbstractItemView, QGraphicsView, 
                             QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsLineItem,
                             QGraphicsPathItem, QDialog, QMenu, QSizePolicy, QListWidgetItem, QLineEdit)
from PyQt6.QtCore import Qt, QRectF, QSettings, QSize
from PyQt6.QtGui import (QPixmap, QImage, QDragEnterEvent, QDropEvent, QColor, QPen, QBrush, 
                         QPainter, QPainterPath, QIcon, QAction)
from PIL import Image

# --- 作者與角色資訊 ---
APP_VERSION = "v1 Azrael Edition (Patch 5.6)"
AUTHOR_NAME = "Aries Abriel Debrusc"
AUTHOR_EMAIL = "irosdp@gmail.com"
COPYRIGHT_YEAR = "2025"
CHAR_NAME = "Azrael"

# --- 設定常數 ---
TARGET_WIDTH = 800
MAX_SLICE_HEIGHT = 1600 
MAX_IMAGES = 12
THUMB_WIDTH = 120 

# --- 資源路徑輔助 ---
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --- 輔助函式：取得不重複的檔名 ---
def get_unique_filename(directory, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    full_path = os.path.join(directory, new_filename)
    
    while os.path.exists(full_path):
        new_filename = f"{base}_{counter}{ext}"
        full_path = os.path.join(directory, new_filename)
        counter += 1
        
    return full_path

class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.mainWindow = None 

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            files = []
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                    files.append(path)
            if self.mainWindow:
                self.mainWindow.add_images_to_list(files)
        else:
            super().dropEvent(event)
            if self.mainWindow:
                self.mainWindow.refresh_preview()

    # [New] 支援 Delete 鍵刪除項目
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            if self.mainWindow:
                self.mainWindow.remove_images()
        else:
            super().keyPressEvent(event)

class MultiColMiniMap(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None 
        self.selections = [] 
        self.column_gap = 10
        self.col_w = THUMB_WIDTH
        self.setMinimumWidth(self.col_w + 20)

    def update_data(self, pil_image, selection_rects):
        if pil_image:
            w, h = pil_image.size
            if w > 0:
                scale = self.col_w / w
                new_h = int(h * scale)
                thumb = pil_image.resize((self.col_w, new_h), Image.Resampling.BILINEAR)
                if thumb.mode != "RGBA":
                    thumb = thumb.convert("RGBA")
                data = thumb.tobytes("raw", "RGBA")
                qimg = QImage(data, self.col_w, new_h, QImage.Format.Format_RGBA8888)
                self.image = QPixmap.fromImage(qimg)
            else:
                self.image = None
        else:
            self.image = None
            
        self.selections = selection_rects
        self.update() 
        self.adjust_size_request()

    def get_ideal_width(self):
        if not self.image: return 150
        view_h = self.parent().height() if self.parent() else 800
        if view_h < 100: view_h = 800
        img_h = self.image.height()
        cols_needed = math.ceil(img_h / view_h)
        req_w = (cols_needed * (self.col_w + self.column_gap)) + 20
        return req_w

    def adjust_size_request(self):
        req_w = self.get_ideal_width()
        self.setMinimumWidth(req_w)
        self.resize(req_w, self.height())

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.image: return 

        view_h = self.parent().height() if self.parent() else self.height()
        if view_h <= 0: view_h = 100
        img_h = self.image.height()
        cols_needed = math.ceil(img_h / view_h)
        scale_ratio = self.col_w / TARGET_WIDTH

        painter.setBrush(QBrush(QColor(233, 30, 99, 100))) 
        painter.setPen(Qt.PenStyle.NoPen)

        for col in range(cols_needed):
            src_y_start = col * view_h
            src_y_end = min((col + 1) * view_h, img_h)
            slice_h = src_y_end - src_y_start
            if slice_h <= 0: break
            
            dst_x = 10 + col * (self.col_w + self.column_gap)
            dst_y = 0 
            
            painter.drawPixmap(dst_x, dst_y, self.image, 0, src_y_start, self.col_w, slice_h)

            if self.selections:
                for (orig_y1, orig_y2) in self.selections:
                    thumb_y1 = orig_y1 * scale_ratio
                    thumb_y2 = orig_y2 * scale_ratio
                    intersect_y1 = max(thumb_y1, src_y_start)
                    intersect_y2 = min(thumb_y2, src_y_end)
                    if intersect_y2 > intersect_y1:
                        rect_y = intersect_y1 - src_y_start
                        rect_h = intersect_y2 - intersect_y1
                        painter.drawRect(int(dst_x), int(rect_y), int(self.col_w), int(rect_h))

class CropCanvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(QColor("#222")))
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        self.bg_char_pixmap = None
        char_path = resource_path("Azrael_Full.png")
        if os.path.exists(char_path):
            self.bg_char_pixmap = QPixmap(char_path)
        
        self.pixmap_item = None
        self.dark_overlay = None 
        self.selection_items = []
        self.split_lines = []
        self.selections = [] 
        
        self.current_action = None 
        self.active_rect_index = -1
        self.drag_start_y = 0
        self.drag_start_pos_global = None 
        self.drag_offset_top = 0 
        self.drag_offset_bottom = 0
        
        self.border_color = QColor("#F06292") 
        self.split_line_color = QColor("#FFEB3B")

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        if self.bg_char_pixmap and not self.bg_char_pixmap.isNull():
            painter.save()
            painter.resetTransform()
            view_w = self.viewport().width()
            view_h = self.viewport().height()
            target_h = int(view_h * 0.7) 
            scaled_pix = self.bg_char_pixmap.scaledToHeight(target_h, Qt.TransformationMode.SmoothTransformation)
            if scaled_pix.width() > view_w * 0.6:
                scaled_pix = self.bg_char_pixmap.scaledToWidth(int(view_w * 0.6), Qt.TransformationMode.SmoothTransformation)
            x = view_w - scaled_pix.width() - 20
            y = view_h - scaled_pix.height() - 20
            painter.setOpacity(0.5)
            painter.drawPixmap(x, y, scaled_pix)
            painter.restore()

    def load_image(self, pil_image):
        self.scene.clear()
        self.pixmap_item = None
        self.dark_overlay = None
        self.selection_items = []
        self.split_lines = []
        self.selections = []
        
        self.image_width, self.image_height = pil_image.size
        if pil_image.mode != "RGBA":
            pil_image = pil_image.convert("RGBA")
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(data, self.image_width, self.image_height, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimage)
        
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.pixmap_item.setZValue(0) 
        self.scene.addItem(self.pixmap_item)
        self.reset_to_full_selection() 

    def reset_to_full_selection(self):
        if not self.pixmap_item: return
        self.selections = [QRectF(0, 0, self.image_width, self.image_height)]
        self.refresh_overlays()

    def refresh_overlays(self):
        if not self.pixmap_item: return

        if self.dark_overlay: 
            self.scene.removeItem(self.dark_overlay)
            self.dark_overlay = None
        for item in self.selection_items:
            self.scene.removeItem(item)
        self.selection_items = []
        for line in self.split_lines:
            self.scene.removeItem(line)
        self.split_lines = []

        full_rect = QRectF(0, 0, self.image_width, self.image_height)
        mask_path = QPainterPath()
        mask_path.addRect(full_rect)
        selection_path = QPainterPath()
        for sel in self.selections:
            selection_path.addRect(sel)
        final_mask = mask_path.subtracted(selection_path)
        
        self.dark_overlay = QGraphicsPathItem(final_mask)
        self.dark_overlay.setBrush(QBrush(QColor(0, 0, 0, 180)))
        self.dark_overlay.setPen(QPen(Qt.PenStyle.NoPen))
        self.dark_overlay.setZValue(1)
        self.scene.addItem(self.dark_overlay)

        border_pen = QPen(self.border_color)
        border_pen.setWidth(3)
        border_pen.setStyle(Qt.PenStyle.DashLine)
        split_pen = QPen(self.split_line_color)
        split_pen.setWidth(2)
        split_pen.setStyle(Qt.PenStyle.DotLine)

        total_pixels = 0
        self.selections.sort(key=lambda r: r.top())
        accumulated_h = 0
        
        for sel in self.selections:
            rect_item = QGraphicsRectItem(sel)
            rect_item.setPen(border_pen)
            rect_item.setZValue(2)
            self.scene.addItem(rect_item)
            self.selection_items.append(rect_item)
            
            chunk_h = sel.height()
            current_chunk_y = 0
            while current_chunk_y < chunk_h:
                space_left = MAX_SLICE_HEIGHT - (accumulated_h % MAX_SLICE_HEIGHT)
                if space_left < chunk_h - current_chunk_y:
                    cut_y = current_chunk_y + space_left
                    abs_y = sel.top() + cut_y
                    line = QGraphicsLineItem(0, abs_y, self.image_width, abs_y)
                    line.setPen(split_pen)
                    line.setZValue(2)
                    self.scene.addItem(line)
                    self.split_lines.append(line)
                    accumulated_h += space_left
                    current_chunk_y += space_left
                else:
                    accumulated_h += (chunk_h - current_chunk_y)
                    current_chunk_y = chunk_h
            total_pixels += chunk_h
        self.window().update_stats(total_pixels, self.selections)

    def mousePressEvent(self, event):
        if not self.pixmap_item: return

        pos = self.mapToScene(event.pos())
        y = pos.y()
        y = max(0, min(y, self.image_height))
        margin = 20 
        
        self.active_rect_index = -1
        self.current_action = None
        self.drag_start_pos_global = event.globalPosition() 
        
        if event.button() == Qt.MouseButton.RightButton:
            for i, rect in enumerate(self.selections):
                if rect.contains(pos):
                    del self.selections[i]
                    self.refresh_overlays()
                    return
        
        for i, rect in enumerate(self.selections):
            if abs(y - rect.top()) < margin:
                self.current_action = 'RESIZE_TOP'
                self.active_rect_index = i
                return
            elif abs(y - rect.bottom()) < margin:
                self.current_action = 'RESIZE_BOTTOM'
                self.active_rect_index = i
                return
            elif rect.contains(pos):
                self.current_action = 'MOVE_OR_SPLIT'
                self.active_rect_index = i
                self.drag_start_y = y
                self.drag_offset_top = rect.top()
                self.drag_offset_bottom = rect.bottom()
                return

        if self.current_action is None:
            self.current_action = 'CREATE'
            self.drag_start_y = y
            new_rect = QRectF(0, y, self.image_width, 0)
            self.selections.append(new_rect)
            self.active_rect_index = len(self.selections) - 1

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.pixmap_item: return

        pos = self.mapToScene(event.pos())
        y = pos.y()
        y = max(0, min(y, self.image_height))
        
        margin = 20

        cursor_set = False
        for rect in self.selections:
            if abs(y - rect.top()) < margin or abs(y - rect.bottom()) < margin:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
                cursor_set = True
                break
            elif rect.contains(pos):
                self.setCursor(Qt.CursorShape.SizeAllCursor) 
                cursor_set = True
                break
        if not cursor_set:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        if self.current_action and self.active_rect_index != -1:
            rect = self.selections[self.active_rect_index]
            
            if self.current_action == 'MOVE_OR_SPLIT':
                dist = (event.globalPosition() - self.drag_start_pos_global).manhattanLength()
                if dist > 5:
                    self.current_action = 'MOVE'
            
            if self.current_action == 'RESIZE_TOP':
                new_top = min(y, rect.bottom() - 10)
                new_top = max(0, new_top)
                self.selections[self.active_rect_index].setTop(new_top)
            elif self.current_action == 'RESIZE_BOTTOM':
                new_bottom = max(y, rect.top() + 10)
                new_bottom = min(self.image_height, new_bottom)
                self.selections[self.active_rect_index].setBottom(new_bottom)
            elif self.current_action == 'CREATE':
                top = min(self.drag_start_y, y)
                bottom = max(self.drag_start_y, y)
                self.selections[self.active_rect_index].setTop(top)
                self.selections[self.active_rect_index].setBottom(bottom)
            elif self.current_action == 'MOVE':
                dy = y - self.drag_start_y
                current_h = self.drag_offset_bottom - self.drag_offset_top
                new_top = self.drag_offset_top + dy
                new_bottom = new_top + current_h
                if new_top < 0:
                    new_top = 0
                    new_bottom = current_h
                if new_bottom > self.image_height:
                    new_bottom = self.image_height
                    new_top = new_bottom - current_h
                self.selections[self.active_rect_index].setTop(new_top)
                self.selections[self.active_rect_index].setBottom(new_bottom)

            self.refresh_overlays()
            
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if not self.pixmap_item: return

        if self.current_action == 'MOVE_OR_SPLIT':
            pos = self.mapToScene(event.pos())
            y = pos.y()
            rect = self.selections[self.active_rect_index]
            if rect.top() + 10 < y < rect.bottom() - 10:
                top_part = QRectF(0, rect.top(), self.image_width, y - rect.top())
                bottom_part = QRectF(0, y, self.image_width, rect.bottom() - y)
                del self.selections[self.active_rect_index]
                self.selections.append(top_part)
                self.selections.append(bottom_part)
                self.merge_overlaps()
                self.refresh_overlays()
                self.current_action = None
                self.active_rect_index = -1
                super().mouseReleaseEvent(event)
                return

        self.selections = [s for s in self.selections if s.height() > 5]
        self.current_action = None
        self.active_rect_index = -1
        self.merge_overlaps()
        self.refresh_overlays()
        super().mouseReleaseEvent(event)

    def merge_overlaps(self):
        if not self.selections: return
        self.selections.sort(key=lambda r: r.top())
        merged = []
        if not self.selections: return
        curr = self.selections[0]
        for i in range(1, len(self.selections)):
            next_rect = self.selections[i]
            if next_rect.top() < curr.bottom():
                new_bottom = max(curr.bottom(), next_rect.bottom())
                curr.setBottom(new_bottom)
            else:
                merged.append(curr)
                curr = next_rect
        merged.append(curr)
        self.selections = merged

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"關於 {CHAR_NAME}")
        self.resize(450, 600)
        self.setStyleSheet("background-color: #263238; color: #fce4ec;")
        layout = QVBoxLayout(self)
        
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        char_img_path = resource_path("Azrael_Full.png")
        if os.path.exists(char_img_path):
            pix = QPixmap(char_img_path)
            pix = pix.scaled(390, 390, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.img_label.setPixmap(pix)
        else:
            self.img_label.setText("(Azrael_Full.png 未找到)")
            self.img_label.setStyleSheet("color: #ec407a; border: 2px dashed #ec407a; padding: 20px;")
            
        layout.addWidget(self.img_label)
        
        info_html = f"""
        <h2 style='color: #f48fb1;'>{APP_VERSION}</h2>
        <p><b>Author:</b> {AUTHOR_NAME}</p>
        <p><b>Email:</b> {AUTHOR_EMAIL}</p>
        <p style='font-size: 10px; color: #b0bec5;'>© {COPYRIGHT_YEAR} {AUTHOR_NAME}. All rights reserved.</p>
        """
        lbl_text = QLabel(info_html)
        lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_text.setOpenExternalLinks(True)
        layout.addWidget(lbl_text)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        btn_close.setStyleSheet("""
            QPushButton { background-color: #880e4f; color: white; border: none; padding: 8px; font-weight: bold; border-radius: 4px;}
            QPushButton:hover { background-color: #c2185b; }
        """)
        layout.addWidget(btn_close)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("AzraelSoft", "ShopeeTool")
        self.setWindowTitle(f"蝦皮上架神器 - {APP_VERSION}")
        self.resize(1400, 900)
        self.setAcceptDrops(True)
        
        icon_path = resource_path("Azrael_Head.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.image_paths = [] 
        self.stitched_image = None
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget) 
        main_layout.setContentsMargins(0,0,0,0)

        # --- 0. 頂部工具列 ---
        toolbar_container = QFrame()
        toolbar_container.setObjectName("Toolbar")
        toolbar_container.setMinimumHeight(50)
        toolbar_layout = QHBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        
        btn_open = QPushButton("📂 開啟圖片")
        btn_open.clicked.connect(self.open_file_dialog)
        btn_open.setStyleSheet("font-weight: bold; padding: 6px 15px;")
        toolbar_layout.addWidget(btn_open)
        
        toolbar_layout.addStretch() 
        
        btn_theme = QPushButton("🎨 風格設定")
        menu_theme = QMenu(self)
        menu_theme.addAction("Azrael Deep (深粉/暗黑)", lambda: self.apply_theme("AzraelDeep"))
        menu_theme.addAction("Azrael Pale (淡粉/夢幻)", lambda: self.apply_theme("AzraelPale"))
        btn_theme.setMenu(menu_theme)
        toolbar_layout.addWidget(btn_theme)
        
        btn_about = QPushButton("ℹ️ 關於")
        btn_about.clicked.connect(self.show_about)
        toolbar_layout.addWidget(btn_about)
        
        main_layout.addWidget(toolbar_container, 0)

        # --- 下方主要工作區 (Splitter) ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_center_widget = QWidget()
        lc_layout = QHBoxLayout(left_center_widget)
        lc_layout.setContentsMargins(0, 0, 0, 0)
        lc_layout.setSpacing(0)
        
        left_panel = QFrame()
        left_panel.setFixedWidth(260)
        left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        lbl_hint = QLabel("1. 圖片列表")
        lbl_hint.setStyleSheet("font-weight: bold; font-size: 14px;")
        left_layout.addWidget(lbl_hint)
        
        self.file_list = DraggableListWidget()
        self.file_list.mainWindow = self
        left_layout.addWidget(self.file_list)
        
        # [New] 排序按鈕區
        sort_layout = QHBoxLayout()
        btn_sort_name = QPushButton("依名稱排序")
        btn_sort_name.clicked.connect(self.sort_images_by_name)
        btn_sort_date = QPushButton("依日期排序")
        btn_sort_date.clicked.connect(self.sort_images_by_date)
        sort_layout.addWidget(btn_sort_name)
        sort_layout.addWidget(btn_sort_date)
        left_layout.addLayout(sort_layout)

        # 功能按鈕區
        btn_layout = QHBoxLayout()
        btn_reset_selection = QPushButton("重製選取區")
        btn_reset_selection.clicked.connect(self.reset_canvas_selection)
        btn_clear = QPushButton("清空圖庫")
        btn_clear.clicked.connect(self.clear_all)
        btn_layout.addWidget(btn_reset_selection)
        btn_layout.addWidget(btn_clear)
        left_layout.addLayout(btn_layout)
        
        # 檔名設定區
        setting_group = QFrame()
        setting_layout = QVBoxLayout(setting_group)
        setting_layout.setContentsMargins(0,10,0,5)
        
        lbl_prefix_desc = QLabel("描述圖前綴 (Shpoee_XXX):")
        saved_desc = self.settings.value("prefix_desc", "Shopee")
        self.txt_prefix_desc = QLineEdit(str(saved_desc))
        
        lbl_prefix_main = QLabel("主圖前綴 (Main_XXX):")
        saved_main = self.settings.value("prefix_main", "Main")
        self.txt_prefix_main = QLineEdit(str(saved_main))
        
        setting_layout.addWidget(lbl_prefix_desc)
        setting_layout.addWidget(self.txt_prefix_desc)
        setting_layout.addWidget(lbl_prefix_main)
        setting_layout.addWidget(self.txt_prefix_main)
        left_layout.addWidget(setting_group)

        self.status_box = QFrame()
        self.status_box.setObjectName("StatusBox") 
        sb_layout = QVBoxLayout(self.status_box)
        self.lbl_stats = QLabel("準備就緒")
        self.lbl_stats.setWordWrap(True)
        sb_layout.addWidget(self.lbl_stats)
        self.lbl_warning = QLabel("")
        self.lbl_warning.setObjectName("WarningLabel")
        sb_layout.addWidget(self.lbl_warning)
        left_layout.addWidget(self.status_box)

        self.btn_export = QPushButton("2. 輸出描述圖 (裁切)")
        self.btn_export.setObjectName("ExportBtn")
        self.btn_export.clicked.connect(self.export_images)
        left_layout.addWidget(self.btn_export)

        self.btn_export_raw = QPushButton("3. 輸出選取區 (不裁切)")
        self.btn_export_raw.setObjectName("ExportBtnRaw")
        self.btn_export_raw.clicked.connect(self.export_selections_raw)
        left_layout.addWidget(self.btn_export_raw)
        
        lc_layout.addWidget(left_panel)

        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        
        info_bar = QFrame()
        info_bar.setObjectName("InfoBar")
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(10, 5, 10, 5)
        lbl_preview = QLabel("左鍵點擊=分割 | 拖曳=移動/新增 | 右鍵=刪除")
        info_layout.addWidget(lbl_preview)
        center_layout.addWidget(info_bar)
        
        self.canvas = CropCanvas(self)
        center_layout.addWidget(self.canvas)
        lc_layout.addWidget(center_panel)
        
        self.splitter.addWidget(left_center_widget)

        right_container = QWidget()
        right_container.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.map_scroll = QScrollArea()
        self.map_scroll.setWidgetResizable(True)
        self.map_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.map_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.minimap = MultiColMiniMap()
        self.map_scroll.setWidget(self.minimap)
        right_layout.addWidget(self.map_scroll)
        
        self.splitter.addWidget(right_container)
        self.splitter.setStretchFactor(0, 8)
        self.splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(self.splitter, 1)

        self.apply_theme("AzraelDeep")

    def open_file_dialog(self):
        last_dir = self.settings.value("last_open_dir", os.path.expanduser("~"))
        files, _ = QFileDialog.getOpenFileNames(self, "選擇圖片", last_dir, "Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        if files:
            self.settings.setValue("last_open_dir", os.path.dirname(files[0]))
            self.add_images_to_list(files)

    def add_images_to_list(self, files):
        for f in files:
            found = False
            for i in range(self.file_list.count()):
                if self.file_list.item(i).data(Qt.ItemDataRole.UserRole) == f:
                    found = True
                    break
            if not found:
                item = QListWidgetItem(os.path.basename(f))
                item.setData(Qt.ItemDataRole.UserRole, f)
                self.file_list.addItem(item)
        self.refresh_preview()

    def remove_images(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items: return
        for item in selected_items:
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
        self.refresh_preview()

    # [New] 依名稱排序
    def sort_images_by_name(self):
        if self.file_list.count() == 0: return
        
        items_data = []
        for i in range(self.file_list.count()):
            path = self.file_list.item(i).data(Qt.ItemDataRole.UserRole)
            items_data.append(path)
            
        # 依檔名排序 (不分大小寫)
        items_data.sort(key=lambda x: os.path.basename(x).lower())
        
        self.file_list.clear()
        for path in items_data:
            item = QListWidgetItem(os.path.basename(path))
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.file_list.addItem(item)
            
        self.refresh_preview()

    # [New] 依日期排序
    def sort_images_by_date(self):
        if self.file_list.count() == 0: return
        
        items_data = []
        for i in range(self.file_list.count()):
            path = self.file_list.item(i).data(Qt.ItemDataRole.UserRole)
            if os.path.exists(path):
                items_data.append((path, os.path.getmtime(path)))
            
        # 依日期排序 (舊到新)
        items_data.sort(key=lambda x: x[1])
        
        self.file_list.clear()
        for path, _ in items_data:
            item = QListWidgetItem(os.path.basename(path))
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.file_list.addItem(item)
            
        self.refresh_preview()

    def reset_canvas_selection(self):
        if self.stitched_image:
            self.canvas.reset_to_full_selection()

    def clear_all(self):
        self.file_list.clear()
        self.canvas.scene.clear()
        self.minimap.update_data(None, [])
        self.lbl_stats.setText("列表已清空")

    def refresh_preview(self):
        if self.file_list.count() == 0: 
            return

        try:
            processed_imgs = []
            for i in range(self.file_list.count()):
                path = self.file_list.item(i).data(Qt.ItemDataRole.UserRole)
                if not path or not os.path.exists(path): continue
                
                img = Image.open(path)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                w, h = img.size
                scale = TARGET_WIDTH / w
                new_h = int(h * scale)
                img = img.resize((TARGET_WIDTH, new_h), Image.Resampling.LANCZOS)
                processed_imgs.append(img)
            
            if not processed_imgs: return

            total_h = sum(img.height for img in processed_imgs)
            self.stitched_image = Image.new("RGB", (TARGET_WIDTH, total_h), (255, 255, 255))
            y_offset = 0
            for img in processed_imgs:
                self.stitched_image.paste(img, (0, y_offset))
                y_offset += img.height
            
            self.canvas.load_image(self.stitched_image)
            
            ideal_width = self.minimap.get_ideal_width()
            total_w = self.width()
            target_right_w = ideal_width
            if target_right_w > total_w * 0.4:
                 target_right_w = int(total_w * 0.4)
            self.splitter.setSizes([total_w - target_right_w, target_right_w])
            
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"處理失敗: {str(e)}")

    def update_stats(self, total_height, selections_coords):
        sel_tuples = [(r.top(), r.bottom()) for r in selections_coords]
        self.minimap.update_data(self.stitched_image, sel_tuples)
        
        num_images = math.ceil(total_height / MAX_SLICE_HEIGHT)
        info = f"原始總高度: {self.stitched_image.height} px\n保留總高度: {int(total_height)} px\n預計輸出: {num_images} 張"
        self.lbl_stats.setText(info)
        
        if num_images > MAX_IMAGES:
            max_allowed_h = MAX_IMAGES * MAX_SLICE_HEIGHT
            excess_pixels = int(total_height) - max_allowed_h
            self.lbl_warning.setText(f"⚠️ 超過 {MAX_IMAGES} 張！\n需刪減高度: 約 {excess_pixels} px")
            self.btn_export.setEnabled(False)
        else:
            self.lbl_warning.setText(f"✅ 符合限制")
            self.btn_export.setEnabled(True)

    def resizeEvent(self, event):
        self.minimap.adjust_size_request()
        super().resizeEvent(event)

    def export_images(self):
        if not self.stitched_image: return
        self.settings.setValue("prefix_desc", self.txt_prefix_desc.text())
        
        last_export_dir = self.settings.value("last_export_dir", os.path.expanduser("~"))
        output_dir = QFileDialog.getExistingDirectory(self, "選擇輸出資料夾", last_export_dir)
        if not output_dir: return
        
        self.settings.setValue("last_export_dir", output_dir)
        
        selections = sorted(self.canvas.selections, key=lambda r: r.top())
        if not selections:
            QMessageBox.warning(self, "提示", "沒有選取任何範圍！")
            return
            
        chunks = []
        for rect in selections:
            y1, y2 = int(rect.top()), int(rect.bottom())
            if y2 > y1:
                chunk = self.stitched_image.crop((0, y1, TARGET_WIDTH, y2))
                chunks.append(chunk)
        
        if not chunks: return
        final_h = sum(c.height for c in chunks)
        final_long_img = Image.new("RGB", (TARGET_WIDTH, final_h))
        curr_y = 0
        for c in chunks:
            final_long_img.paste(c, (0, curr_y))
            curr_y += c.height
            
        idx = 1
        curr_y = 0
        prefix = self.txt_prefix_desc.text().strip() or "Shopee"
        
        try:
            while curr_y < final_h:
                cut_h = min(MAX_SLICE_HEIGHT, final_h - curr_y)
                piece = final_long_img.crop((0, curr_y, TARGET_WIDTH, curr_y + cut_h))
                
                filename = f"{prefix}_{idx:02d}.jpg"
                save_path = get_unique_filename(output_dir, filename)
                
                piece.save(save_path, "JPEG", quality=95)
                curr_y += cut_h
                idx += 1
            QMessageBox.information(self, "完成", f"成功輸出 {idx-1} 張圖片！")
        except Exception as e:
            QMessageBox.critical(self, "存檔錯誤", str(e))

    def export_selections_raw(self):
        if not self.stitched_image: return
        self.settings.setValue("prefix_main", self.txt_prefix_main.text())
        
        last_export_dir = self.settings.value("last_export_dir", os.path.expanduser("~"))
        output_dir = QFileDialog.getExistingDirectory(self, "選擇輸出資料夾 (主圖模式)", last_export_dir)
        if not output_dir: return
        
        self.settings.setValue("last_export_dir", output_dir)
        
        selections = sorted(self.canvas.selections, key=lambda r: r.top())
        if not selections:
            QMessageBox.warning(self, "提示", "沒有選取任何範圍！")
            return

        prefix = self.txt_prefix_main.text().strip() or "Main"
        idx = 1
        try:
            for rect in selections:
                y1, y2 = int(rect.top()), int(rect.bottom())
                if y2 > y1:
                    chunk = self.stitched_image.crop((0, y1, TARGET_WIDTH, y2))
                    
                    filename = f"{prefix}_{idx:02d}.jpg"
                    save_path = get_unique_filename(output_dir, filename)
                    
                    chunk.save(save_path, "JPEG", quality=95)
                    idx += 1
                    
            QMessageBox.information(self, "完成", f"成功輸出 {idx-1} 張主圖區塊！")
        except Exception as e:
            QMessageBox.critical(self, "存檔錯誤", str(e))

    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def apply_theme(self, theme_name):
        common_font = "font-family: 'Segoe UI', 'Microsoft JhengHei', sans-serif;"
        
        if theme_name == "AzraelDeep":
            bg_dark = "#1a1a1a"
            bg_panel = "#263238"
            accent_dark = "#880e4f" 
            accent_light = "#c2185b" 
            highlight = "#f06292" 
            text_main = "#fce4ec" 
            
            qss = f"""
                QMainWindow {{ background-color: {bg_dark}; color: {text_main}; {common_font} }}
                QWidget {{ color: {text_main}; {common_font} }}
                QFrame#Toolbar, QFrame#LeftPanel, QWidget#RightPanel {{ background-color: {bg_panel}; border: none; }}
                QFrame#InfoBar {{ background-color: {accent_dark}; color: white; }}
                
                QPushButton {{ background-color: {accent_dark}; color: white; border: none; padding: 6px; border-radius: 4px; }}
                QPushButton:hover {{ background-color: {accent_light}; }}
                
                QListWidget {{ background-color: #37474f; border: 1px solid #455a64; color: #eceff1; }}
                QListWidget::item:selected {{ background-color: {accent_light}; color: white; }}
                
                QSplitter::handle {{ background-color: #455a64; }}
                
                QFrame#StatusBox {{ background-color: #37474f; border: 1px solid {accent_light}; border-radius: 5px; }}
                QLabel#WarningLabel {{ color: #ff80ab; font-weight: bold; }}
                
                QLineEdit {{ background-color: #37474f; border: 1px solid #455a64; color: #eceff1; padding: 3px; }}
                
                QPushButton#ExportBtn {{ background-color: {accent_light}; font-size: 14px; font-weight: bold; padding: 8px; }}
                QPushButton#ExportBtn:hover {{ background-color: {highlight}; }}
                QPushButton#ExportBtn:disabled {{ background-color: #546e7a; color: #90a4ae; }}

                QPushButton#ExportBtnRaw {{ background-color: #00897b; color: white; font-size: 14px; font-weight: bold; padding: 8px; }}
                QPushButton#ExportBtnRaw:hover {{ background-color: #26a69a; }}

                QMenu {{ background-color: {bg_panel}; border: 1px solid #455a64; color: {text_main}; }}
                QMenu::item {{ padding: 5px 20px; }}
                QMenu::item:selected {{ background-color: {accent_light}; color: white; }}
                
                QMessageBox {{ background-color: {bg_panel}; color: {text_main}; }}
                QMessageBox QLabel {{ color: {text_main}; }}
            """
            self.canvas.setBackgroundBrush(QBrush(QColor("#101010")))
            self.minimap.setStyleSheet(f"background-color: {bg_dark};")
            self.canvas.border_color = QColor(highlight)
            self.canvas.split_line_color = QColor("#ffeb3b")
            
        elif theme_name == "AzraelPale":
            bg_light = "#fce4ec" 
            bg_panel = "#f8bbd0" 
            accent = "#ec407a" 
            accent_hover = "#d81b60" 
            text_main = "#4a148c" 
            
            qss = f"""
                QMainWindow {{ background-color: {bg_light}; color: {text_main}; {common_font} }}
                QWidget {{ color: {text_main}; {common_font} }}
                QFrame#Toolbar, QFrame#LeftPanel, QWidget#RightPanel {{ background-color: white; border: 1px solid #f48fb1; }}
                QFrame#InfoBar {{ background-color: {bg_panel}; color: {text_main}; }}
                
                QPushButton {{ background-color: {bg_panel}; color: {text_main}; border: 1px solid {accent}; padding: 6px; border-radius: 4px; }}
                QPushButton:hover {{ background-color: {accent}; color: white; }}
                
                QListWidget {{ background-color: white; border: 1px solid {accent}; color: {text_main}; }}
                QListWidget::item:selected {{ background-color: {accent}; color: white; }}
                
                QSplitter::handle {{ background-color: {accent}; }}
                
                QFrame#StatusBox {{ background-color: #fff; border: 1px solid {accent}; border-radius: 5px; }}
                QLabel#WarningLabel {{ color: #c2185b; font-weight: bold; }}
                
                QLineEdit {{ background-color: #fff; border: 1px solid {accent}; color: {text_main}; padding: 3px; }}

                QPushButton#ExportBtn {{ background-color: {accent}; color: white; font-size: 14px; font-weight: bold; padding: 8px; }}
                QPushButton#ExportBtn:hover {{ background-color: {accent_hover}; }}
                QPushButton#ExportBtn:disabled {{ background-color: #e0e0e0; color: #9e9e9e; border: none; }}

                QPushButton#ExportBtnRaw {{ background-color: #26a69a; color: white; font-size: 14px; font-weight: bold; padding: 8px; border: none; }}
                QPushButton#ExportBtnRaw:hover {{ background-color: #00897b; }}

                QMenu {{ background-color: white; border: 1px solid {accent}; color: {text_main}; }}
                QMenu::item {{ padding: 5px 20px; }}
                QMenu::item:selected {{ background-color: {bg_panel}; color: {accent_hover}; }}
                
                QMessageBox {{ background-color: #fff; color: {text_main}; }}
                QMessageBox QLabel {{ color: {text_main}; }}
            """
            self.canvas.setBackgroundBrush(QBrush(QColor("#fff0f5")))
            self.minimap.setStyleSheet(f"background-color: {bg_light};")
            self.canvas.border_color = QColor(accent)
            self.canvas.split_line_color = QColor("#880e4f")

        self.setStyleSheet(qss)
        self.canvas.refresh_overlays() 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())