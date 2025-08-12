from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QToolBar, QAction, QLineEdit, QLabel, QMessageBox, QStyle, QDialog, QFormLayout, QPushButton, QFileDialog, QHeaderView, QSizePolicy, QMenu, QApplication, QGroupBox, QScrollArea, QComboBox, QProgressDialog, QFrame
from PyQt5.QtCore import Qt, QEvent, QPoint, QTimer
from PyQt5.QtGui import QFont, QIcon
from modules.database import Database
from modules.custom_widgets import NoWheelComboBox, CustomDialog_Progress, CustomDialog_Flexible, CustomTableWidget, TableActions, CustomPaper
import csv
import re
import pandas as pd
import logging

# تنظیم لاگ برای دیباگ
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CircuitInputDialog(CustomPaper):
    def __init__(self, parent=None, circuit_data=None, is_edit=False):
        # تنظیم اندازه مناسب برای دیالوگ
        dialog_width = 800
        dialog_height = 400  # کاهش بیشتر ارتفاع
        
        super().__init__(parent, background_color="#F5F5F5", corner_radius=15, width=dialog_width, height=dialog_height)
        
        self.setWindowTitle("افزودن مدار" if not is_edit else "ویرایش مدار")
        self.setLayoutDirection(Qt.RightToLeft)
        self.is_edit = is_edit
        self.current_id = circuit_data.get('id') if circuit_data else None
        self.db = Database()

        # متغیرهای مربوط به جابجایی
        self.dragging = False
        self.drag_position = None

        # فونت اصلی
        self.font = QFont("Vazir", 12)

        # استایل‌های کلی
        self.setStyleSheet("""
            QGroupBox {
                font-weight: normal;
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: rgb(1, 123, 204);
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        # استایل راست‌چین برای کمبوباکس‌ها
        combo_rtl_style = """
            QComboBox {
                height:38px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }

            QComboBox QAbstractItemView {
                border-radius: 4px;
                border: 1px solid #b0b0b0;
                background: white;
                padding: 2px;
            }"""

        # چیدمان اصلی در فریم CustomPaper
        self.main_layout = QVBoxLayout(self.frame)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(8)

        # هدر
        header_layout = QHBoxLayout()
        
        # دکمه بستن در سمت راست
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
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn, alignment=Qt.AlignRight)
        
        # فاصله
        header_layout.addSpacing(10)
        
        # عنوان در وسط
        header_text = "افزودن مدار" if not is_edit else "ویرایش مدار"
        header_label = QLabel(header_text)
        header_label.setFont(QFont("Vazir", 12))
        header_label.setStyleSheet("color: black; background: transparent;")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFixedHeight(38)
        header_layout.addWidget(header_label, stretch=1)
        
        # فاصله در سمت چپ
        header_layout.addSpacing(38)  # همان اندازه دکمه بستن
        
        self.main_layout.addLayout(header_layout)
        
        # خط جداکننده
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("color: #b0b0b0; background: #b0b0b0; height: 1px;")
        self.main_layout.addWidget(divider)

        # محتوای اصلی
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 10, 0, 0)
        content_layout.setSpacing(15)
        self.main_layout.addLayout(content_layout)

        # عرض responsive برای ویجت‌ها
        label_width = 120
        widget_width = 200
        combo_width = 300  # کاهش عرض
        line_name_width = 400  # کاهش عرض برای نام خط

        # سکشن ۱: اطلاعات پایه
        self.section1 = QGroupBox("اطلاعات پایه")
        self.section1.setFont(self.font)
        self.section1.setStyleSheet("""
            QGroupBox {
                background-color: #F5F5F5;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
                font-weight: normal;
            }
            QGroupBox::title {
                color: rgb(1, 123, 204);
                background-color: #F5F5F5;
                border-radius: 8px;
                border: 0px solid #E0E0E0;
                subcontrol-origin: margin;
                left: 20px;
                padding: 0px 5px 0px 5px;
            }
        """)
        self.section1_layout = QVBoxLayout()
        self.section1_layout.setContentsMargins(15, 10, 15, 10)
        self.section1_layout.setSpacing(10)
        self.section1.setLayout(self.section1_layout)

        # ردیف ۱: کد دیسپاچینگ و نام مدار
        self.dispatch_code = QLineEdit()
        self.dispatch_code.setFont(self.font)
        self.dispatch_code.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.dispatch_code.setFixedWidth(widget_width)
        
        self.circuit_name = QLineEdit()
        self.circuit_name.setFont(self.font)
        self.circuit_name.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.circuit_name.setFixedWidth(widget_width)
        
        row1 = QHBoxLayout()
        label1_1 = QLabel("کد دیسپاچینگ:", font=self.font)
        label1_1.setFixedWidth(label_width)
        label1_1.setStyleSheet("background-color: transparent;")
        row1.addWidget(label1_1)
        row1.addWidget(self.dispatch_code)
        row1.addSpacing(20)
        label1_2 = QLabel("نام مدار:", font=self.font)
        label1_2.setFixedWidth(label_width)
        label1_2.setStyleSheet("background-color: transparent;")
        row1.addWidget(label1_2)
        row1.addWidget(self.circuit_name)
        row1.addStretch()
        self.section1_layout.addLayout(row1)

        # ردیف ۲: ولتاژ و تعداد باندل
        self.voltage = NoWheelComboBox()
        self.voltage.setFont(self.font)
        self.voltage.addItems(["","400", "230", "132", "63"])
        self.voltage.setStyleSheet(combo_rtl_style)
        self.voltage.setFixedWidth(widget_width)
        
        self.bundle_number = NoWheelComboBox()
        self.bundle_number.setFont(self.font)
        self.bundle_number.addItems(["", "1", "2", "3", "4", "5", "6"])
        self.bundle_number.setStyleSheet(combo_rtl_style)
        self.bundle_number.setFixedWidth(widget_width)
        
        row2 = QHBoxLayout()
        label2_1 = QLabel("ولتاژ (kV):", font=self.font)
        label2_1.setFixedWidth(label_width)
        label2_1.setStyleSheet("background-color: transparent;")
        row2.addWidget(label2_1)
        row2.addWidget(self.voltage)
        row2.addSpacing(20)
        label2_2 = QLabel("تعداد باندل:", font=self.font)
        label2_2.setFixedWidth(label_width)
        label2_2.setStyleSheet("background-color: transparent;")
        row2.addWidget(label2_2)
        row2.addWidget(self.bundle_number)
        row2.addStretch()
        self.section1_layout.addLayout(row2)

        # ردیف ۳: طول مدار و نوع سیم
        self.circuit_length = QLineEdit()
        self.circuit_length.setFont(self.font)
        self.circuit_length.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.circuit_length.setFixedWidth(widget_width)
        self.circuit_length.setPlaceholderText("کیلومتر")
        
        self.wire_type = NoWheelComboBox()
        self.wire_type.setFont(self.font)
        self.wire_type.addItems(["", "لینکس", "کاناری", "کرلو", "داگ"])
        self.wire_type.setStyleSheet(combo_rtl_style)
        self.wire_type.setFixedWidth(widget_width)
        
        row3 = QHBoxLayout()
        label3_1 = QLabel("طول مدار (km):", font=self.font)
        label3_1.setFixedWidth(label_width)
        label3_1.setStyleSheet("background-color: transparent;")
        row3.addWidget(label3_1)
        row3.addWidget(self.circuit_length)
        row3.addSpacing(20)
        label3_2 = QLabel("نوع سیم:", font=self.font)
        label3_2.setFixedWidth(label_width)
        label3_2.setStyleSheet("background-color: transparent;")
        row3.addWidget(label3_2)
        row3.addWidget(self.wire_type)
        row3.addStretch()
        self.section1_layout.addLayout(row3)

        # ردیف ۴: نوع مقره و سال سیم کشی
        self.insulator_type = NoWheelComboBox()
        self.insulator_type.setFont(self.font)
        self.insulator_type.addItems(["", "پورسلین", "شیشه‌ای", "سیلیکون", "پلیمری"])
        self.insulator_type.setStyleSheet(combo_rtl_style)
        self.insulator_type.setFixedWidth(widget_width)
        
        self.wiring_year = QLineEdit()
        self.wiring_year.setFont(self.font)
        self.wiring_year.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.wiring_year.setFixedWidth(widget_width)
        self.wiring_year.setPlaceholderText("YYYY")
        
        row4 = QHBoxLayout()
        label4_1 = QLabel("نوع مقره:", font=self.font)
        label4_1.setFixedWidth(label_width)
        label4_1.setStyleSheet("background-color: transparent;")
        row4.addWidget(label4_1)
        row4.addWidget(self.insulator_type)
        row4.addSpacing(20)
        label4_2 = QLabel("سال سیم کشی:", font=self.font)
        label4_2.setFixedWidth(label_width)
        label4_2.setStyleSheet("background-color: transparent;")
        row4.addWidget(label4_2)
        row4.addWidget(self.wiring_year)
        row4.addStretch()
        self.section1_layout.addLayout(row4)

        content_layout.addWidget(self.section1)

        # دکمه‌های ذخیره و لغو
        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("ذخیره")
        self.save_button.setFont(self.font)
        self.save_button.setStyleSheet("padding: 8px 30px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; min-width: 100px;")
        self.cancel_button = QPushButton("لغو")
        self.cancel_button.setFont(self.font)
        self.cancel_button.setStyleSheet("padding: 8px 30px; background-color: #f44336; color: white; border: none; border-radius: 5px; min-width: 100px;")
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)
        content_layout.addLayout(self.button_layout)

        # اتصال دکمه‌ها
        self.save_button.clicked.connect(self.save_circuit)
        self.cancel_button.clicked.connect(self.reject)

        # اشاره‌گر موس برای دکمه‌های ذخیره و لغو
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setCursor(Qt.PointingHandCursor)

        # پر کردن فیلدها در حالت ویرایش
        if circuit_data:
            self.dispatch_code.setText(str(circuit_data.get('Dispatch_Code', '')))
            self.circuit_name.setText(str(circuit_data.get('Circuit_Name', '')))
            self.voltage.setCurrentText(str(circuit_data.get('Voltage', '')))
            self.bundle_number.setCurrentText(str(circuit_data.get('Bundle_Number', '')))
            self.circuit_length.setText(str(circuit_data.get('Circuit_length', '')))
            self.wire_type.setCurrentText(str(circuit_data.get('Wire_Type', '')))
            self.insulator_type.setCurrentText(str(circuit_data.get('Insulator_Type', '')))
            self.wiring_year.setText(str(circuit_data.get('Operation_Year', '')))

        # تنظیم اندازه خودکار
        content_layout.addStretch()
        self.adjust_dialog_size()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # بررسی اینکه آیا کلیک روی هدر است
            header_height = 38 + 32  # ارتفاع هدر + margins
            if event.pos().y() <= header_height:
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def adjust_dialog_size(self):
        sections = [self.section1]
        total_height = 0
        
        # ارتفاع هدر و جداکننده
        header_height = 38  # ارتفاع هدر
        divider_height = 1  # ارتفاع جداکننده
        header_margins = 32  # margins هدر (16 بالا + 16 پایین)
        
        for section in sections:
            total_height += self.calculate_section_height(section)
        button_height = self.save_button.sizeHint().height() + 10
        
        # محاسبه کل ارتفاع
        total_height += (
            header_height + divider_height + header_margins +  # هدر و جداکننده
            button_height +
            self.main_layout.spacing() * (len(sections) + 1) +
            self.main_layout.contentsMargins().top() +
            self.main_layout.contentsMargins().bottom()
        )
        
        dialog_width = 800  # عرض ثابت
        dialog_height = min(total_height, 400)  # کاهش بیشتر حداکثر ارتفاع
        self.set_size(dialog_width, dialog_height)

    def calculate_section_height(self, section):
        layout = section.layout()
        total_height = layout.contentsMargins().top() + layout.contentsMargins().bottom()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.layout():
                widget = item.layout().itemAt(1).widget()
                if widget:
                    total_height += widget.sizeHint().height()
            total_height += layout.spacing()
        total_height += section.fontMetrics().height() + 20
        return total_height

    def validate_inputs(self):
        try:
            if not self.dispatch_code.text().strip():
                return False, "کد دیسپاچینگ اجباری است!"
            if not self.circuit_name.text().strip():
                return False, "نام مدار اجباری است!"
            if not self.voltage.currentText():
                return False, "ولتاژ اجباری است!"
            if self.bundle_number.currentText() and not re.match(r"^\d+$", self.bundle_number.currentText()):
                return False, "تعداد باندل باید عدد صحیح باشد!"
            if self.circuit_length.text() and not re.match(r"^\d*\.?\d*$", self.circuit_length.text()):
                return False, "طول مدار باید عدد باشد!"
            if self.wiring_year.text() and not re.match(r"^\d{4}$", self.wiring_year.text()):
                return False, "سال سیم کشی باید عدد چهار رقمی باشد!"
            try:
                existing_codes = self.db.fetch_all(
                    "SELECT Circuit_Code FROM circuits WHERE Circuit_Code != ? AND id != ?",
                    (self.dispatch_code.text(), self.current_id or -1)
                )
            except Exception as e:
                dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در بررسی یکتایی کد دیسپاچینگ: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
                dlg.exec_()
                return False, "خطا در بررسی یکتایی کد دیسپاچینگ"
            if existing_codes and self.dispatch_code.text() in [code[0] for code in existing_codes]:
                return False, "کد دیسپاچینگ باید یکتا باشد!"
            try:
                existing_names = self.db.fetch_all(
                    "SELECT Circuit_Name FROM circuits WHERE Circuit_Name != ? AND id != ?",
                    (self.circuit_name.text(), self.current_id or -1)
                )
            except Exception as e:
                dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در بررسی یکتایی نام مدار: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
                dlg.exec_()
                return False, "خطا در بررسی یکتایی نام مدار"
            if existing_names and self.circuit_name.text() in [name[0] for name in existing_names]:
                return False, "نام مدار باید یکتا باشد!"
            return True, ""
        except Exception as e:
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطای غیرمنتظره در اعتبارسنجی: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()
            return False, "خطای غیرمنتظره در اعتبارسنجی"

    def save_circuit(self):
        is_valid, error_msg = self.validate_inputs()
        if not is_valid:
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=error_msg, ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            dlg.exec_()
            return

        def format_number(value, is_integer=False):
            if value:
                try:
                    num = float(value)
                    if is_integer:
                        return str(int(num))
                    return str(int(num)) if num.is_integer() else str(num).rstrip('0').rstrip('.')
                except ValueError:
                    return value
            return value

        self.circuit_data = {
            'Circuit_Code': self.dispatch_code.text(),
            'Circuit_Name': self.circuit_name.text(),
            'Voltage': self.voltage.currentText(),
            'Dispatch_Code': self.dispatch_code.text(),
            'Bundle_Number': self.bundle_number.currentText(),
            'Circuit_length': format_number(self.circuit_length.text()),
            'Wire_Type': self.wire_type.currentText(),
            'Insulator_Type': self.insulator_type.currentText(),
            'Operation_Year': self.wiring_year.text(),
            'id': self.current_id
        }
        self.accept()

class CircuitsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)  # کاهش margins
        self.layout.setSpacing(10)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.column_filters = {}
        self.original_headers = [
            "کد دیسپاچینگ", "نام مدار", "ولتاژ", "تعداد باندل", "طول مدار (کیلومتر)", "نوع سیم", "نوع مقره", "سال سیم کشی"
        ]
        self.column_names = [
            "Dispatch_Code", "Circuit_Name", "Voltage", "Bundle_Number", "Circuit_length", "Wire_Type", "Insulator_Type", "Operation_Year"
        ]

        self.toolbar = QToolBar()
        self.toolbar.setFont(QFont("Vazir", 12))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.setStyleSheet("""
            QToolBar { 
                background-color: #e0e0e0; 
                padding: 5px; 
                spacing: 8px; 
                border-radius: 8px;
            }
            QToolButton { 
                margin: 2px; 
                direction: ltr; 
                background-color: transparent !important; 
                border: none; 
                padding: 2px; 
                cursor: pointer !important;
            }
            QToolButton:flat { background: transparent; }
            QToolButton:hover { 
                background-color: #d0d0d0;
                cursor: pointer !important;
                border-radius: 5px;
                padding: 5px; 
            }
            QToolSeparator { color: #333333; font-weight: bold; width: 10px; }
        """)
        self.layout.addWidget(self.toolbar)

        self.add_action = QAction(QIcon("Resources/Icons/Add_Item.png"), "افزودن مدار جدید", self)
        self.copy_action = QAction(QIcon("Resources/Icons/Toolsbar_Copy.png"), "کپی", self)
        self.delete_action = QAction(QIcon("Resources/Icons/Delete_Table.png"), "حذف", self)
        self.edit_action = QAction(QIcon("Resources/Icons/Edit_Table.png"), "ویرایش", self)
        self.import_excel_action = QAction(QIcon("Resources/Icons/Import_From_Excel.png"), "ورود اطلاعات از اکسل", self)
        self.report_action = QAction(QIcon("resources/Icons/Export_From_Excel.png"), "خروج اطلاعات به اکسل", self)
        self.back_action = QAction(QIcon("resources/Icons/Back.png"), "برگشت", self)

        self.toolbar.addAction(self.add_action)
        self.toolbar.addSeparator().setText("|")
        self.toolbar.addAction(self.copy_action)
        self.toolbar.addSeparator().setText("|")
        self.toolbar.addAction(self.delete_action)
        self.toolbar.addSeparator().setText("|")
        self.toolbar.addAction(self.edit_action)
        self.toolbar.addSeparator().setText("|")
        self.toolbar.addAction(self.import_excel_action)
        self.toolbar.addSeparator().setText("|")
        self.toolbar.addAction(self.report_action)
        self.toolbar.addSeparator().setText("|")
        self.toolbar.addAction(self.back_action)

        for action in [self.add_action, self.copy_action, self.delete_action, self.edit_action, self.import_excel_action, self.report_action, self.back_action]:
            btn = self.toolbar.widgetForAction(action)
            if btn is not None:
                btn.setCursor(Qt.PointingHandCursor)

        self.add_action.triggered.connect(self.add_circuit)
        self.copy_action.triggered.connect(lambda: self.safe_copy())
        self.delete_action.triggered.connect(self.delete_circuit)
        self.edit_action.triggered.connect(self.edit_circuit)
        self.import_excel_action.triggered.connect(self.import_from_excel)
        self.report_action.triggered.connect(self.generate_report)
        self.back_action.triggered.connect(self.close)

        # Table
        self.table = CustomTableWidget(
            table_name="circuits",
            headers=self.original_headers,
            column_names=self.column_names,
            db=self.db
        )
        self.layout.addWidget(self.table, 1)  # stretch factor = 1
        self.table.table.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.table.table.customContextMenuRequested.connect(self.show_context_menu)  # حذف شد
        self.table.load_table()
        self.table._custom_edit_callback = self.edit_circuit
        self.table._custom_clear_filters_callback = self.clear_all_filters
        
        # اتصال سیگنال itemChanged برای ویرایش سلولی
        self.table.table.itemChanged.connect(self.save_cell_edit)

    def update_column_filter(self, column_index, filter_text):
        try:
            column_name = self.column_names[column_index]
            if filter_text:
                self.column_filters[column_name] = filter_text
            elif column_name in self.column_filters:
                del self.column_filters[column_name]
            
            # به‌روزرسانی هدرها با آیکن فیلتر
            header = self.table.horizontalHeader()
            for i, name in enumerate(self.column_names):
                if name in self.column_filters and self.column_filters[name]:
                    # نمایش آیکن فیلتر
                    header_item = QTableWidgetItem(self.original_headers[i])
                    header_item.setIcon(QIcon("resources/Icons/Filter_Table.png"))
                    self.table.setHorizontalHeaderItem(i, header_item)
                else:
                    # حذف آیکن فیلتر
                    header_item = QTableWidgetItem(self.original_headers[i])
                    self.table.setHorizontalHeaderItem(i, header_item)
            
            self.load_table()
        except Exception as e:
            logging.error(f"Error in update_column_filter: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در به‌روزرسانی فیلتر: {str(e)}")
    
    def clear_all_filters(self):
        """حذف تمام فیلترهای ستون‌ها"""
        try:
            # پاک کردن فیلترهای ستون‌ها
            self.column_filters.clear()
            
            # بازگرداندن هدرها به حالت عادی (حذف آیکن فیلتر)
            header = self.table.horizontalHeader()
            for i in range(len(self.original_headers)):
                header_item = QTableWidgetItem(self.original_headers[i])
                self.table.setHorizontalHeaderItem(i, header_item)
            
            # بارگذاری مجدد جدول
            self.load_table()
            
            logging.debug("Circuits window column filters cleared successfully")
        except Exception as e:
            logging.error(f"Error in clear_all_filters: {str(e)}", exc_info=True)

    def load_table(self, global_filter=""):
        try:
            query = """
                SELECT Dispatch_Code, Circuit_Name, Voltage, Bundle_Number, Circuit_length, Wire_Type, Insulator_Type, Operation_Year, id
                FROM circuits
            """
            params = []
            conditions = []
            if global_filter:
                conditions.append("""
                    (Dispatch_Code LIKE ? OR Circuit_Name LIKE ? OR Voltage LIKE ? OR Bundle_Number LIKE ?
                    OR Circuit_length LIKE ? OR Wire_Type LIKE ? OR Insulator_Type LIKE ? OR Operation_Year LIKE ?)
                """)
                params.extend([f"%{global_filter}%"] * 8)
            for column, filter_text in self.column_filters.items():
                if filter_text:
                    conditions.append(f"{column} LIKE ?")
                    params.append(f"%{filter_text}%")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            rows = self.db.fetch_all(query, tuple(params))
            self.table.table.setRowCount(len(rows))
            self.table.table.blockSignals(True)
            for row_idx, row_data in enumerate(rows):
                for col_idx, data in enumerate(row_data[:-1]):
                    data = str(data) if data is not None else ""
                    if col_idx == 4:  # Circuit_length
                        try:
                            num = float(data)
                            data = str(int(num)) if num.is_integer() else str(num).rstrip('0').rstrip('.')
                        except (ValueError, TypeError):
                            pass
                    item = QTableWidgetItem(data)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    self.table.table.setItem(row_idx, col_idx, item)
                self.table.table.item(row_idx, 0).setData(Qt.UserRole, row_data[-1])
            self.table.table.blockSignals(False)
            self.table.table.resizeColumnsToContents()
            for col in range(self.table.table.columnCount()):
                if self.table.table.columnWidth(col) < 100:
                    self.table.table.setColumnWidth(col, 100)
            self.table.table.resizeRowsToContents()
            self.table.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        except Exception as e:
            logging.error(f"[load_table] Error: {str(e)}", exc_info=True)
            try:
                # Use top-level import for CustomDialog_Flexible
                dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در بارگذاری جدول: {str(e)}", ok_text="باشه", parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical)))
                dlg.exec_()
            except Exception as ex:
                logging.error(f"[load_table] Error showing dialog: {str(ex)}", exc_info=True)

    def add_circuit(self):
        dialog = CircuitInputDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            circuit_data = dialog.circuit_data
            try:
                self.db.execute_query(
                    """
                    INSERT INTO circuits (Circuit_Code, Circuit_Name, Voltage, Dispatch_Code, Bundle_Number,
                                         Circuit_length, Wire_Type, Insulator_Type, Operation_Year)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        circuit_data['Circuit_Code'], circuit_data['Circuit_Name'], circuit_data['Voltage'],
                        circuit_data['Dispatch_Code'], circuit_data['Bundle_Number'], circuit_data['Circuit_length'],
                        circuit_data['Wire_Type'], circuit_data['Insulator_Type'], circuit_data['Operation_Year']
                    )
                )
                self.load_table()
                dlg = CustomDialog_Flexible(header_text="موفقیت", main_text="مدار با موفقیت اضافه شد.", ok_text="باشه", parent=self)
                dlg.exec_()
            except Exception as e:
                logging.error(f"Error in add_circuit: {str(e)}")
                dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در افزودن مدار: {str(e)}", ok_text="باشه", parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical)))
                dlg.exec_()

    def edit_circuit(self):
        selected = self.table.table.selectedItems()
        if not selected:
            # Use top-level import for CustomDialog_Flexible
            dlg = CustomDialog_Flexible(
                header_text="هشدار",
                main_text="لطفاً ابتدا مدار مورد نظر را انتخاب کنید.",
                ok_text="باشه",
                parent=self,
                icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            )
            dlg.exec_()
            return
        row = self.table.table.currentRow()
        dispatch_code = self.table.table.item(row, 0).text() if self.table.table.item(row, 0) else ""
        try:
            result = self.db.fetch_all("SELECT id FROM circuits WHERE Dispatch_Code=?", (dispatch_code,))
            if not result:
                QMessageBox.critical(self, "خطا", "مدار موردنظر یافت نشد!")
                return
            current_id = result[0][0]
            circuit_data = {
                'id': current_id,
                'Dispatch_Code': dispatch_code,
                'Circuit_Name': self.table.table.item(row, 1).text() if self.table.table.item(row, 1) else "",
                'Voltage': self.table.table.item(row, 2).text() if self.table.table.item(row, 2) else "",
                'Bundle_Number': self.table.table.item(row, 3).text() if self.table.table.item(row, 3) else "",
                'Circuit_length': self.table.table.item(row, 4).text() if self.table.table.item(row, 4) else "",
                'Wire_Type': self.table.table.item(row, 5).text() if self.table.table.item(row, 5) else "",
                'Insulator_Type': self.table.table.item(row, 6).text() if self.table.table.item(row, 6) else "",
                'Operation_Year': self.table.table.item(row, 7).text() if self.table.table.item(row, 7) else ""
            }
            dialog = CircuitInputDialog(self, circuit_data, is_edit=True)
            if dialog.exec_() == QDialog.Accepted:
                circuit_data = dialog.circuit_data
                # بررسی تکراری نبودن Dispatch_Code برای رکوردهای دیگر
                duplicate = self.db.fetch_all(
                    "SELECT id FROM circuits WHERE Dispatch_Code=? AND id<>?",
                    (circuit_data['Dispatch_Code'], circuit_data['id'])
                )
                if duplicate:
                    dlg = CustomDialog_Flexible(header_text="خطا", main_text="کد دیسپاچینگ وارد شده قبلاً برای مدار دیگری ثبت شده است!", ok_text="باشه", parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical)))
                    dlg.exec_()
                    return
                try:
                    self.db.execute_query(
                        """
                        UPDATE circuits SET Circuit_Code=?, Circuit_Name=?, Voltage=?, Dispatch_Code=?,
                                           Bundle_Number=?, Circuit_length=?, Wire_Type=?, Insulator_Type=?, Operation_Year=?
                        WHERE id=?
                        """,
                        (
                            circuit_data['Circuit_Code'], circuit_data['Circuit_Name'], circuit_data['Voltage'],
                            circuit_data['Dispatch_Code'], circuit_data['Bundle_Number'], circuit_data['Circuit_length'],
                            circuit_data['Wire_Type'], circuit_data['Insulator_Type'], circuit_data['Operation_Year'], circuit_data['id']
                        )
                    )
                    self.table.load_table()
                    dlg = CustomDialog_Flexible(header_text="موفقیت", main_text="مدار با موفقیت ویرایش شد.", ok_text="باشه", parent=self)
                    dlg.exec_()
                except Exception as e:
                    logging.error(f"Error in edit_circuit: {str(e)}")
                    dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در ویرایش مدار: {str(e)}", ok_text="باشه", parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical)))
                    dlg.exec_()
        except Exception as e:
            logging.error(f"Error in edit_circuit: {str(e)}")
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در ویرایش مدار: {str(e)}", ok_text="باشه", parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical)))
            dlg.exec_()

    def copy_circuit(self):
        selected_rows = sorted(set(index.row() for index in self.table.table.selectedIndexes()))
        if not selected_rows:
            dlg = CustomDialog_Flexible(
                header_text="هشدار",
                main_text="لطفاً ابتدا مدار مورد نظر را انتخاب کنید.",
                ok_text="باشه",
                parent=self,
                icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            )
            dlg.exec_()
            return

        row_count = len(selected_rows)
        msg = f"آیا از کپی کردن این {row_count} مدار مطمئن هستید؟"
        dlg = CustomDialog_Flexible(
            header_text="تأیید کپی",
            main_text=msg,
            ok_text="بله",
            cancel_text="خیر",
            parent=self
        )
        if dlg.exec_() != dlg.Accepted:
            return

        try:
            progress = CustomDialog_Progress(header_text="در حال کپی کردن مدارها...", cancel_text="لغو عملیات", parent=self)
            progress.set_maximum(row_count)
            progress.set_progress(0)
            progress.set_text(f"0 از {row_count}")
            progress.show()
            QApplication.processEvents()
            self.copy_cancelled = False
            copied_count = 0
            def cancel():
                self.copy_cancelled = True
            progress.cancel_btn.clicked.connect(cancel)
            
            # ابتدا اطلاعات مدارها انتخاب شده را جمع‌آوری کنیم
            circuits_to_copy = []
            for row in selected_rows:
                try:
                    dispatch_code = self.table.table.item(row, 0).text() if self.table.table.item(row, 0) else ""
                    circuit_name = self.table.table.item(row, 1).text() if self.table.table.item(row, 1) else ""
                    voltage = self.table.table.item(row, 2).text() if self.table.table.item(row, 2) else ""
                    bundle_number = self.table.table.item(row, 3).text() if self.table.table.item(row, 3) else ""
                    circuit_length = self.table.table.item(row, 4).text() if self.table.table.item(row, 4) else ""
                    wire_type = self.table.table.item(row, 5).text() if self.table.table.item(row, 5) else ""
                    insulator_type = self.table.table.item(row, 6).text() if self.table.table.item(row, 6) else ""
                    operation_year = self.table.table.item(row, 7).text() if self.table.table.item(row, 7) else ""
                    
                    if dispatch_code and circuit_name:
                        circuits_to_copy.append({
                            'Dispatch_Code': dispatch_code,
                            'Circuit_Name': circuit_name,
                            'Voltage': voltage,
                            'Bundle_Number': bundle_number,
                            'Circuit_length': circuit_length,
                            'Wire_Type': wire_type,
                            'Insulator_Type': insulator_type,
                            'Operation_Year': operation_year
                        })
                except Exception as e:
                    logging.error(f"Error reading circuit data from row {row}: {str(e)}")
                    continue
            
            # حالا کپی را انجام دهیم
            for i, circuit_data in enumerate(circuits_to_copy):
                try:
                    QApplication.processEvents()
                    if self.copy_cancelled:
                        break
                    progress.set_progress(i + 1)
                    progress.set_text(f"{i+1} از {row_count}")
                    
                    # ایجاد کد دیسپاچینگ جدید با پسوند _COPY
                    original_code = circuit_data['Dispatch_Code']
                    new_code = f"{original_code}_COPY"
                    
                    # بررسی یکتایی کد جدید
                    existing = self.db.fetch_all("SELECT Dispatch_Code FROM circuits WHERE Dispatch_Code=?", (new_code,))
                    if existing:
                        # اگر کد تکراری بود، شماره اضافه کن
                        counter = 1
                        while True:
                            new_code = f"{original_code}_COPY_{counter}"
                            existing = self.db.fetch_all("SELECT Dispatch_Code FROM circuits WHERE Dispatch_Code=?", (new_code,))
                            if not existing:
                                break
                            counter += 1
                    
                    # ایجاد نام جدید
                    original_name = circuit_data['Circuit_Name']
                    new_name = f"{original_name} (کپی)"
                    
                    # بررسی یکتایی نام جدید
                    existing = self.db.fetch_all("SELECT Circuit_Name FROM circuits WHERE Circuit_Name=?", (new_name,))
                    if existing:
                        # اگر نام تکراری بود، شماره اضافه کن
                        counter = 1
                        while True:
                            new_name = f"{original_name} (کپی {counter})"
                            existing = self.db.fetch_all("SELECT Circuit_Name FROM circuits WHERE Circuit_Name=?", (new_name,))
                            if not existing:
                                break
                            counter += 1
                    
                    # درج مدار جدید
                    self.db.execute_query(
                        """
                        INSERT INTO circuits (Circuit_Code, Circuit_Name, Voltage, Dispatch_Code, Bundle_Number,
                                             Circuit_length, Wire_Type, Insulator_Type, Operation_Year)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            new_code, new_name, circuit_data['Voltage'], new_code, circuit_data['Bundle_Number'],
                            circuit_data['Circuit_length'], circuit_data['Wire_Type'], circuit_data['Insulator_Type'], 
                            circuit_data['Operation_Year']
                        )
                    )
                    copied_count += 1
                except Exception as e:
                    logging.error(f"Error copying circuit {circuit_data.get('Dispatch_Code', 'Unknown')}: {str(e)}")
                    continue
            
            # بستن progress dialog
            try:
                progress.close()
            except:
                pass
            
            try:
                self.table.load_table()
            except Exception as e:
                logging.error(f"Error in load_table after copy: {str(e)}")
            
            if self.copy_cancelled:
                msg = f"عملیات لغو شد و {copied_count} مدار تا این لحظه کپی شد."
                self.table.table.clearSelection()
                dlg = CustomDialog_Flexible(header_text="لغو عملیات", main_text=msg, ok_text="باشه", parent=self)
                dlg.exec_()
            elif copied_count > 0:
                self.table.table.clearSelection()
                dlg = CustomDialog_Flexible(header_text="موفقیت", main_text=f"{copied_count} مدار با موفقیت کپی شد.", ok_text="باشه", parent=self)
                dlg.exec_()
            else:
                dlg = CustomDialog_Flexible(header_text="هشدار", main_text="هیچ مداری کپی نشد.", ok_text="باشه", parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning)))
                dlg.exec_()
        except Exception as e:
            logging.error(f"Error in copy_circuit: {str(e)}")
            try:
                progress.close()
            except:
                pass
            self.table.table.clearSelection()
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در کپی کردن: {str(e)}", ok_text="باشه", parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical)))
            dlg.exec_()

    def safe_copy(self):
        """کپی کردن مدار انتخاب شده - مشابه عملکرد کلیک راست"""
        try:
            TableActions.copy_selected(self.table.table, self.db, self, "circuits", self.table.load_table)
        except Exception as e:
            logging.error(f"Exception in safe_copy: {str(e)}", exc_info=True)
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در کپی: {str(e)}", ok_text="باشه", parent=self)
            dlg.exec_()

    def delete_circuit(self):
        selected_rows = sorted(set(index.row() for index in self.table.table.selectedIndexes()))
        if not selected_rows:
            # Use top-level import for CustomDialog_Flexible
            dlg = CustomDialog_Flexible(
                header_text="هشدار",
                main_text="لطفاً ابتدا مدار مورد نظر را انتخاب کنید.",
                ok_text="باشه",
                parent=self,
                icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            )
            dlg.exec_()
            return

        row_count = len(selected_rows)
        msg = f"آیا از حذف این {row_count} مدار مطمئن هستید؟"
        # Use top-level import for CustomDialog_Flexible
        dlg = CustomDialog_Flexible(
            header_text="تأیید حذف",
            main_text=msg,
            ok_text="بله",
            cancel_text="خیر",
            parent=self
        )
        if dlg.exec_() != dlg.Accepted:
            return

        try:
            progress = CustomDialog_Progress(header_text="در حال حذف مدارها...", cancel_text="لغو عملیات", parent=self)
            progress.set_maximum(row_count)
            progress.set_progress(0)
            progress.set_text(f"0 از {row_count}")
            progress.show()
            QApplication.processEvents()
            self.deletion_cancelled = False
            deleted_count = 0
            def cancel():
                self.deletion_cancelled = True
            progress.cancel_btn.clicked.connect(cancel)
            # ابتدا کدهای مدارها انتخاب شده را جمع‌آوری کنیم
            circuit_codes_to_delete = []
            for row in selected_rows:
                dispatch_code = self.table.table.item(row, 0).text() if self.table.table.item(row, 0) else ""
                if dispatch_code:
                    circuit_codes_to_delete.append(dispatch_code)
            
            # حالا حذف را انجام دهیم
            for i, dispatch_code in enumerate(circuit_codes_to_delete):
                try:
                    QApplication.processEvents()
                    if self.deletion_cancelled:
                        break
                    progress.set_progress(i + 1)
                    progress.set_text(f"{i+1} از {row_count}")
                    self.db.execute_query("DELETE FROM circuits WHERE Dispatch_Code=?", (dispatch_code,))
                    deleted_count += 1
                except Exception as e:
                    logging.error(f"Error deleting circuit {dispatch_code}: {str(e)}")
                    continue
            # بستن progress dialog
            try:
                progress.close()
            except:
                pass
            
            try:
                self.table.load_table()
            except Exception as e:
                logging.error(f"Error in load_table after deletion: {str(e)}")
            if self.deletion_cancelled:
                msg = f"عملیات لغو شد و {deleted_count} مدار تا این لحظه حذف شد."
                self.table.table.clearSelection()
                dlg = CustomDialog_Flexible(header_text="لغو عملیات", main_text=msg, ok_text="باشه", parent=self)
                dlg.exec_()
            elif deleted_count > 0:
                self.table.table.clearSelection()
                dlg = CustomDialog_Flexible(header_text="موفقیت", main_text=f"{deleted_count} مدار با موفقیت حذف شد.", ok_text="باشه", parent=self)
                dlg.exec_()
        except Exception as e:
            logging.error(f"Error in delete_circuit: {str(e)}\n{traceback.format_exc()}")
            try:
                progress.close()
            except:
                pass
            self.table.table.clearSelection()
            QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")

    def load_row_data(self, row, col):
        pass

    def save_cell_edit(self, item):
        """ذخیره تغییرات سلول در جدول مدارها"""
        try:
            row = item.row()
            col = item.column()
            new_value = item.text().strip()
            column_name = self.column_names[col]
            circuit_id = self.table.table.item(row, 0).data(Qt.UserRole)  # گرفتن id

            # اعتبارسنجی
            if column_name == "Circuit_Name" and not new_value:
                dlg = CustomDialog_Flexible(
                    header_text="خطا",
                    main_text="نام مدار اجباری است!",
                    ok_text="باشه",
                    parent=self,
                    icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                )
                dlg.exec_()
                self.table.load_table()
                return
            if column_name == "Dispatch_Code" and not new_value:
                dlg = CustomDialog_Flexible(
                    header_text="خطا",
                    main_text="کد دیسپاچینگ اجباری است!",
                    ok_text="باشه",
                    parent=self,
                    icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                )
                dlg.exec_()
                self.table.load_table()
                return
            if column_name == "Voltage" and not new_value:
                dlg = CustomDialog_Flexible(
                    header_text="خطا",
                    main_text="ولتاژ اجباری است!",
                    ok_text="باشه",
                    parent=self,
                    icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                )
                dlg.exec_()
                self.table.load_table()
                return
            if column_name == "Bundle_Number" and new_value:
                if not re.match(r"^\d+$", new_value):
                    dlg = CustomDialog_Flexible(
                        header_text="خطا",
                        main_text="تعداد باندل باید عدد صحیح باشد!",
                        ok_text="باشه",
                        parent=self,
                        icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    )
                    dlg.exec_()
                    self.table.load_table()
                    return
            if column_name == "Circuit_length" and new_value:
                if not re.match(r"^\d*\.?\d*$", new_value):
                    dlg = CustomDialog_Flexible(
                        header_text="خطا",
                        main_text="طول مدار باید عدد باشد!",
                        ok_text="باشه",
                        parent=self,
                        icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    )
                    dlg.exec_()
                    self.table.load_table()
                    return
            if column_name == "Operation_Year" and new_value:
                if not re.match(r"^\d{4}$", new_value):
                    dlg = CustomDialog_Flexible(
                        header_text="خطا",
                        main_text="سال سیم کشی باید عدد چهار رقمی باشد!",
                        ok_text="باشه",
                        parent=self,
                        icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    )
                    dlg.exec_()
                    self.table.load_table()
                    return

            # بررسی یکتایی کد دیسپاچینگ
            if column_name == "Dispatch_Code" and new_value:
                existing_codes = self.db.fetch_all(
                    "SELECT Dispatch_Code FROM circuits WHERE Dispatch_Code != ? AND id != ?",
                    (new_value, circuit_id)
                )
                if existing_codes and new_value in [code[0] for code in existing_codes]:
                    dlg = CustomDialog_Flexible(
                        header_text="خطا",
                        main_text="کد دیسپاچینگ باید یکتا باشد!",
                        ok_text="باشه",
                        parent=self,
                        icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    )
                    dlg.exec_()
                    self.table.load_table()
                    return

            # بررسی یکتایی نام مدار
            if column_name == "Circuit_Name" and new_value:
                existing_names = self.db.fetch_all(
                    "SELECT Circuit_Name FROM circuits WHERE Circuit_Name != ? AND id != ?",
                    (new_value, circuit_id)
                )
                if existing_names and new_value in [name[0] for name in existing_names]:
                    dlg = CustomDialog_Flexible(
                        header_text="خطا",
                        main_text="نام مدار باید یکتا باشد!",
                        ok_text="باشه",
                        parent=self,
                        icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    )
                    dlg.exec_()
                    self.table.load_table()
                    return

            # به‌روزرسانی دیتابیس
            query = f"UPDATE circuits SET {column_name} = ? WHERE id = ?"
            self.db.execute_query(query, (new_value, circuit_id))
            logging.debug(f"Updated {column_name} to {new_value} for circuit id {circuit_id}")
            # به‌روزرسانی جدول
            item.setText(new_value)
        except Exception as e:
            logging.error(f"Error in save_cell_edit: {str(e)}")
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در ذخیره تغییرات: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()
            self.table.load_table()

    def generate_report(self):
        try:
            rows = self.db.fetch_all("""
                SELECT Dispatch_Code, Circuit_Name, Voltage, Bundle_Number, Circuit_length, Wire_Type, Insulator_Type, Operation_Year
                FROM circuits
            """)
            import pandas as pd
            from PyQt5.QtWidgets import QFileDialog
            df = pd.DataFrame(rows, columns=self.original_headers)
            default_name = "Circuit_Report.xlsx"
            file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره گزارش مدارها", default_name, "Excel Files (*.xlsx)")
            if not file_path:
                return
            if not file_path.endswith(".xlsx"):
                file_path += ".xlsx"
            df.to_excel(file_path, index=False)
            # Use top-level import for CustomDialog_Flexible
            dlg = CustomDialog_Flexible(header_text="موفقیت", main_text=f"گزارش با نام {file_path} ذخیره شد.", ok_text="باشه", cancel_text=None, parent=self)
            dlg.exec_()
        except Exception as e:
            logging.error(f"Error in generate_report: {str(e)}")
            # Use top-level import for CustomDialog_Flexible
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در تولید گزارش: {str(e)}", ok_text="باشه", cancel_text=None, parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical)))
            dlg.exec_()

    def import_from_excel(self):
        try:
            import re
            file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل اکسل", "", "Excel Files (*.xlsx *.xls)")
            if not file_path:
                return
            df = pd.read_excel(file_path)
            expected_columns = self.original_headers
            if not all(col in df.columns for col in expected_columns):
                # ساخت متن خطا با فرمت بهتر
                error_text = "ساختار فایل اکسل نادرست است!\n\nستون‌های مورد انتظار:\n"
                # تقسیم ستون‌ها به خطوط جداگانه برای خوانایی بهتر
                columns_text = "\n".join([f"• {col}" for col in expected_columns])
                error_text += columns_text
                
                dlg = CustomDialog_Flexible(
                    header_text="خطا", 
                    main_text=error_text, 
                    ok_text="باشه", 
                    cancel_text=None, 
                    parent=self, 
                    icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical))
                )
                dlg.exec_()
                return

            self.import_cancelled = False
            existing_codes = self.db.fetch_all("SELECT Dispatch_Code FROM circuits")
            existing_code_set = {row[0] for row in existing_codes if row[0]}

            duplicate_names = []
            invalid_rows = []
            valid_rows = []
            seen_codes = set()
            for index, row in df.iterrows():
                dispatch_code = str(row["کد دیسپاچینگ"]).strip() if pd.notna(row["کد دیسپاچینگ"]) else ""
                circuit_name = str(row["نام مدار"]).strip() if pd.notna(row["نام مدار"]) else ""
                # سطر نامعتبر: کد دیسپاچینگ یا نام مدار خالی
                if not dispatch_code or not circuit_name:
                    invalid_rows.append(f"سطر {index+1}: کد دیسپاچینگ یا نام مدار خالی است")
                    continue
                # تکراری در دیتابیس یا فایل
                if dispatch_code in existing_code_set or dispatch_code in seen_codes:
                    duplicate_names.append(circuit_name)
                    continue
                seen_codes.add(dispatch_code)
                valid_rows.append(row)

            error_messages = []
            if duplicate_names:
                summarized = '\n'.join(sorted(set(duplicate_names)))
                error_messages.append(f"نام مدار تکراری ({len(duplicate_names)} مورد):\n{summarized}")
            if invalid_rows:
                summarized = '\n'.join(invalid_rows[:10])
                more = f"\n... و {len(invalid_rows)-10} سطر دیگر" if len(invalid_rows) > 10 else ""
                error_messages.append(f"سطرهای نامعتبر ({len(invalid_rows)} مورد):\n{summarized}{more}")
            if error_messages:
                error_text = "\n\n".join(error_messages)
                error_text += f"\n\nاز {len(df)} ردیف، فقط {len(valid_rows)} ردیف قابل وارد کردن است."
                dlg = CustomDialog_Flexible(
                    header_text="خطاهای یافت شده",
                    main_text=error_text,
                    ok_text="بله",
                    cancel_text="خیر",
                    question_text="آیا می‌خواهید مدارهای معتبر را وارد کنید؟",
                    parent=self
                )
                dlg.adjustSize()
                if dlg.exec_() != dlg.Accepted:
                    return
            if not valid_rows:
                dlg = CustomDialog_Flexible(header_text="هشدار", main_text="هیچ مدار معتبری برای وارد کردن یافت نشد.", ok_text="باشه", cancel_text=None, parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning)))
                dlg.exec_()
                return
            inserted_count = 0
            progress = CustomDialog_Progress(header_text="در حال وارد کردن اطلاعات مدارها...", cancel_text="لغو عملیات", parent=self)
            progress.set_maximum(len(valid_rows))
            progress.set_progress(0)
            progress.set_text(f"0 از {len(valid_rows)}")
            progress.show()
            QApplication.processEvents()
            def cancel():
                self.import_cancelled = True
            progress.cancel_btn.clicked.connect(cancel)
            for i, row in enumerate(valid_rows):
                QApplication.processEvents()
                if self.import_cancelled:
                    break
                progress.set_progress(i + 1)
                progress.set_text(f"{i+1} از {len(valid_rows)}")
                dispatch_code = str(row["کد دیسپاچینگ"]) if pd.notna(row["کد دیسپاچینگ"]) else ""
                self.db.execute_query(
                    """
                    INSERT INTO circuits (Circuit_Code, Circuit_Name, Voltage, Dispatch_Code, Bundle_Number,
                                         Circuit_length, Wire_Type, Insulator_Type, Operation_Year)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        dispatch_code, str(row["نام مدار"]) if pd.notna(row["نام مدار"]) else "",
                        str(row["ولتاژ"]) if pd.notna(row["ولتاژ"]) else "",
                        dispatch_code, str(row["تعداد باندل"]) if pd.notna(row["تعداد باندل"]) else "",
                        str(row["طول مدار (کیلومتر)"]) if pd.notna(row["طول مدار (کیلومتر)"]) else "",
                        str(row["نوع سیم"]) if pd.notna(row["نوع سیم"]) else "",
                        str(row["نوع مقره"]) if pd.notna(row["نوع مقره"]) else "",
                        str(row["سال سیم کشی"]) if pd.notna(row["سال سیم کشی"]) else ""
                    )
                )
                inserted_count += 1
            progress.accept()
            self.load_table()
            dlg = CustomDialog_Flexible(header_text="موفقیت", main_text=f"{inserted_count} مدار با موفقیت وارد شد.", ok_text="باشه", parent=self)
            dlg.exec_()
        except Exception as e:
            logging.error(f"Error in import_from_excel: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در وارد کردن اطلاعات از اکسل: {str(e)}")
