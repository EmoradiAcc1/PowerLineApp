from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt, QPoint, QTimer, QPropertyAnimation
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGraphicsOpacityEffect
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QTableWidget, QVBoxLayout, QWidget, QLineEdit, QLabel, QHeaderView, QHBoxLayout, QTableWidgetItem, QCheckBox, QScrollArea
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import pyqtSignal
import logging

# --- هدر سفارشی برای جلوگیری از بولد شدن ---
class NoBoldHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        font = QFont("Vazir", 13)
        font.setWeight(QFont.Normal)
        self.setFont(font)
        # استایل نرم برای هدر جدول
        self.setStyleSheet("""
            QHeaderView::section {
                background-color: #f5f7fa;
                color: #222;
                border: none;
                border-bottom: 1.5px solid #e0e0e0;
                padding: 6px 4px;
                font-weight: normal;
            }
        """)
    def paintSection(self, painter, rect, logicalIndex):
        font = self.font()
        font.setWeight(QFont.Normal)
        painter.save()
        painter.setFont(font)
        super().paintSection(painter, rect, logicalIndex)
        painter.restore()
    def mousePressEvent(self, event):
        logical_index = self.logicalIndexAt(event.pos())
        if event.button() == Qt.LeftButton and logical_index >= 0:
            self.sectionClicked.emit(logical_index)
        super().mousePressEvent(event)

if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomPaper(QDialog):
    """
    دیالوگ سفارشی با گوشه‌های کاملاً پخ و بدون لایه مربعی زیرین
    """
    def __init__(self, parent=None, background_color="#FFFFFF", corner_radius=8, width=500, height=140):
        super().__init__(parent)
        self.background_color = background_color
        self.corner_radius = corner_radius
        self.width = width
        self._custom_height = height

        self.setFixedSize(self.width, self._custom_height)
        self.setWindowTitle("CustomPaper")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("QDialog { background: transparent; border: none; }")

        # لایه اصلی بدون margin
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # فریم اصلی با پخ و رنگ پس‌زمینه
        self.frame = QFrame(self)
        self.frame.setObjectName("mainFrame")
        self.frame.setStyleSheet(f"""
            QFrame#mainFrame {{
                box-shadow: 0px 8px 32px #88888855;
                background: {self.background_color};
                border-radius: {self.corner_radius}px;
                border: 2px solid #E0E0E0;
            }}
        """)
        self.frame.setFixedSize(self.width, self._custom_height)
        layout.addWidget(self.frame)

        # اگر خواستی محتوا اضافه کنی، به self.frame یک layout بده و محتوا را داخل آن بگذار

    def set_background_color(self, color):
        self.background_color = color
        self.frame.setStyleSheet(f"""
            QFrame#mainFrame {{
                background: {self.background_color};
                border-radius: {self.corner_radius}px;
                border: 2px solid #E0E0E0;
            }}
        """)

    def set_corner_radius(self, radius):
        self.corner_radius = radius
        self.frame.setStyleSheet(f"""
            QFrame#mainFrame {{
                background: {self.background_color};
                border-radius: {self.corner_radius}px;
                border: 2px solid #E0E0E0;
            }}
        """)

    def set_size(self, width, height):
        self.width = width
        self._custom_height = height
        self.setFixedSize(self.width, self._custom_height)
        self.frame.setFixedSize(self.width, self._custom_height)

    def get_background_color(self):
        return self.background_color

    def get_corner_radius(self):
        return self.corner_radius

    def get_size(self):
        return (self.width, self._custom_height)

    def mousePressEvent(self, event):
        # اگر روی بیرون فریم کلیک شد، دیالوگ بسته شود
        if not self.frame.geometry().contains(event.pos()):
            self.reject()
        else:
            super().mousePressEvent(event)

class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event):
        # Ignore wheel events to prevent accidental value changes
        event.ignore()

class CustomDialog_Flexible(CustomPaper):
    def __init__(self, header_text="عنوان دیالوگ", main_text="متن اصلی دیالوگ", ok_text="تایید", cancel_text=None, question_text="", parent=None, icon=None, dialog_height=300):
        # محاسبه ارتفاع مناسب بر اساس متن
        calculated_height = self._calculate_optimal_height(main_text, question_text)
        
        super().__init__(parent, background_color="#FFFFFF", corner_radius=15, width=300, height=calculated_height)
        
        # تنظیم عنوان دیالوگ
        self.setWindowTitle(header_text)
        
        # ایجاد layout اصلی
        main_layout = QVBoxLayout(self.frame)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(8)
        
        # هدر
        header_layout = QHBoxLayout()
        if icon is not None:
            icon_label = QLabel()
            icon_label.setFixedSize(32, 32)
            icon_label.setScaledContents(True)
            icon_label.setStyleSheet("background: transparent;")
            icon_label.setPixmap(icon.pixmap(32, 32))
            header_layout.addWidget(icon_label, alignment=Qt.AlignLeft)
        else:
            header_layout.addSpacing(4)
            
        header_label = QLabel(header_text)
        header_label.setFont(QFont("Vazir", 12))
        header_label.setStyleSheet("color: black; background: transparent;")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFixedHeight(38)
        header_layout.addWidget(header_label, stretch=1)
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 18px;
                color: #888;
            }
            QPushButton:hover {
                background: #fbeaea;
                color: #d32f2f;
            }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn, alignment=Qt.AlignRight)
        main_layout.addLayout(header_layout)
        
        # خط جداکننده
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("color: #b0b0b0; background: #b0b0b0; height: 1px;")
        main_layout.addWidget(divider)
        
        # متن اصلی (اسکرول‌دار در صورت نیاز)
        main_label = QLabel(main_text)
        main_label.setFont(QFont("Vazir", 11))
        main_label.setAlignment(Qt.AlignCenter)
        main_label.setStyleSheet("background: white; border-radius: 8px; padding: 8px;")  # اضافه کردن padding
        main_label.setWordWrap(True)
        main_label.adjustSize()
        
        # محاسبه ارتفاع مورد نیاز برای متن
        needed_height = main_label.sizeHint().height()
        max_text_height = 300  # حداکثر ارتفاع برای متن قبل از اسکرول
        
        from PyQt5.QtWidgets import QScrollArea
        if needed_height > max_text_height:
            # استفاده از اسکرول برای متن‌های طولانی
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setStyleSheet("""
                QScrollArea {
                    background: transparent; 
                    border: none;
                }
                QScrollBar:vertical {
                    background: #f0f0f0;
                    width: 8px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background: #c0c0c0;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #a0a0a0;
                }
            """)
            scroll.setWidget(main_label)
            scroll.setMaximumHeight(max_text_height)
            main_layout.addWidget(scroll)
        else:
            main_layout.addWidget(main_label)
        
        # سوال جداگانه اگر وجود داشت
        if question_text:
            question_label = QLabel(question_text)
            question_label.setFont(QFont("Vazir", 12))
            question_label.setAlignment(Qt.AlignCenter)
            question_label.setStyleSheet("background: transparent; margin-top: 8px;")
            main_layout.addWidget(question_label)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton(ok_text)
        ok_btn.setFixedWidth(80)
        ok_btn.setStyleSheet("""
            QPushButton {
                background: #017BCC;
                color: white;
                border-radius: 6px;
                padding: 6px 0;
                cursor: pointer;
            }
            QPushButton:hover {
                background: #0056a3;
            }
        """)
        ok_btn.setCursor(Qt.PointingHandCursor)
        
        if cancel_text:
            cancel_btn = QPushButton(cancel_text)
            cancel_btn.setFixedWidth(80)
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background: #f44336;
                    color: white;
                    border-radius: 6px;
                    padding: 6px 0;
                    cursor: pointer;
                }
                QPushButton:hover {
                    background: #d32f2f;
                }
            """)
            cancel_btn.setCursor(Qt.PointingHandCursor)
            btn_layout.addWidget(cancel_btn)
            btn_layout.addSpacing(16)
            btn_layout.addWidget(ok_btn)
            btn_layout.addStretch()
            cancel_btn.clicked.connect(self.reject)
        else:
            btn_layout.addWidget(ok_btn)
            btn_layout.addStretch()
            
        main_layout.addLayout(btn_layout)
        ok_btn.clicked.connect(self.accept)
        
        # تنظیم ارتفاع نهایی
        self._adjust_final_height()
        self._fade_anim = None
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(0)
        self._fade_in()

    def _calculate_optimal_height(self, main_text, question_text):
        """
        محاسبه ارتفاع بهینه بر اساس متن
        """
        # عرض مفید برای محاسبه (عرض دیالوگ - حاشیه‌ها)
        available_width = 300 - 32  # 300px عرض - 16px حاشیه از هر طرف
        
        # محاسبه ارتفاع متن اصلی
        font = QFont("Vazir", 11)
        font_metrics = QFontMetrics(font)
        
        # محاسبه تعداد خطوط متن اصلی
        text_lines = self._calculate_text_lines(main_text, available_width, font_metrics)
        main_text_height = text_lines * font_metrics.height()
        
        # محاسبه ارتفاع سوال (اگر وجود داشته باشد)
        question_height = 0
        if question_text:
            question_font = QFont("Vazir", 12)
            question_metrics = QFontMetrics(question_font)
            question_lines = self._calculate_text_lines(question_text, available_width, question_metrics)
            question_height = question_lines * question_metrics.height()
        
        # محاسبه ارتفاع کل
        # هدر: 38px + حاشیه‌ها: 32px + خط جداکننده: 1px + فاصله‌ها: 24px + دکمه‌ها: 40px
        base_height = 38 + 32 + 1 + 24 + 40
        
        # ارتفاع متن
        text_height = main_text_height + question_height
        
        # اضافه کردن padding برای متن
        text_height += 16  # 8px padding از بالا و پایین
        
        # محاسبه ارتفاع کل
        total_height = base_height + text_height
        
        # محدودیت‌های ارتفاع
        min_height = 200  # حداقل ارتفاع برای یک خط
        max_height = 500  # حداکثر ارتفاع قبل از اسکرول
        
        if total_height < min_height:
            return min_height
        elif total_height > max_height:
            return max_height
        else:
            return total_height

    def _calculate_text_lines(self, text, available_width, font_metrics):
        """
        محاسبه تعداد خطوط مورد نیاز برای نمایش متن
        """
        if not text:
            return 0
            
        words = text.split()
        if not words:
            return 1
            
        lines = 1
        current_line_width = 0
        
        for word in words:
            word_width = font_metrics.horizontalAdvance(word + " ")
            if current_line_width + word_width <= available_width:
                current_line_width += word_width
            else:
                lines += 1
                current_line_width = word_width
                
        return lines

    def _adjust_final_height(self):
        """
        تنظیم ارتفاع نهایی دیالوگ
        """
        # محاسبه ارتفاع واقعی محتوا
        content_height = self.frame.sizeHint().height()
        
        # محدودیت‌های ارتفاع
        min_height = 200
        max_height = 500
        
        if content_height < min_height:
            final_height = min_height
        elif content_height > max_height:
            final_height = max_height
        else:
            final_height = content_height
            
        # تنظیم ارتفاع نهایی
        self.setFixedHeight(final_height)
        self.frame.setFixedHeight(final_height)

    def _fade_in(self):
        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_anim.setDuration(250)
        self._fade_anim.setStartValue(0)
        self._fade_anim.setEndValue(1)
        self._fade_anim.start()

    def accept(self):
        self._fade_out_and_close(super().accept)
    def reject(self):
        self._fade_out_and_close(super().reject)
    def closeEvent(self, event):
        self._fade_out_and_close(lambda: super().closeEvent(event))

    def _fade_out_and_close(self, final_callback):
        if self._fade_anim and self._fade_anim.state() == QPropertyAnimation.Running:
            self._fade_anim.stop()
        anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        anim.setDuration(250)
        anim.setStartValue(1)
        anim.setEndValue(0)
        def on_finished():
            final_callback()
        anim.finished.connect(on_finished)
        anim.start()
        self._fade_anim = anim

class CustomDialog_Progress(CustomPaper):
    def __init__(self, header_text="در حال انجام عملیات...", cancel_text="لغو", parent=None):
        super().__init__(parent, background_color="#FFFFFF", corner_radius=15, width=340, height=220)
        
        # تنظیم عنوان دیالوگ
        self.setWindowTitle(header_text)
        
        # ایجاد layout اصلی
        main_layout = QVBoxLayout(self.frame)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(8)
        
        # هدر
        header_layout = QHBoxLayout()
        header_label = QLabel(header_text)
        header_label.setFont(QFont("Vazir", 12))
        header_label.setStyleSheet("color: black; background: transparent;")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFixedHeight(38)
        header_layout.addWidget(header_label, stretch=1)
        main_layout.addLayout(header_layout)
        
        # خط جداکننده
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("color: #b0b0b0; background: #b0b0b0; height: 1px;")
        main_layout.addWidget(divider)
        
        # نوار پیشرفت
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)  # نمایش متن روی نوار غیرفعال شود
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("QProgressBar { height: 50px; border-radius: 4px; font: bold 14px 'Vazir'; text-align: center; background: #eee; margin-top: 2px; margin-bottom: 2px; } QProgressBar::chunk { background: #017BCC; border-radius: 4px; }")
        main_layout.addStretch()
        main_layout.addWidget(self.progress_bar)
        
        # لیبل مقدار شمارش
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setFont(QFont("Vazir", 12))
        self.progress_label.setStyleSheet("background: transparent; padding: 2px 8px; border-radius: 6px;")
        main_layout.addWidget(self.progress_label)
        main_layout.addStretch()
        
        # دکمه لغو
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton(cancel_text)
        cancel_btn.setFixedWidth(100)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border-radius: 6px;
                padding: 6px 0;
                cursor: pointer;
            }
            QPushButton:hover {
                background: #d32f2f;
            }
        """)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        self.cancel_btn = cancel_btn
    
    def set_progress(self, value):
        self.progress_bar.setValue(value)
        if value >= self.progress_bar.maximum():
            self.accept()
    
    def set_maximum(self, maximum):
        self.progress_bar.setMaximum(maximum)
    
    def set_text(self, text):
        self.progress_label.setText(text)

class CustomTableWidget(QWidget):
    def __init__(self, table_name, headers, column_names, db, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.headers = headers
        self.column_names = column_names
        self.db = db
        self.column_filters = {}
        self._custom_edit_callback = None  # کال‌بک سفارشی ویرایش
        self._custom_clear_filters_callback = None  # کال‌بک سفارشی حذف فیلترها
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)  # کاهش margins
        self.layout.setSpacing(10)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Filter with Search Button - بهبود responsive بودن
        self.filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("جستجو در تمام ستون‌ها...")
        self.filter_input.setFont(QFont("Vazir", 12))
        self.filter_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: white;
                min-width: 100px;
                max-width: 300px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
        """)
        self.filter_input.setFixedWidth(300)  # تنظیم عرض ثابت
        # حذف setFixedWidth برای responsive بودن
        self.filter_input.returnPressed.connect(self.perform_search)
        # حذف تمام event handlers - textbox کاملاً طبیعی
        self.filter_layout.addWidget(QLabel("فیلتر:"))
        self.filter_layout.addWidget(self.filter_input)
        
        # دکمه جستجو
        self.search_button = QPushButton("جستجو")
        self.search_button.setFont(QFont("Vazir", 12))
        self.search_button.setCursor(Qt.PointingHandCursor)
        self.search_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #017BCC;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: normal;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0056a3;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
        """)
        self.search_button.clicked.connect(self.perform_search)
        self.filter_layout.addWidget(self.search_button)
        
        # دکمه حذف فیلتر
        self.clear_filter_button = QPushButton("حذف فیلتر")
        self.clear_filter_button.setFont(QFont("Vazir", 12))
        self.clear_filter_button.setCursor(Qt.PointingHandCursor)
        self.clear_filter_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: normal;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.clear_filter_button.clicked.connect(self.clear_all_filters)
        self.filter_layout.addWidget(self.clear_filter_button)
        
        self.filter_layout.addStretch()
        self.layout.addLayout(self.filter_layout)

        self.table = QTableWidget()
        # استفاده از هدر سفارشی برای جلوگیری از بولد شدن متن هدر
        self.table.setHorizontalHeader(NoBoldHeader(Qt.Horizontal, self.table))
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setFont(QFont("Vazir", 12))
        self.table.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #ccc; 
                background-color: white; 
            }
        """)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellClicked.connect(self.load_row_data)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.horizontalHeader().sectionClicked.connect(self.show_filter_popover)
        self.table.itemChanged.connect(self.save_cell_edit)
        
        # بهبود responsive بودن جدول
        self.table.setMinimumHeight(400)  # کاهش ارتفاع حداقل
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.table, 1)  # stretch factor = 1
        
        # اضافه کردن ویجت صفحه‌بندی
        self.pagination_widget = PaginationWidget()
        self.pagination_widget.pageChanged.connect(self.on_page_changed)
        self.layout.addWidget(self.pagination_widget)

    def set_database(self, db):
        """تنظیم دیتابیس برای استفاده"""
        self.db = db
        self.load_table()

    def load_table(self, global_filter=""):
        """بارگذاری جدول از دیتابیس با صفحه‌بندی"""
        if not self.db:
            return
            
        try:
            # ابتدا تعداد کل ردیف‌ها را محاسبه کن
            count_query = f"SELECT COUNT(*) FROM {self.table_name}"
            count_params = []
            count_conditions = []
            
            if global_filter:
                like_conditions = []
                for col in self.column_names:
                    like_conditions.append(f"{col} LIKE ?")
                count_conditions.append(f"({' OR '.join(like_conditions)})")
                count_params.extend([f"%{global_filter}%"] * len(self.column_names))
                
            for column, filter_text in self.column_filters.items():
                if filter_text:
                    if ',' in filter_text:
                        values = [v.strip() for v in filter_text.split(',') if v.strip()]
                        if values:
                            placeholders = ','.join(['?' for _ in values])
                            count_conditions.append(f"{column} IN ({placeholders})")
                            count_params.extend(values)
                    else:
                        count_conditions.append(f"{column} LIKE ?")
                        count_params.append(f"%{filter_text}%")
            
            if count_conditions:
                count_query += " WHERE " + " AND ".join(count_conditions)
            
            total_count = self.db.fetch_all(count_query, tuple(count_params))[0][0]
            self.pagination_widget.set_total_items(total_count)
            
            # ساخت کوئری اصلی با صفحه‌بندی
            select_columns = ", ".join(self.column_names)
            query = f"SELECT {select_columns}, id FROM {self.table_name}"
            
            params = []
            conditions = []
            if global_filter:
                like_conditions = []
                for col in self.column_names:
                    like_conditions.append(f"{col} LIKE ?")
                conditions.append(f"({' OR '.join(like_conditions)})")
                params.extend([f"%{global_filter}%"] * len(self.column_names))
                
            for column, filter_text in self.column_filters.items():
                if filter_text:
                    if ',' in filter_text:
                        values = [v.strip() for v in filter_text.split(',') if v.strip()]
                        if values:
                            placeholders = ','.join(['?' for _ in values])
                            conditions.append(f"{column} IN ({placeholders})")
                            params.extend(values)
                    else:
                        conditions.append(f"{column} LIKE ?")
                        params.append(f"%{filter_text}%")
                    
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            # اضافه کردن LIMIT و OFFSET برای صفحه‌بندی
            offset = self.pagination_widget.get_offset()
            limit = self.pagination_widget.get_limit()
            query += f" LIMIT {limit} OFFSET {offset}"
            
            rows = self.db.fetch_all(query, tuple(params))
            self.table.setRowCount(len(rows))
            self.table.blockSignals(True)
            for row_idx, row_data in enumerate(rows):
                for col_idx, data in enumerate(row_data[:-1]):  # آخرین ستون id است
                    data = str(data) if data is not None else ""
                    item = QTableWidgetItem(data)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    self.table.setItem(row_idx, col_idx, item)
                # ذخیره id در اولین سلول
                self.table.item(row_idx, 0).setData(Qt.UserRole, row_data[-1])
            self.table.blockSignals(False)
            self.table.resizeColumnsToContents()
            for col in range(self.table.columnCount()):
                if self.table.columnWidth(col) < 100:
                    self.table.setColumnWidth(col, 100)
            self.table.resizeRowsToContents()
            self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        except Exception as e:
            logging.error(f"Error in load_table: {str(e)}", exc_info=True)

    def perform_search(self):
        """انجام جستجو با کلیک روی دکمه"""
        try:
            search_text = self.filter_input.text().strip()
            # بازگشت به صفحه اول هنگام جستجو
            self.pagination_widget.set_current_page(1)
            self.load_table(search_text)
        except Exception as e:
            logging.error(f"Error in perform_search: {str(e)}", exc_info=True)
    
    def clear_all_filters(self):
        """حذف تمام فیلترها و نمایش همه محتوا"""
        try:
            # پاک کردن متن جستجو
            self.filter_input.clear()
            
            # پاک کردن فیلترهای ستون‌ها
            self.column_filters.clear()
            
            # بازگرداندن هدرها به حالت عادی (حذف آیکن فیلتر)
            header = self.table.horizontalHeader()
            for i in range(len(self.headers)):
                header_item = QTableWidgetItem(self.headers[i])
                self.table.setHorizontalHeaderItem(i, header_item)
            
            # فراخوانی کال‌بک سفارشی حذف فیلترها (اگر وجود داشته باشد)
            if self._custom_clear_filters_callback:
                self._custom_clear_filters_callback()
            
            # بازگشت به صفحه اول
            self.pagination_widget.set_current_page(1)
            
            # بارگذاری مجدد جدول بدون فیلتر
            self.load_table("")
            
            logging.debug("All filters cleared successfully")
        except Exception as e:
            logging.error(f"Error in clear_all_filters: {str(e)}", exc_info=True)
    
    def on_page_changed(self, page):
        """وقتی صفحه تغییر می‌کند"""
        try:
            search_text = self.filter_input.text().strip()
            self.load_table(search_text)
        except Exception as e:
            logging.error(f"Error in on_page_changed: {str(e)}", exc_info=True)

    def load_row_data(self, row, col):
        """برای سازگاری - خالی"""
        pass

    def show_context_menu(self, position):
        try:
            menu = CustomRightClick(self)
            from modules.custom_widgets import TableActions
            def safe_delete():
                try:
                    TableActions.delete_selected(
                        self.table, self.db, self, self.table_name, self.load_table
                    )
                except Exception as e:
                    logging.error(f"Exception in delete_selected: {str(e)}", exc_info=True)
                    from modules.custom_widgets import CustomDialog_Flexible
                    dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در حذف: {str(e)}", ok_text="باشه", parent=self)
                    dlg.exec_()
            def safe_edit():
                try:
                    if self._custom_edit_callback:
                        self._custom_edit_callback()
                        return
                    parent = self.parent()
                    last_parent = None
                    chain = []
                    while parent is not None:
                        last_parent = parent
                        chain.append(str(type(parent)))
                        parent = parent.parent() if hasattr(parent, 'parent') else None
                    if last_parent is not None and last_parent.__class__.__name__ == 'TeamsWindow':
                        last_parent.edit_team()
                        return
                    if last_parent is not None and last_parent.__class__.__name__ == 'LinesWindow':
                        last_parent.edit_line()
                        return
                    if last_parent is not None and last_parent.__class__.__name__ == 'TowersWindow':
                        last_parent.edit_tower()
                        return
                    TableActions.edit_selected(self.table, self.db, self, self.table_name, self.load_table)
                except Exception as e:
                    logging.error(f"Exception in edit_selected: {str(e)}", exc_info=True)
                    from modules.custom_widgets import CustomDialog_Flexible
                    dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در ویرایش: {str(e)}", ok_text="باشه", parent=self)
                    dlg.exec_()
            def safe_copy():
                try:
                    TableActions.copy_selected(self.table, self.db, self, self.table_name, self.load_table)
                except Exception as e:
                    logging.error(f"Exception in copy_selected: {str(e)}", exc_info=True)
                    from modules.custom_widgets import CustomDialog_Flexible
                    dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در کپی: {str(e)}", ok_text="باشه", parent=self)
                    dlg.exec_()
            menu.deleteRequested.connect(safe_delete)
            menu.editRequested.connect(safe_edit)
            if hasattr(menu, 'copyRequested'):
                menu.copyRequested.connect(safe_copy)
            global_pos = self.table.viewport().mapToGlobal(position)
            menu.show_at(global_pos, self)
        except Exception as e:
            logging.error(f"Exception in show_context_menu: {str(e)}", exc_info=True)
            from modules.custom_widgets import CustomDialog_Flexible
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در نمایش منوی راست‌کلیک: {str(e)}", ok_text="باشه", parent=self)
            dlg.exec_()

    def show_filter_popover(self, logical_index):
        """نمایش پاپ‌آپ فیلتر با CustomFilter و مقداردهی آیتم‌ها بر اساس داده‌های ستون"""
        try:
            from PyQt5.QtCore import QPoint
            from PyQt5.QtGui import QIcon
            if logical_index >= len(self.column_names):
                return
            column_name = self.column_names[logical_index]
            current_filter = self.column_filters.get(column_name, "")
            selected_values = set(current_filter.split(",")) if current_filter else set()
            # --- منطق جدید: مقدارهای یکتای ستون را فقط بر اساس سایر فیلترهای فعال واکشی کن ---
            conditions = []
            params = []
            for col, val in self.column_filters.items():
                if col == column_name or not val:
                    continue
                if ',' in val:
                    values = [v.strip() for v in val.split(',') if v.strip()]
                    placeholders = ','.join(['?' for _ in values])
                    conditions.append(f"{col} IN ({placeholders})")
                    params.extend(values)
                else:
                    conditions.append(f"{col} LIKE ?")
                    params.append(f"%{val}%")
            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
            query = f"SELECT DISTINCT {column_name} FROM {self.table_name} {where_clause} ORDER BY {column_name}"
            values = [row[0] for row in self.db.fetch_all(query, tuple(params))]
            # استفاده از CustomFilter به جای FilterPopover
            filter_dialog = CustomFilter(self.table)
            filter_dialog.setWindowModality(Qt.ApplicationModal)
            # --- تغییر placeholder جستجو بر اساس عنوان هدر ---
            header_title = self.headers[logical_index] if logical_index < len(self.headers) else "آیتم‌ها"
            filter_dialog.search_input.setPlaceholderText(f"جستجو در {header_title}")
            # آیتم‌های جدید را اضافه کن
            for val in values:
                cb = QCheckBox(str(val))
                cb.setFont(QFont("Vazir", 14))
                cb.setLayoutDirection(Qt.RightToLeft)
                cb.setStyleSheet("""
                    QCheckBox {
                        padding-right: 12px;
                        min-height: 36px;
                        font-size: 14px;
                    }
                    QCheckBox::indicator {
                        width: 15px;
                        height: 15px;
                        border-radius: 4px;
                        border: 2px solid #bbb;
                        background: #fff;
                    }
                    QCheckBox::indicator:checked {
                        width: 15px;
                        height: 15px;
                        background: #017BCC;
                        border: 2px solid #bbb;
                    }
                """)
                if str(val) in selected_values:
                    cb.setChecked(True)
                filter_dialog.checkbox_layout.addWidget(cb)
                filter_dialog.checkboxes.append(cb)
            # فقط یک بار Stretch اضافه کن
            filter_dialog.checkbox_layout.addStretch()
            # موقعیت دیالوگ
            header_rect = self.table.horizontalHeader().sectionViewportPosition(logical_index)
            header_width = self.table.horizontalHeader().sectionSize(logical_index)
            header_height = self.table.horizontalHeader().height()
            global_pos = self.table.mapToGlobal(
                QPoint(header_rect + header_width - filter_dialog.width, header_height)
            )
            x = global_pos.x()
            y = global_pos.y()
            if x < 0:
                # Align to the header section's global X
                header_global_x = self.table.mapToGlobal(QPoint(header_rect, 0)).x()
                x = header_global_x
            filter_dialog.move(x, y)
            filter_dialog.show()
            # مقداردهی اولیه جستجو (در صورت نیاز)
            filter_dialog.search_input.setText("")
            # اتصال دکمه تایید به ثبت فیلتر
            def on_accept():
                # مقدار فیلتر را از چک‌باکس‌های انتخاب‌شده بگیر
                selected = []
                for cb in filter_dialog.checkboxes:
                    if cb.isChecked():
                        selected.append(cb.text())
                # اگر همه آیتم‌ها تیک خورده‌اند و جستجو خالی است، فیلتر را حذف کن
                all_checked = all(cb.isChecked() for cb in filter_dialog.checkboxes)
                if all_checked and not filter_dialog.search_input.text().strip():
                    filter_text = ""
                else:
                    filter_text = ",".join(selected)
                self.on_column_filter_changed(logical_index, filter_text)
                filter_dialog.close()
            filter_dialog.btn1.clicked.connect(on_accept)
            # اتصال دکمه لغو به بستن دیالوگ
            filter_dialog.btn3.clicked.connect(filter_dialog.close)
        except Exception as e:
            import traceback
            logging.error(f"Error in show_filter_popover: {str(e)}\n{traceback.format_exc()}", exc_info=True)

    def on_column_filter_changed(self, column_index, filter_text):
        """وقتی فیلتر ستون تغییر می‌کند"""
        try:
            from PyQt5.QtGui import QIcon
            if column_index >= len(self.column_names):
                return
            column_name = self.column_names[column_index]
            header_item = self.table.horizontalHeaderItem(column_index)
            if filter_text:
                self.column_filters[column_name] = filter_text
                # آیکون فیلتر را ست کن
                icon = QIcon("Resources/Icons/Filter_Table.png")
                header_item.setIcon(icon)
            else:
                self.column_filters.pop(column_name, None)
                # آیکون را پاک کن
                header_item.setIcon(QIcon())
            # بازگشت به صفحه اول هنگام تغییر فیلتر
            self.pagination_widget.set_current_page(1)
            # بارگذاری مجدد جدول با فیلترهای جدید
            self.load_table(self.filter_input.text().strip())
        except Exception as e:
            logging.error(f"Error in on_column_filter_changed: {str(e)}", exc_info=True)

    def save_cell_edit(self, item):
        """ذخیره تغییرات سلول"""
        pass  # برای سازگاری
    
    def set_pagination_visible(self, visible):
        """تنظیم نمایش/عدم نمایش صفحه‌بندی"""
        self.pagination_widget.setVisible(visible)
    
    def get_pagination_widget(self):
        """دریافت ویجت صفحه‌بندی"""
        return self.pagination_widget

class CustomRightClick(CustomPaper):
    deleteRequested = pyqtSignal()
    editRequested = pyqtSignal()
    copyRequested = pyqtSignal() # Added this line
    _open_instance = None  # فقط یک نمونه باز
    def __init__(self, parent=None):
        super().__init__(parent, background_color="#FFFFFF", corner_radius=8, width=120, height=160)
        from PyQt5.QtWidgets import QVBoxLayout, QLabel
        from PyQt5.QtCore import Qt, QEvent
        item_style = """
            QLabel {
                font-size: 16px;
                color: #222;
                padding: 8px 5px;
                background: transparent;
                border: none;
                text-align: right;
                border-radius: 8px;
            }
            QLabel:hover {
                background: #F0F0F0;
                border-radius: 8px;
            }
        """
        items = [
            ("کپی", "Resources/Icons/RightClick_Copy.png"),
            ("حذف", "Resources/Icons/RightClick_Delete.png"),
            ("ویرایش", "Resources/Icons/RightClick_Edit.png"),
        ]
        layout = QVBoxLayout(self.frame)
        layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.setSpacing(0)
        for text, icon_path in items:
            item = QLabel()
            item.setTextFormat(Qt.RichText)
            item.setText(
                f"<table style='border:none;' dir='rtl' align='right'><tr>"
                f"<td style='border:none; padding-left:0; padding-right:12px; font-size:16px; text-align:right;'>{text}</td>"
                f"<td style='border:none; padding-left:0; padding-right:0;'><img src='{icon_path}' width='18' height='18'></td>"
                f"</tr></table>"
            )
            item.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setStyleSheet(item_style)
            item.setCursor(Qt.PointingHandCursor)
            def make_mouse_press(label, text=text):
                def handler(event):
                    if text == "حذف":
                        self.close()
                        self.deleteRequested.emit()
                    elif text == "ویرایش":
                        self.close()
                        self.editRequested.emit()
                    elif text == "کپی":
                        self.close()
                        self.copyRequested.emit()
                return handler
            item.mousePressEvent = make_mouse_press(item)
            layout.addWidget(item)
        self.setFixedSize(120, 160)
        self._event_filter_installed = False

    def show_at(self, pos, parent=None):
        # فقط یک نمونه باز باشد
        if CustomRightClick._open_instance is not None:
            CustomRightClick._open_instance.close()
        CustomRightClick._open_instance = self
        self.move(pos.x(), pos.y())
        self.show()
        # نصب eventFilter روی QApplication برای بستن با هر کلیک بیرون
        from PyQt5.QtWidgets import QApplication
        if not self._event_filter_installed:
            QApplication.instance().installEventFilter(self)
            self._event_filter_installed = True
        self._parent_for_filter = None  # دیگر نیازی به parent نیست

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
                return True
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        # حذف eventFilter از QApplication
        from PyQt5.QtWidgets import QApplication
        if self._event_filter_installed:
            QApplication.instance().removeEventFilter(self)
            self._event_filter_installed = False
        CustomRightClick._open_instance = None
        super().closeEvent(event)

class CustomFilter(CustomPaper):
    _open_instance = None
    def __init__(self, parent=None):
        super().__init__(parent, background_color="#FFFFFF", corner_radius=12, width=320, height=400)
        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, QScrollArea, QWidget, QPushButton
        from PyQt5.QtCore import Qt
        main_layout = QVBoxLayout(self.frame)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        # تکست‌باکس جستجو
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو در آیتم‌ها")
        self.search_input.setFont(QFont("Vazir", 12))
        self.search_input.setStyleSheet("padding: 8px 12px; border: 1px solid #ccc; border-radius: 8px; background: #fff;")
        self.search_input.textChanged.connect(self.filter_checkboxes)
        main_layout.addWidget(self.search_input)
        # چک‌لیست اسکرول‌دار
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                padding: 8px;
                border: 1px solid #ccc;
                background: #fff;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                background: #fff;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar:horizontal {
                background: #fff;
                height: 8px;
                border-radius: 4px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
                background: none;
                border: none;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
                border: none;
            }
        """)
        self.scroll_area.setLayoutDirection(Qt.RightToLeft)
        self.checkbox_widget = QWidget()
        self.checkbox_widget.setStyleSheet("background: #fff;")
        self.checkbox_layout = QVBoxLayout(self.checkbox_widget)
        self.checkbox_layout.setContentsMargins(0, 0, 0, 0)
        self.checkbox_layout.setSpacing(6)
        self.checkboxes = []
        # چک‌باکس انتخاب همه
        self.select_all_checkbox = QCheckBox("انتخاب همه")
        self.select_all_checkbox.setFont(QFont("Vazir", 14))
        self.select_all_checkbox.setLayoutDirection(Qt.RightToLeft)
        self.select_all_checkbox.setStyleSheet("""
            QCheckBox {
                padding-right: 12px;
                min-height: 36px;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
                border-radius: 4px;
                border: 2px solid #bbb;
                background: #fff;
            }
            QCheckBox::indicator:checked {
                width: 15px;
                height: 15px;
                background: #017BCC;
                border: 2px solid #bbb;
            }
        """)
        self.select_all_checkbox.stateChanged.connect(self.toggle_all_checkboxes)
        self.checkbox_layout.addWidget(self.select_all_checkbox)
        # حذف آیتم‌های تستی (آیتم 1، آیتم 2، ...)
        # فقط آیتم‌های واقعی از show_filter_popover اضافه می‌شوند
        # self.checkbox_layout.addStretch()  # حذف Stretch برای رفع فاصله اضافی
        self.scroll_area.setWidget(self.checkbox_widget)
        main_layout.addWidget(self.scroll_area, stretch=1)
        # دکمه‌ها در پایین
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)
        btn_layout.setAlignment(Qt.AlignRight)
        self.btn1 = QPushButton("تایید")
        self.btn3 = QPushButton("لغو")
        self.btn3.clicked.connect(self.close)
        # استایل دکمه تایید (آبی)
        self.btn1.setFont(QFont("Vazir", 12))
        self.btn1.setFixedHeight(38)
        self.btn1.setStyleSheet("""
            QPushButton {
                background: #017BCC;
                color: white;
                border-radius: 6px;
                padding: 0 24px;
                cursor: pointer;
            }
            QPushButton:hover {
                background: #0056a3;
            }
        """)
        self.btn1.setCursor(Qt.PointingHandCursor)
        # استایل دکمه لغو (قرمز)
        self.btn3.setFont(QFont("Vazir", 12))
        self.btn3.setFixedHeight(38)
        self.btn3.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border-radius: 6px;
                padding: 0 24px;
                cursor: pointer;
            }
            QPushButton:hover {
                background: #d32f2f;
            }
        """)
        self.btn3.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(self.btn3, stretch=1)
        btn_layout.addWidget(self.btn1, stretch=1)
        main_layout.addLayout(btn_layout)
        self.setFixedSize(320, 400)
        self._event_filter_installed = False

    def show_at(self, pos, parent=None):
        if CustomFilter._open_instance is not None:
            CustomFilter._open_instance.close()
        CustomFilter._open_instance = self
        self.move(pos.x(), pos.y())
        self.show()
        from PyQt5.QtWidgets import QApplication
        if not self._event_filter_installed:
            QApplication.instance().installEventFilter(self)
            self._event_filter_installed = True
        self._parent_for_filter = None

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
                return True
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        from PyQt5.QtWidgets import QApplication
        if self._event_filter_installed:
            QApplication.instance().removeEventFilter(self)
            self._event_filter_installed = False
        CustomFilter._open_instance = None
        super().closeEvent(event)

    def filter_checkboxes(self):
        text = self.search_input.text().strip()
        for cb in self.checkboxes:
            cb.setVisible(text in cb.text() if text else True)

    def toggle_all_checkboxes(self, state):
        checked = state == 2
        for cb in self.checkboxes:
            if cb.isVisible():
                cb.setChecked(checked)

class TableActions:
    @staticmethod
    def delete_selected(table_widget, db, parent, table_name, reload_callback):
        try:
            from PyQt5.QtCore import Qt
            from PyQt5.QtWidgets import QApplication
            selected_rows = sorted(set(index.row() for index in table_widget.selectedIndexes()))
            if not selected_rows:
                from modules.custom_widgets import CustomDialog_Flexible
                dlg = CustomDialog_Flexible(
                    header_text="هشدار",
                    main_text="لطفاً ابتدا یک ردیف را انتخاب کنید.",
                    ok_text="باشه",
                    parent=parent
                )
                dlg.exec_()
                return
            row_count = len(selected_rows)
            msg = f"آیا از حذف این {row_count} ردیف مطمئن هستید؟"
            from modules.custom_widgets import CustomDialog_Flexible
            dlg = CustomDialog_Flexible(
                header_text="تأیید حذف",
                main_text=msg,
                ok_text="بله",
                cancel_text="خیر",
                parent=parent
            )
            if dlg.exec_() != dlg.Accepted:
                return

            # نمایش progress dialog
            from modules.custom_widgets import CustomDialog_Progress
            progress = CustomDialog_Progress(header_text="در حال حذف ردیف‌ها...", cancel_text="لغو عملیات", parent=parent)
            progress.set_maximum(row_count)
            progress.set_progress(0)
            progress.set_text(f"0 از {row_count}")
            progress.show()
            QApplication.processEvents()
            
            deletion_cancelled = False
            def cancel():
                nonlocal deletion_cancelled
                deletion_cancelled = True
            progress.cancel_btn.clicked.connect(cancel)

            # جمع‌آوری شناسه‌های ردیف‌ها
            ids_to_delete = []
            for row in selected_rows:
                item = table_widget.item(row, 0)
                if item:
                    ids_to_delete.append(item.data(Qt.UserRole))

            # حذف ردیف‌ها با نمایش progress
            deleted_count = 0
            for i, id_ in enumerate(ids_to_delete):
                try:
                    QApplication.processEvents()
                    if deletion_cancelled:
                        break
                    progress.set_progress(i + 1)
                    progress.set_text(f"{i+1} از {row_count}")
                    db.execute_query(f"DELETE FROM {table_name} WHERE id=?", (id_,))
                    deleted_count += 1
                except Exception as e:
                    logging.error(f"Error deleting row with id {id_}: {str(e)}")
                    continue

            # بستن progress dialog
            try:
                progress.close()
            except:
                pass

            # بارگذاری مجدد جدول
            try:
                reload_callback()
            except Exception as e:
                logging.error(f"Error in reload_callback after deletion: {str(e)}")

            # نمایش نتیجه
            if deletion_cancelled:
                msg = f"عملیات لغو شد و {deleted_count} ردیف تا این لحظه حذف شد."
                table_widget.clearSelection()
                dlg = CustomDialog_Flexible(header_text="لغو عملیات", main_text=msg, ok_text="باشه", parent=parent)
                dlg.exec_()
            elif deleted_count > 0:
                table_widget.clearSelection()
                dlg = CustomDialog_Flexible(header_text="موفقیت", main_text=f"{deleted_count} ردیف با موفقیت حذف شد.", ok_text="باشه", parent=parent)
                dlg.exec_()

        except Exception as e:
            logging.error(f"Exception in TableActions.delete_selected: {str(e)}", exc_info=True)
            try:
                progress.close()
            except:
                pass
            from modules.custom_widgets import CustomDialog_Flexible
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در حذف: {str(e)}", ok_text="باشه", parent=parent)
            dlg.exec_()
    @staticmethod
    def edit_selected(table_widget, db, parent, table_name, reload_callback):
        try:
            from modules.custom_widgets import CustomDialog_Flexible
            selected_rows = sorted(set(index.row() for index in table_widget.selectedIndexes()))
            if len(selected_rows) != 1:
                dlg = CustomDialog_Flexible(
                    header_text="هشدار",
                    main_text="لطفاً فقط یک ردیف را برای ویرایش انتخاب کنید.",
                    ok_text="باشه",
                    parent=parent
                )
                dlg.exec_()
                return
            dlg = CustomDialog_Flexible(
                header_text="ویرایش",
                main_text="تابع ویرایش باید در هر بخش پیاده‌سازی شود.",
                ok_text="باشه",
                parent=parent
            )
            dlg.exec_()
        except Exception as e:
            logging.error(f"Exception in TableActions.edit_selected: {str(e)}", exc_info=True)
            from modules.custom_widgets import CustomDialog_Flexible
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در ویرایش: {str(e)}", ok_text="باشه", parent=parent)
            dlg.exec_()
    @staticmethod
    def copy_selected(table_widget, db, parent, table_name, reload_callback):
        try:
            from PyQt5.QtWidgets import QApplication
            from modules.custom_widgets import CustomDialog_Flexible
            selected_items = table_widget.selectedItems()
            if not selected_items:
                dlg = CustomDialog_Flexible(
                    header_text="کپی",
                    main_text="هیچ سلولی انتخاب نشده است.",
                    ok_text="باشه",
                    parent=parent
                )
                dlg.exec_()
                return
            rows = sorted(set(item.row() for item in selected_items))
            cols = sorted(set(item.column() for item in selected_items))
            text = ""
            for row in rows:
                row_data = []
                for col in cols:
                    item = table_widget.item(row, col)
                    row_data.append(item.text() if item else "")
                text += "\t".join(row_data) + "\n"
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            dlg = CustomDialog_Flexible(
                header_text="کپی",
                main_text="محتوای سلول‌های انتخاب‌شده کپی شد.",
                ok_text="باشه",
                parent=parent
            )
            dlg.exec_()
        except Exception as e:
            logging.error(f"Exception in TableActions.copy_selected: {str(e)}", exc_info=True)
            from modules.custom_widgets import CustomDialog_Flexible
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در کپی: {str(e)}", ok_text="باشه", parent=parent)
            dlg.exec_()

class PaginationWidget(QWidget):
    """ویجت صفحه‌بندی برای جداول"""
    
    pageChanged = pyqtSignal(int)  # سیگنال تغییر صفحه
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 1
        self.total_pages = 1
        self.items_per_page = 50
        self.total_items = 0
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(10)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # اطلاعات صفحه
        self.info_label = QLabel()
        self.info_label.setFont(QFont("Vazir", 11))
        self.info_label.setStyleSheet("color: #555;")
        self.layout.addWidget(self.info_label)
        
        self.layout.addStretch()
        
        # انتخاب تعداد آیتم در هر صفحه
        self.items_per_page_label = QLabel("تعداد در هر صفحه:")
        self.items_per_page_label.setFont(QFont("Vazir", 11))
        self.items_per_page_label.setStyleSheet("color: #555;")
        self.layout.addWidget(self.items_per_page_label)
        
        self.items_per_page_combo = NoWheelComboBox()
        self.items_per_page_combo.addItems(["25", "50", "100", "200", "500"])
        self.items_per_page_combo.setCurrentText("50")
        self.items_per_page_combo.setFont(QFont("Vazir", 11))
        self.items_per_page_combo.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
                min-width: 80px;
            }
        """)
        self.items_per_page_combo.currentTextChanged.connect(self.on_items_per_page_changed)
        self.layout.addWidget(self.items_per_page_combo)
        
        # دکمه‌های ناوبری
        self.first_page_btn = QPushButton("صفحه اول")
        self.prev_page_btn = QPushButton("صفحه قبلی")
        self.next_page_btn = QPushButton("صفحه بعدی")
        self.last_page_btn = QPushButton("صفحه آخر")
        
        # استایل دکمه‌ها
        button_style = """
            QPushButton {
                padding: 6px 12px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
                color: #333;
                font-weight: normal;
                min-width: 40px;
            }
            QPushButton:hover {
                background: #f0f0f0;
                border-color: #999;
            }
            QPushButton:pressed {
                background: #e0e0e0;
            }
            QPushButton:disabled {
                background: #f5f5f5;
                color: #999;
                border-color: #ddd;
            }
        """
        
        for btn in [self.first_page_btn, self.prev_page_btn, self.next_page_btn, self.last_page_btn]:
            btn.setFont(QFont("Vazir", 11))
            btn.setStyleSheet(button_style)
            btn.setCursor(Qt.PointingHandCursor)
        
        # اتصال سیگنال‌ها
        self.first_page_btn.clicked.connect(lambda: self.go_to_page(1))
        self.prev_page_btn.clicked.connect(self.go_to_previous_page)
        self.next_page_btn.clicked.connect(self.go_to_next_page)
        self.last_page_btn.clicked.connect(lambda: self.go_to_page(self.total_pages))
        
        # اضافه کردن دکمه‌ها به layout
        self.layout.addWidget(self.first_page_btn)
        self.layout.addWidget(self.prev_page_btn)
        
        # شماره صفحه فعلی
        self.page_label = QLabel()
        self.page_label.setFont(QFont("Vazir", 11))
        self.page_label.setStyleSheet("color: #333; font-weight: bold; padding: 0 10px;")
        self.layout.addWidget(self.page_label)
        
        self.layout.addWidget(self.next_page_btn)
        self.layout.addWidget(self.last_page_btn)
        
        self.update_display()
    
    def set_total_items(self, total):
        """تنظیم تعداد کل آیتم‌ها"""
        self.total_items = total
        self.total_pages = max(1, (total + self.items_per_page - 1) // self.items_per_page)
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        self.update_display()
    
    def set_current_page(self, page):
        """تنظیم صفحه فعلی"""
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self.update_display()
            self.pageChanged.emit(page)
    
    def set_items_per_page(self, items):
        """تنظیم تعداد آیتم در هر صفحه"""
        self.items_per_page = items
        self.total_pages = max(1, (self.total_items + items - 1) // items)
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        self.update_display()
    
    def go_to_page(self, page):
        """رفتن به صفحه مشخص"""
        self.set_current_page(page)
    
    def go_to_previous_page(self):
        """رفتن به صفحه قبل"""
        if self.current_page > 1:
            self.set_current_page(self.current_page - 1)
    
    def go_to_next_page(self):
        """رفتن به صفحه بعد"""
        if self.current_page < self.total_pages:
            self.set_current_page(self.current_page + 1)
    
    def on_items_per_page_changed(self, text):
        """وقتی تعداد آیتم در هر صفحه تغییر می‌کند"""
        try:
            items = int(text)
            self.set_items_per_page(items)
            self.pageChanged.emit(self.current_page)
        except ValueError:
            pass
    
    def update_display(self):
        """به‌روزرسانی نمایش"""
        # به‌روزرسانی اطلاعات
        start_item = (self.current_page - 1) * self.items_per_page + 1
        end_item = min(self.current_page * self.items_per_page, self.total_items)
        
        if self.total_items == 0:
            self.info_label.setText("هیچ آیتمی یافت نشد")
        else:
            self.info_label.setText(f"نمایش {start_item} تا {end_item} از {self.total_items} آیتم")
        
        # به‌روزرسانی شماره صفحه
        self.page_label.setText(f"صفحه {self.current_page} از {self.total_pages}")
        self.page_label.setStyleSheet("font-weight: normal;")

        # فعال/غیرفعال کردن دکمه‌ها
        self.first_page_btn.setEnabled(self.current_page > 1)
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < self.total_pages)
        self.last_page_btn.setEnabled(self.current_page < self.total_pages)
    
    def get_offset(self):
        """دریافت offset برای کوئری دیتابیس"""
        return (self.current_page - 1) * self.items_per_page
    
    def get_limit(self):
        """دریافت limit برای کوئری دیتابیس"""
        return self.items_per_page

class CustomDialog_Info(CustomPaper):
    def __init__(self, header_text="اطلاعات", main_text="", parent=None, dialog_height=340):
        # Reduce width by 25% (480 * 0.75 = 360)
        super().__init__(parent, background_color="#FFFFFF", corner_radius=15, width=360, height=dialog_height)
        self.setWindowTitle(header_text)
        main_layout = QVBoxLayout(self.frame)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(8)

        # هدر
        header_layout = QHBoxLayout()
        header_label = QLabel(header_text)
        header_label.setFont(QFont("Vazir", 13))
        header_label.setStyleSheet("color: black; background: transparent;")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFixedHeight(38)
        header_layout.addWidget(header_label, stretch=1)
        close_btn = QPushButton("×")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 18px;
                color: #888;
            }
            QPushButton:hover {
                background: #fbeaea;
                color: #d32f2f;
            }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn, alignment=Qt.AlignRight)
        main_layout.addLayout(header_layout)

        # خط جداکننده
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("color: #b0b0b0; background: #b0b0b0; height: 1px;")
        main_layout.addWidget(divider)

        # متن اصلی اسکرول‌دار
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(dialog_height - 80)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget { background: transparent; }
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                margin: 2px 2px 2px 2px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #d0d0d0;
                min-height: 32px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        # Remove line name from main_text if present (it should only be in header)
        import re
        cleaned_text = re.sub(r'^<div[^>]*>.*?</div>\s*<div[^>]*class=["\"]line-popup-separator["\"]>.*?</div>', '', main_text, flags=re.DOTALL)
        content = QLabel()
        content.setText(cleaned_text)
        content.setFont(QFont("Vazir", 12))
        content.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        content.setWordWrap(True)
        content.setStyleSheet("background: white; border-radius: 8px; padding: 8px; border: none;")
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

class CustomComboBox(QWidget):
    valueChanged = pyqtSignal(str)
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self._items = items or []
        self._current_text = ""
        self.setLayoutDirection(Qt.RightToLeft)
        self.textbox = QLineEdit(self)
        self.textbox.setReadOnly(True)
        self.textbox.setAlignment(Qt.AlignRight)
        self.textbox.setStyleSheet("padding: 8px 12px; border: 1.5px solid #bbb; border-radius: 8px; background: #fff; font-family: Vazir; font-size: 14px;")
        self.textbox.setPlaceholderText("انتخاب کنید...")
        self.textbox.mousePressEvent = self._show_popup
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.textbox)
        self.setLayout(layout)
        self._popup = None

    def set_items(self, items):
        self._items = items

    def setCurrentText(self, text):
        self._current_text = text
        self.textbox.setText(text)

    def currentText(self):
        return self.textbox.text()

    def _show_popup(self, event):
        if self._popup is not None:
            self._popup.close()
        self._popup = _ComboRightClick(self._items, self)
        self._popup.itemSelected.connect(self._on_item_selected)
        # موقعیت باز شدن: زیر تکست‌باکس و هم‌راستا با لبه راست
        textbox = self.textbox
        global_pos = textbox.mapToGlobal(textbox.rect().bottomRight())
        popup_width = textbox.width()
        popup_height = min(38 * len(self._items), 250)
        # بررسی فضای پایین صفحه
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        if global_pos.y() + popup_height > screen.bottom():
            # اگر جا نشد، بالای تکست‌باکس باز شود
            new_y = textbox.mapToGlobal(textbox.rect().topRight()).y() - popup_height
        else:
            new_y = global_pos.y()
        new_x = global_pos.x() - popup_width
        self._popup.setFixedWidth(popup_width)
        self._popup.setFixedHeight(popup_height)
        self._popup.move(new_x, new_y)
        self._popup.show()

    def _on_item_selected(self, text):
        self.setCurrentText(text)
        self.valueChanged.emit(text)
        if self._popup:
            self._popup.close()

class _ComboRightClick(CustomRightClick):
    itemSelected = pyqtSignal(str)
    def __init__(self, items, parent=None):
        super().__init__(parent)
        # حذف آیتم‌های پیش‌فرض و آیکون‌ها
        for i in reversed(range(self.frame.layout().count())):
            self.frame.layout().itemAt(i).widget().deleteLater()
        # ساخت لیست آیتم‌ها با اسکرول
        item_style = """
            QLabel {
                font-size: 16px;
                color: #222;
                padding: 8px 5px;
                background: transparent;
                border: none;
                text-align: right;
                border-radius: 8px;
            }
            QLabel:hover {
                background: #F0F0F0;
                border-radius: 8px;
            }
        """
        item_widget = QFrame()
        item_layout = QVBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(0)
        for text in items:
            item = QLabel(text)
            item.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setStyleSheet(item_style)
            item.setCursor(Qt.PointingHandCursor)
            def make_mouse_press(label, text=text):
                def handler(event):
                    self.close()
                    self.itemSelected.emit(text)
                return handler
            item.mousePressEvent = make_mouse_press(item)
            item_layout.addWidget(item)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(item_widget)
        # پاک کردن محتوای قبلی و افزودن اسکرول
        for i in reversed(range(self.frame.layout().count())):
            self.frame.layout().itemAt(i).widget().deleteLater()
        self.frame.layout().addWidget(scroll)
        # تنظیم ارتفاع دیالوگ: حداکثر 5 آیتم
        max_visible = 5
        item_height = 38
        total_height = min(len(items), max_visible) * item_height
        # تنظیم عرض بیشتر برای دیالوگ و لیست آیتم‌ها
        popup_width = 280
        items_width = 200
        self.setFixedWidth(popup_width)
        self.frame.setFixedWidth(popup_width)
        scroll.setFixedWidth(items_width)
        item_widget.setFixedWidth(items_width)
        self.setFixedHeight(total_height)
