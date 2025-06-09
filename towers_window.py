from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QToolBar, QAction, QLineEdit, QLabel, QMessageBox, QStyle, QDialog, QFormLayout, QPushButton, QFileDialog, QHeaderView, QSizePolicy, QMenu, QApplication, QSpacerItem, QComboBox, QGroupBox, QScrollArea
from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QFont, QIcon
from database import Database
import csv
import re
import pandas as pd
import logging
import traceback

# تنظیم لاگ برای دیباگ
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# -----------------------------------------------
# Filter Popover: A small widget for column-specific filtering
# -----------------------------------------------
class FilterPopover(QWidget):
    def __init__(self, parent, column_index, column_name, current_filter, on_filter_changed):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)
        self.column_index = column_index
        self.column_name = column_name
        self.on_filter_changed = on_filter_changed
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 4px;")

        # Filter input
        self.filter_input = QLineEdit()
        self.filter_input.setFont(QFont("Vazir", 10))
        self.filter_input.setPlaceholderText(f"فیلتر {column_name}")
        self.filter_input.setStyleSheet("padding: 3px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.filter_input.setFixedWidth(150)
        self.filter_input.setText(current_filter or "")
        self.filter_input.textChanged.connect(self.apply_filter)
        self.layout().addWidget(self.filter_input)

        # Adjust size
        self.adjustSize()

    def apply_filter(self):
        try:
            filter_text = self.filter_input.text().strip()
            logging.debug(f"Applying filter for column {self.column_index}: {filter_text}")
            self.on_filter_changed(self.column_index, filter_text)
        except Exception as e:
            logging.error(f"Error in apply_filter: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در اعمال فیلتر: {str(e)}")

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.close()

# -----------------------------------------------
# Input Dialog: A dialog for adding or editing tower information
# -----------------------------------------------
class TowersInputDialog(QDialog):
    def __init__(self, parent=None, tower_data=None, is_edit=False):
        super().__init__(parent)
        self.setWindowTitle("افزودن دکل" if not is_edit else "ویرایش دکل")
        self.setLayoutDirection(Qt.RightToLeft)
        self.is_edit = is_edit
        self.current_id = tower_data.get('id') if tower_data else None
        self.db = Database()

        # فونت اصلی
        self.font = QFont("Vazir", 12)

        # چیدمان اصلی با اسکرول
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)
        self.scroll.setWidget(self.content_widget)
        self.scroll_layout = QVBoxLayout(self)
        self.scroll_layout.addWidget(self.scroll)

        # سکشن اطلاعات پایه
        self.section1 = QGroupBox("اطلاعات پایه")
        self.section1.setFont(self.font)
        self.section1_layout = QVBoxLayout()
        self.section1_layout.setContentsMargins(20, 10, 20, 10)
        self.section1_layout.setSpacing(15)
        self.section1.setLayout(self.section1_layout)

        # عرض ثابت برای ویجت‌ها
        dialog_width = 800
        label_width = 100  # عرض ثابت برای لیبل‌ها (برای ترازبندی)
        widget_width = 4*(dialog_width - 2 * label_width - 3 * 20) // 10  # حدود 260 پیکسل برای هر QLineEdit
        combo_width = 2 * widget_width  # حدود 520 پیکسل برای QComboBox

        # ردیف اول: فقط نام خط
        self.line_name = QComboBox()
        self.line_name.setFont(self.font)
        self.line_name.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.line_name.setFixedWidth(combo_width)
        row1 = QHBoxLayout()
        label1 = QLabel("نام خط:", font=self.font)
        label1.setFixedWidth(label_width)  # تنظیم عرض ثابت برای لیبل
        row1.addWidget(label1)
        row1.addWidget(self.line_name)
        row1.addStretch()
        self.section1_layout.addLayout(row1)

        # ردیف دوم: شماره دکل و ساختار دکل
        self.tower_number = QLineEdit()
        self.tower_number.setFont(self.font)
        self.tower_number.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.tower_number.setFixedWidth(widget_width)
        self.tower_structure = QLineEdit()
        self.tower_structure.setFont(self.font)
        self.tower_structure.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.tower_structure.setFixedWidth(widget_width)
        row2 = QHBoxLayout()
        label2_1 = QLabel("شماره دکل:", font=self.font)
        label2_1.setFixedWidth(label_width)  # تنظیم عرض ثابت برای لیبل
        row2.addWidget(label2_1)
        row2.addWidget(self.tower_number)
        row2.addSpacing(20)  # فاصله بین دو ویجت
        label2_2 = QLabel("ساختار دکل:", font=self.font)
        label2_2.setFixedWidth(label_width)  # تنظیم عرض ثابت برای لیبل
        row2.addWidget(label2_2)
        row2.addWidget(self.tower_structure)
        row2.addStretch()  # برای اطمینان از ترازبندی راست
        self.section1_layout.addLayout(row2)

        # ردیف سوم: نوع پایه و نوع دکل
        self.base_type = QLineEdit()
        self.base_type.setFont(self.font)
        self.base_type.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.base_type.setFixedWidth(widget_width)
        self.tower_type = QLineEdit()
        self.tower_type.setFont(self.font)
        self.tower_type.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.tower_type.setFixedWidth(widget_width)
        row3 = QHBoxLayout()
        label3_1 = QLabel("نوع پایه:", font=self.font)
        label3_1.setFixedWidth(label_width)  # تنظیم عرض ثابت برای لیبل
        row3.addWidget(label3_1)
        row3.addWidget(self.base_type)
        row3.addSpacing(20)  # فاصله بین دو ویجت
        label3_2 = QLabel("نوع دکل:", font=self.font)
        label3_2.setFixedWidth(label_width)  # تنظیم عرض ثابت برای لیبل
        row3.addWidget(label3_2)
        row3.addWidget(self.tower_type)
        row3.addStretch()  # برای اطمینان از ترازبندی راست
        self.section1_layout.addLayout(row3)

        self.main_layout.addWidget(self.section1)

        # سکشن ارتفاع سرقالب‌ها
        self.section2 = QGroupBox("ارتفاع سرقالب‌ها")
        self.section2.setFont(self.font)
        self.section2_layout = QVBoxLayout()
        self.section2_layout.setContentsMargins(10, 10, 10, 10)
        self.section2_layout.setSpacing(8)
        self.section2.setLayout(self.section2_layout)

        # ردیف اول: پایه A و پایه B
        self.height_leg_a = QLineEdit()
        self.height_leg_a.setFont(self.font)
        self.height_leg_a.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.height_leg_b = QLineEdit()
        self.height_leg_b.setFont(self.font)
        self.height_leg_b.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("پایه A:", font=self.font))
        row4.addWidget(self.height_leg_a)
        row4.addWidget(QLabel("سانتی‌متر", font=self.font))  # اضافه کردن لیبل سانتی‌متر
        row4.addSpacing(20)
        row4.addWidget(QLabel("پایه B:", font=self.font))
        row4.addWidget(self.height_leg_b)
        row4.addWidget(QLabel("سانتی‌متر", font=self.font))  # اضافه کردن لیبل سانتی‌متر
        self.section2_layout.addLayout(row4)

        # ردیف دوم: پایه C و پایه D
        self.height_leg_c = QLineEdit()
        self.height_leg_c.setFont(self.font)
        self.height_leg_c.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.height_leg_d = QLineEdit()
        self.height_leg_d.setFont(self.font)
        self.height_leg_d.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        row5 = QHBoxLayout()
        row5.addWidget(QLabel("پایه C:", font=self.font))
        row5.addWidget(self.height_leg_c)
        row5.addWidget(QLabel("سانتی‌متر", font=self.font))  # اضافه کردن لیبل سانتی‌متر
        row5.addSpacing(20)
        row5.addWidget(QLabel("پایه D:", font=self.font))
        row5.addWidget(self.height_leg_d)
        row5.addWidget(QLabel("سانتی‌متر", font=self.font))  # اضافه کردن لیبل سانتی‌متر
        self.section2_layout.addLayout(row5)

        self.main_layout.addWidget(self.section2)

        # سکشن نوع مقره‌ها
        self.section3 = QGroupBox("نوع مقره‌ها")
        self.section3.setFont(self.font)
        self.section3_layout = QVBoxLayout()
        self.section3_layout.setContentsMargins(10, 10, 10, 10)
        self.section3_layout.setSpacing(8)
        self.section3.setLayout(self.section3_layout)

        # ردیف اول: نوع مقره R مدار اول (راست) و R مدار دوم (چپ)
        self.insulator_type_c1_r = QComboBox()
        self.insulator_type_c1_r.setFont(self.font)
        self.insulator_type_c1_r.addItems(["", "سرامیکی", "شیشه‌ای", "سیلیکونی"])
        self.insulator_type_c1_r.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.insulator_type_c1_r.setFixedWidth(widget_width)
        self.insulator_type_c2_r = QComboBox()
        self.insulator_type_c2_r.setFont(self.font)
        self.insulator_type_c2_r.addItems(["", "سرامیکی", "شیشه‌ای", "سیلیکونی"])
        self.insulator_type_c2_r.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.insulator_type_c2_r.setFixedWidth(widget_width)
        row6 = QHBoxLayout()
        row6.addWidget(QLabel("نوع مقره R مدار اول:", font=self.font))
        row6.addWidget(self.insulator_type_c1_r)
        row6.addSpacing(20)
        row6.addWidget(QLabel("نوع مقره R مدار دوم:", font=self.font))
        row6.addWidget(self.insulator_type_c2_r)
        self.section3_layout.addLayout(row6)

        # ردیف دوم: نوع مقره S مدار اول (راست) و S مدار دوم (چپ)
        self.insulator_type_c1_s = QComboBox()
        self.insulator_type_c1_s.setFont(self.font)
        self.insulator_type_c1_s.addItems(["", "سرامیکی", "شیشه‌ای", "سیلیکونی"])
        self.insulator_type_c1_s.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.insulator_type_c1_s.setFixedWidth(widget_width)
        self.insulator_type_c2_s = QComboBox()
        self.insulator_type_c2_s.setFont(self.font)
        self.insulator_type_c2_s.addItems(["", "سرامیکی", "شیشه‌ای", "سیلیکونی"])
        self.insulator_type_c2_s.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.insulator_type_c2_s.setFixedWidth(widget_width)
        row7 = QHBoxLayout()
        row7.addWidget(QLabel("نوع مقره S مدار اول:", font=self.font))
        row7.addWidget(self.insulator_type_c1_s)
        row7.addSpacing(20)
        row7.addWidget(QLabel("نوع مقره S مدار دوم:", font=self.font))
        row7.addWidget(self.insulator_type_c2_s)
        self.section3_layout.addLayout(row7)

        # ردیف سوم: نوع مقره T مدار اول (راست) و T مدار دوم (چپ)
        self.insulator_type_c1_t = QComboBox()
        self.insulator_type_c1_t.setFont(self.font)
        self.insulator_type_c1_t.addItems(["", "سرامیکی", "شیشه‌ای", "سیلیکونی"])
        self.insulator_type_c1_t.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.insulator_type_c1_t.setFixedWidth(widget_width)
        self.insulator_type_c2_t = QComboBox()
        self.insulator_type_c2_t.setFont(self.font)
        self.insulator_type_c2_t.addItems(["", "سرامیکی", "شیشه‌ای", "سیلیکونی"])
        self.insulator_type_c2_t.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.insulator_type_c2_t.setFixedWidth(widget_width)
        row8 = QHBoxLayout()
        row8.addWidget(QLabel("نوع مقره T مدار اول:", font=self.font))
        row8.addWidget(self.insulator_type_c1_t)
        row8.addSpacing(20)
        row8.addWidget(QLabel("نوع مقره T مدار دوم:", font=self.font))
        row8.addWidget(self.insulator_type_c2_t)
        self.section3_layout.addLayout(row8)

        self.main_layout.addWidget(self.section3)

        # سکشن تعداد مقره‌ها
        self.section4 = QGroupBox("تعداد مقره‌ها")
        self.section4.setFont(self.font)
        self.section4_layout = QVBoxLayout()
        self.section4_layout.setContentsMargins(10, 10, 10, 10)
        self.section4_layout.setSpacing(8)
        self.section4.setLayout(self.section4_layout)

        # ردیف اول: تعداد R مدار اول (راست) و R مدار دوم (چپ)
        self.insulator_count_c1_r = QLineEdit()
        self.insulator_count_c1_r.setFont(self.font)
        self.insulator_count_c1_r.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.insulator_count_c2_r = QLineEdit()
        self.insulator_count_c2_r.setFont(self.font)
        self.insulator_count_c2_r.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        row9 = QHBoxLayout()
        row9.addWidget(QLabel("تعداد R مدار اول:", font=self.font))
        row9.addWidget(self.insulator_count_c1_r)
        row9.addSpacing(20)
        row9.addWidget(QLabel("تعداد R مدار دوم:", font=self.font))
        row9.addWidget(self.insulator_count_c2_r)
        self.section4_layout.addLayout(row9)

        # ردیف دوم: تعداد S مدار اول (راست) و S مدار دوم (چپ)
        self.insulator_count_c1_s = QLineEdit()
        self.insulator_count_c1_s.setFont(self.font)
        self.insulator_count_c1_s.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.insulator_count_c2_s = QLineEdit()
        self.insulator_count_c2_s.setFont(self.font)
        self.insulator_count_c2_s.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        row10 = QHBoxLayout()
        row10.addWidget(QLabel("تعداد S مدار اول:", font=self.font))
        row10.addWidget(self.insulator_count_c1_s)
        row10.addSpacing(20)
        row10.addWidget(QLabel("تعداد S مدار دوم:", font=self.font))
        row10.addWidget(self.insulator_count_c2_s)
        self.section4_layout.addLayout(row10)

        # ردیف سوم: تعداد T مدار اول (راست) و T مدار دوم (چپ)
        self.insulator_count_c1_t = QLineEdit()
        self.insulator_count_c1_t.setFont(self.font)
        self.insulator_count_c1_t.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.insulator_count_c2_t = QLineEdit()
        self.insulator_count_c2_t.setFont(self.font)
        self.insulator_count_c2_t.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        row11 = QHBoxLayout()
        row11.addWidget(QLabel("تعداد T مدار اول:", font=self.font))
        row11.addWidget(self.insulator_count_c1_t)
        row11.addSpacing(20)
        row11.addWidget(QLabel("تعداد T مدار دوم:", font=self.font))
        row11.addWidget(self.insulator_count_c2_t)
        self.section4_layout.addLayout(row11)

        self.main_layout.addWidget(self.section4)

        # سکشن موقعیت جغرافیایی
        self.section5 = QGroupBox("موقعیت جغرافیایی")
        self.section5.setFont(self.font)
        self.section5_layout = QVBoxLayout()
        self.section5_layout.setContentsMargins(10, 10, 10, 10)
        self.section5_layout.setSpacing(8)
        self.section5.setLayout(self.section5_layout)

        # ردیف اول: طول و عرض جغرافیایی
        self.longitude = QLineEdit()
        self.longitude.setFont(self.font)
        self.longitude.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.longitude.setPlaceholderText("مثال: 47.235")
        self.latitude = QLineEdit()
        self.latitude.setFont(self.font)
        self.latitude.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.latitude.setPlaceholderText("مثال: 34.567")
        row_coords = QHBoxLayout()
        row_coords.addWidget(QLabel("طول جغرافیایی:", font=self.font))
        row_coords.addWidget(self.longitude)
        row_coords.addSpacing(20)
        row_coords.addWidget(QLabel("عرض جغرافیایی:", font=self.font))
        row_coords.addWidget(self.latitude)
        self.section5_layout.addLayout(row_coords)

        self.main_layout.addWidget(self.section5)

        # دکمه‌ها
        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("ذخیره")
        self.save_button.setFont(QFont("Vazir", 14))  # افزایش اندازه فونت به 14
        self.save_button.setStyleSheet("padding: 5px; background-color: #4CAF50; color: white; border-radius: 6px;")  # افزایش padding و border-radius
        self.save_button.setMinimumSize(120, 40)  # تنظیم حداقل عرض و ارتفاع دکمه
        self.cancel_button = QPushButton("لغو")
        self.cancel_button.setFont(QFont("Vazir", 14))  # افزایش اندازه فونت به 14
        self.cancel_button.setStyleSheet("padding: 5px; background-color: #f44336; color: white; border-radius: 6px;")  # افزایش padding و border-radius
        self.cancel_button.setMinimumSize(120, 40)  # تنظیم حداقل عرض و ارتفاع دکمه
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)
        self.main_layout.addLayout(self.button_layout)

        # پر کردن ComboBox نام خط
        self.load_line_names()

        # پر کردن فیلدها در حالت ویرایش
        if tower_data:
            index = self.line_name.findText(str(tower_data.get('line_name', '')))
            if index >= 0:
                self.line_name.setCurrentIndex(index)
            self.tower_number.setText(str(tower_data.get('tower_number', '')))
            self.tower_structure.setText(str(tower_data.get('tower_structure', '')))
            self.tower_type.setText(str(tower_data.get('tower_type', '')))
            self.base_type.setText(str(tower_data.get('base_type', '')))
            self.height_leg_a.setText(str(tower_data.get('height_leg_a', '')))
            self.height_leg_b.setText(str(tower_data.get('height_leg_b', '')))
            self.height_leg_c.setText(str(tower_data.get('height_leg_c', '')))
            self.height_leg_d.setText(str(tower_data.get('height_leg_d', '')))
            self.insulator_type_c1_r.setCurrentText(str(tower_data.get('insulator_type_c1_r', '')))
            self.insulator_type_c1_s.setCurrentText(str(tower_data.get('insulator_type_c1_s', '')))
            self.insulator_type_c1_t.setCurrentText(str(tower_data.get('insulator_type_c1_t', '')))
            self.insulator_type_c2_r.setCurrentText(str(tower_data.get('insulator_type_c2_r', '')))
            self.insulator_type_c2_s.setCurrentText(str(tower_data.get('insulator_type_c2_s', '')))
            self.insulator_type_c2_t.setCurrentText(str(tower_data.get('insulator_type_c2_t', '')))
            self.insulator_count_c1_r.setText(str(tower_data.get('insulator_count_c1_r', '')))
            self.insulator_count_c1_s.setText(str(tower_data.get('insulator_count_c1_s', '')))
            self.insulator_count_c1_t.setText(str(tower_data.get('insulator_count_c1_t', '')))
            self.insulator_count_c2_r.setText(str(tower_data.get('insulator_count_c2_r', '')))
            self.insulator_count_c2_s.setText(str(tower_data.get('insulator_count_c2_s', '')))
            self.insulator_count_c2_t.setText(str(tower_data.get('insulator_count_c2_t', '')))
            self.longitude.setText(str(tower_data.get('longitude', '')))
            self.latitude.setText(str(tower_data.get('latitude', '')))

        # تنظیم اندازه خودکار
        self.main_layout.addStretch()
        self.adjust_dialog_size()

        # اتصال سیگنال‌ها
        self.save_button.clicked.connect(self.save_tower)
        self.cancel_button.clicked.connect(self.reject)

    def adjust_dialog_size(self):
        """تنظیم خودکار اندازه دیالوگ بر اساس محتوای سکشن‌ها"""
        sections = [self.section1, self.section2, self.section3, self.section4, self.section5]
        total_height = 0

        # محاسبه ارتفاع سکشن‌ها
        for section in sections:
            total_height += self.calculate_section_height(section)

        # ارتفاع دکمه‌ها
        button_height = self.save_button.sizeHint().height() + 10

        # مجموع ارتفاع‌ها + فاصله‌ها
        total_height += (
            button_height +
            self.main_layout.spacing() * (len(sections) + 1) +  # فاصله بین سکشن‌ها و دکمه‌ها
            self.main_layout.contentsMargins().top() +
            self.main_layout.contentsMargins().bottom()
        )

        # تنظیم عرض ثابت
        dialog_width = 800

        # تنظیم اندازه دیالوگ
        self.setMinimumSize(dialog_width, min(total_height, 600))  # حداکثر ارتفاع 600
        self.resize(dialog_width, min(total_height, 600))

    def calculate_section_height(self, section):
        """محاسبه ارتفاع یک سکشن بر اساس محتوای آن"""
        layout = section.layout()
        total_height = layout.contentsMargins().top() + layout.contentsMargins().bottom()

        # شمارش ردیف‌ها
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.layout():
                widget = item.layout().itemAt(1).widget()  # مثلاً QLineEdit یا QComboBox
                if widget:
                    total_height += widget.sizeHint().height()
            total_height += layout.spacing()

        # ارتفاع عنوان GroupBox
        total_height += section.fontMetrics().height() + 20

        return total_height

    def load_line_names(self):
        try:
            query = "SELECT line_name FROM lines"
            rows = self.db.fetch_all(query)
            self.line_name.addItem("")
            for row in rows:
                self.line_name.addItem(row[0])
        except Exception as e:
            logging.error(f"Error in load_line_names: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری نام خطوط: {str(e)}")

    def validate_inputs(self):
        if not self.line_name.currentText():
            return False, "نام خط اجباری است!"
        if not self.tower_number.text():
            return False, "شماره دکل اجباری است!"
        if self.height_leg_a.text() and not re.match(r"^\d*\.?\d*$", self.height_leg_a.text()):
            return False, "ارتفاع پایه A باید عدد باشد!"
        if self.height_leg_b.text() and not re.match(r"^\d*\.?\d*$", self.height_leg_b.text()):
            return False, "ارتفاع پایه B باید عدد باشد!"
        if self.height_leg_c.text() and not re.match(r"^\d*\.?\d*$", self.height_leg_c.text()):
            return False, "ارتفاع پایه C باید عدد باشد!"
        if self.height_leg_d.text() and not re.match(r"^\d*\.?\d*$", self.height_leg_d.text()):
            return False, "ارتفاع پایه D باید عدد باشد!"
        if self.insulator_count_c1_r.text() and not self.insulator_count_c1_r.text().isdigit():
            return False, "تعداد مقره R مدار اول باید عدد باشد!"
        if self.insulator_count_c1_s.text() and not self.insulator_count_c1_s.text().isdigit():
            return False, "تعداد مقره S مدار اول باید عدد باشد!"
        if self.insulator_count_c1_t.text() and not self.insulator_count_c1_t.text().isdigit():
            return False, "تعداد مقره T مدار اول باید عدد باشد!"
        if self.insulator_count_c2_r.text() and not self.insulator_count_c2_r.text().isdigit():
            return False, "تعداد مقره R مدار دوم باید عدد باشد!"
        if self.insulator_count_c2_s.text() and not self.insulator_count_c2_s.text().isdigit():
            return False, "تعداد مقره S مدار دوم باید عدد باشد!"
        if self.insulator_count_c2_t.text() and not self.insulator_count_c2_t.text().isdigit():
            return False, "تعداد مقره T مدار دوم باید عدد باشد!"
        if self.longitude.text() and not re.match(r"^-?\d+(\.\d+)?$", self.longitude.text()):
            return False, "طول جغرافیایی نامعتبر است!"
        if self.latitude.text() and not re.match(r"^-?\d+(\.\d+)?$", self.latitude.text()):
            return False, "عرض جغرافیایی نامعتبر است!"
        existing_towers = self.db.fetch_all(
            "SELECT tower_number FROM towers WHERE line_name = ? AND id != ?",
            (self.line_name.currentText(), self.current_id or -1)
        )
        if self.tower_number.text() in [tower[0] for tower in existing_towers]:
            return False, "شماره دکل برای این خط باید یکتا باشد!"
        return True, ""

    def save_tower(self):
        is_valid, error_msg = self.validate_inputs()
        if not is_valid:
            QMessageBox.warning(self, "خطا", error_msg)
            return

        def format_number(value):
            if value:
                try:
                    num = float(value)
                    return str(int(num)) if num.is_integer() else str(num).rstrip('0').rstrip('.')
                except ValueError:
                    return value
            return value

        self.tower_data = {
            'line_name': self.line_name.currentText(),
            'tower_number': self.tower_number.text(),
            'tower_structure': self.tower_structure.text(),
            'tower_type': self.tower_type.text(),
            'base_type': self.base_type.text(),
            'height_leg_a': format_number(self.height_leg_a.text()),
            'height_leg_b': format_number(self.height_leg_b.text()),
            'height_leg_c': format_number(self.height_leg_c.text()),
            'height_leg_d': format_number(self.height_leg_d.text()),
            'insulator_type_c1_r': self.insulator_type_c1_r.currentText(),
            'insulator_type_c1_s': self.insulator_type_c1_s.currentText(),
            'insulator_type_c1_t': self.insulator_type_c1_t.currentText(),
            'insulator_type_c2_r': self.insulator_type_c2_r.currentText(),
            'insulator_type_c2_s': self.insulator_type_c2_s.currentText(),
            'insulator_type_c2_t': self.insulator_type_c2_t.currentText(),
            'insulator_count_c1_r': self.insulator_count_c1_r.text(),
            'insulator_count_c1_s': self.insulator_count_c1_s.text(),
            'insulator_count_c1_t': self.insulator_count_c1_t.text(),
            'insulator_count_c2_r': self.insulator_count_c2_r.text(),
            'insulator_count_c2_s': self.insulator_count_c2_s.text(),
            'insulator_count_c2_t': self.insulator_count_c2_t.text(),
            'longitude': self.longitude.text(),
            'latitude': self.latitude.text(),
            'id': self.current_id
        }
        self.accept()

# -----------------------------------------------
# Towers Window: Displays and manages tower information with column-specific filtering
# -----------------------------------------------
class TowersWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Column filters
        self.column_filters = {}
        self.original_headers = [
            "نام خط", "شماره دکل", "ساختار دکل", "نوع دکل", "نوع پایه",
            "ارتفاع پایه A", "ارتفاع پایه B", "ارتفاع پایه C", "ارتفاع پایه D",
            "نوع مقره R مدار اول", "نوع مقره S مدار اول", "نوع مقره T مدار اول",
            "نوع مقره R مدار دوم", "نوع مقره S مدار دوم", "نوع مقره T مدار دوم",
            "تعداد R مدار اول", "تعداد S مدار اول", "تعداد T مدار اول",
            "تعداد R مدار دوم", "تعداد S مدار دوم", "تعداد T مدار دوم",
            "طول جغرافیایی", "عرض جغرافیایی"
        ]
        self.column_names = [
            "line_name", "tower_number", "tower_structure", "tower_type", "base_type",
            "height_leg_a", "height_leg_b", "height_leg_c", "height_leg_d",
            "insulator_type_c1_r", "insulator_type_c1_s", "insulator_type_c1_t",
            "insulator_type_c2_r", "insulator_type_c2_s", "insulator_type_c2_t",
            "insulator_count_c1_r", "insulator_count_c1_s", "insulator_count_c1_t",
            "insulator_count_c2_r", "insulator_count_c2_s", "insulator_count_c2_t",
            "longitude", "latitude"
        ]

        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setFont(QFont("Vazir", 18))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.setStyleSheet("""
            QToolBar { 
                background-color: #e0e0e0; 
                padding: 5px; 
                spacing: 5px; 
                border-radius: 8px;
            }
            QToolButton { 
                margin: 2px; 
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

        self.add_action = QAction(QIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder)), "افزودن دکل جدید", self)
        self.delete_action = QAction(QIcon(self.style().standardIcon(QStyle.SP_TrashIcon)), "حذف", self)
        self.edit_action = QAction(QIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView)), "ویرایش", self)
        self.import_excel_action = QAction(QIcon(self.style().standardIcon(QStyle.SP_FileDialogStart)), "ورود اطلاعات از اکسل", self)
        self.report_action = QAction(QIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView)), "خروجی گرفتن", self)
        self.back_action = QAction(QIcon(self.style().standardIcon(QStyle.SP_ArrowBack)), "برگشت", self)

        self.toolbar.addAction(self.add_action)
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

        self.add_action.triggered.connect(self.add_tower)
        self.delete_action.triggered.connect(self.delete_tower)
        self.edit_action.triggered.connect(self.edit_tower)
        self.import_excel_action.triggered.connect(self.import_from_excel)
        self.report_action.triggered.connect(self.generate_report)
        self.back_action.triggered.connect(self.close)

        # Filter
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
                width: 300px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
        """)
        self.filter_input.setFixedWidth(300)
        self.filter_input.textChanged.connect(self.filter_table)
        self.filter_input.mousePressEvent = self.clear_placeholder
        self.filter_layout.addWidget(QLabel("فیلتر:"))
        self.filter_layout.addWidget(self.filter_input)
        self.filter_layout.addStretch()
        self.layout.addLayout(self.filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(23)
        self.table.setHorizontalHeaderLabels(self.original_headers)
        self.table.setFont(QFont("Vazir", 12))
        self.table.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #ccc; 
                background-color: white; 
            }
        """)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.AnyKeyPressed | QTableWidget.SelectedClicked)
        self.table.cellClicked.connect(self.load_row_data)
        self.table.cellChanged.connect(self.save_cell)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.horizontalHeader().sectionClicked.connect(self.show_filter_popover)
        self.layout.addWidget(self.table)

        self.load_table()

    def clear_placeholder(self, event):
        if not self.filter_input.text() or self.filter_input.text() == self.filter_input.placeholderText():
            self.filter_input.clear()
        super(QLineEdit, self.filter_input).mousePressEvent(event)

    def show_filter_popover(self, logical_index):
        try:
            header = self.table.horizontalHeader()
            viewport = self.table.viewport()
            visual_index = header.visualIndex(logical_index)
            section_pos = header.sectionViewportPosition(visual_index)
            section_width = header.sectionSize(visual_index)
            header_height = header.height()
            h_scroll = self.table.horizontalScrollBar().value()
            v_scroll = self.table.verticalScrollBar().value()
            adjusted_pos = section_pos - h_scroll
            total_width = viewport.width()
            if adjusted_pos < 0:
                adjusted_pos = 0
            elif adjusted_pos + section_width > total_width:
                adjusted_pos = total_width - section_width
            local_pos = QPoint(adjusted_pos, header_height - v_scroll)
            global_pos = self.table.mapToGlobal(local_pos)
            current_filter = self.column_filters.get(self.column_names[logical_index], "")
            popover = FilterPopover(
                self.table,
                logical_index,
                self.original_headers[logical_index],
                current_filter,
                self.update_column_filter
            )
            popover.move(global_pos)
            popover.show()
            popover.filter_input.setFocus()
            logging.debug(f"Filter popover for column {logical_index} at global_pos {global_pos}")
        except Exception as e:
            logging.error(f"Error in show_filter_popover: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در نمایش فیلتر: {str(e)}")

    def update_column_filter(self, column_index, filter_text):
        try:
            column_name = self.column_names[column_index]
            logging.debug(f"Updating filter for column {column_name}: {filter_text}")
            if filter_text:
                self.column_filters[column_name] = filter_text
            elif column_name in self.column_filters:
                del self.column_filters[column_name]
            new_headers = self.original_headers.copy()
            for i, name in enumerate(self.column_names):
                if name in self.column_filters and self.column_filters[name]:
                    new_headers[i] = f"{self.original_headers[i]} ▼"
                else:
                    new_headers[i] = self.original_headers[i]
            self.table.setHorizontalHeaderLabels(new_headers)
            self.load_table()
        except Exception as e:
            logging.error(f"Error in update_column_filter: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در به‌روزرسانی فیلتر: {str(e)}")

    def load_table(self, global_filter=None):
        try:
            self.table.blockSignals(True)
            query = """
                SELECT id, line_name, tower_number, tower_structure, tower_type, base_type,
                       height_leg_a, height_leg_b, height_leg_c, height_leg_d,
                       insulator_type_c1_r, insulator_type_c1_s, insulator_type_c1_t,
                       insulator_type_c2_r, insulator_type_c2_s, insulator_type_c2_t,
                       insulator_count_c1_r, insulator_count_c1_s, insulator_count_c1_t,
                       insulator_count_c2_r, insulator_count_c2_s, insulator_count_c2_t,
                       longitude, latitude
                FROM towers
            """
            params = []
            conditions = []
            if global_filter:
                conditions.append("""
                    (line_name LIKE ? OR tower_number LIKE ? OR tower_structure LIKE ? 
                    OR tower_type LIKE ? OR base_type LIKE ? OR height_leg_a LIKE ? 
                    OR height_leg_b LIKE ? OR height_leg_c LIKE ? OR height_leg_d LIKE ?
                    OR insulator_type_c1_r LIKE ? OR insulator_type_c1_s LIKE ? 
                    OR insulator_type_c1_t LIKE ? OR insulator_type_c2_r LIKE ? 
                    OR insulator_type_c2_s LIKE ? OR insulator_type_c2_t LIKE ?
                    OR insulator_count_c1_r LIKE ? OR insulator_count_c1_s LIKE ? 
                    OR insulator_count_c1_t LIKE ? OR insulator_count_c2_r LIKE ? 
                    OR insulator_count_c2_s LIKE ? OR insulator_count_c2_t LIKE ?)
                """)
                params.extend([f"%{global_filter}%"] * 21)
            for column, filter_text in self.column_filters.items():
                if filter_text:
                    conditions.append(f"{column} LIKE ?")
                    params.append(f"%{filter_text}%")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            logging.debug(f"Executing query: {query} with params: {params}")
            rows = self.db.fetch_all(query, tuple(params))
            self.table.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                for col_idx, data in enumerate(row_data[1:], start=0):
                    data = str(data) if data is not None else ""
                    if col_idx in [5, 6, 7, 8]:
                        try:
                            num = float(data)
                            data = str(int(num)) if num.is_integer() else str(num).rstrip('0').rstrip('.')
                        except (ValueError, TypeError):
                            pass
                    item = QTableWidgetItem(data)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_idx, col_idx, item)
                self.table.item(row_idx, 0).setData(Qt.UserRole, row_data[0])
            self.table.resizeColumnsToContents()
            for col in range(self.table.columnCount()):
                if self.table.columnWidth(col) < 100:
                    self.table.setColumnWidth(col, 100)
            self.table.resizeRowsToContents()
            self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            logging.debug(f"Table loaded with {len(rows)} rows")
        except Exception as e:
            logging.error(f"Error in load_table: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری جدول: {str(e)}")
        finally:
            self.table.blockSignals(False)

    def filter_table(self):
        try:
            self.load_table(self.filter_input.text())
        except Exception as e:
            logging.error(f"Error in filter_table: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در فیلتر جدول: {str(e)}")

    def add_tower(self):
        dialog = TowersInputDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            tower_data = dialog.tower_data
            try:
                self.db.execute_query(
                    """
                    INSERT INTO towers (line_name, tower_number, tower_structure, tower_type, base_type,
                                        height_leg_a, height_leg_b, height_leg_c, height_leg_d,
                                        insulator_type_c1_r, insulator_type_c1_s, insulator_type_c1_t,
                                        insulator_type_c2_r, insulator_type_c2_s, insulator_type_c2_t,
                                        insulator_count_c1_r, insulator_count_c1_s, insulator_count_c1_t,
                                        insulator_count_c2_r, insulator_count_c2_s, insulator_count_c2_t)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tower_data['line_name'], tower_data['tower_number'], tower_data['tower_structure'],
                        tower_data['tower_type'], tower_data['base_type'], tower_data['height_leg_a'],
                        tower_data['height_leg_b'], tower_data['height_leg_c'], tower_data['height_leg_d'],
                        tower_data['insulator_type_c1_r'], tower_data['insulator_type_c1_s'],
                        tower_data['insulator_type_c1_t'], tower_data['insulator_type_c2_r'],
                        tower_data['insulator_type_c2_s'], tower_data['insulator_type_c2_t'],
                        tower_data['insulator_count_c1_r'], tower_data['insulator_count_c1_s'],
                        tower_data['insulator_count_c1_t'], tower_data['insulator_count_c2_r'],
                        tower_data['insulator_count_c2_s'], tower_data['insulator_count_c2_t'],
                        tower_data['longitude'], tower_data['latitude']
                    )
                )
                self.load_table()
                QMessageBox.information(self, "موفقیت", "دکل با موفقیت اضافه شد.")
            except Exception as e:
                logging.error(f"Error in add_tower: {str(e)}\n{traceback.format_exc()}")
                QMessageBox.critical(self, "خطا", f"خطا در افزودن دکل: {str(e)}")

    def edit_tower(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "خطا", "دکلی انتخاب نشده است!")
            return
        row = self.table.currentRow()
        tower_number = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
        line_name = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
        try:
            result = self.db.fetch_all("SELECT id FROM towers WHERE tower_number=? AND line_name=?", (tower_number, line_name))
            if not result:
                QMessageBox.critical(self, "خطا", "دکل موردنظر یافت نشد!")
                return
            current_id = result[0][0]
            tower_data = {
                'id': current_id,
                'line_name': line_name,
                'tower_number': tower_number,
                'tower_structure': self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                'tower_type': self.table.item(row, 3).text() if self.table.item(row, 3) else "",
                'base_type': self.table.item(row, 4).text() if self.table.item(row, 4) else "",
                'height_leg_a': self.table.item(row, 5).text() if self.table.item(row, 5) else "",
                'height_leg_b': self.table.item(row, 6).text() if self.table.item(row, 6) else "",
                'height_leg_c': self.table.item(row, 7).text() if self.table.item(row, 7) else "",
                'height_leg_d': self.table.item(row, 8).text() if self.table.item(row, 8) else "",
                'insulator_type_c1_r': self.table.item(row, 9).text() if self.table.item(row, 9) else "",
                'insulator_type_c1_s': self.table.item(row, 10).text() if self.table.item(row, 10) else "",
                'insulator_type_c1_t': self.table.item(row, 11).text() if self.table.item(row, 11) else "",
                'insulator_type_c2_r': self.table.item(row, 12).text() if self.table.item(row, 12) else "",
                'insulator_type_c2_s': self.table.item(row, 13).text() if self.table.item(row, 13) else "",
                'insulator_type_c2_t': self.table.item(row, 14).text() if self.table.item(row, 14) else "",
                'insulator_count_c1_r': self.table.item(row, 15).text() if self.table.item(row, 15) else "",
                'insulator_count_c1_s': self.table.item(row, 16).text() if self.table.item(row, 16) else "",
                'insulator_count_c1_t': self.table.item(row, 17).text() if self.table.item(row, 17) else "",
                'insulator_count_c2_r': self.table.item(row, 18).text() if self.table.item(row, 18) else "",
                'insulator_count_c2_s': self.table.item(row, 19).text() if self.table.item(row, 19) else "",
                'insulator_count_c2_t': self.table.item(row, 20).text() if self.table.item(row, 20) else ""
            }
            dialog = TowersInputDialog(self, tower_data, is_edit=True)
            if dialog.exec_() == QDialog.Accepted:
                tower_data = dialog.tower_data
                self.db.execute_query(
                    """
                    UPDATE towers SET line_name=?, tower_number=?, tower_structure=?, tower_type=?, 
                                      base_type=?, height_leg_a=?, height_leg_b=?, height_leg_c=?, 
                                      height_leg_d=?, insulator_type_c1_r=?, insulator_type_c1_s=?, 
                                      insulator_type_c1_t=?, insulator_type_c2_r=?, insulator_type_c2_s=?, 
                                      insulator_type_c2_t=?, insulator_count_c1_r=?, insulator_count_c1_s=?, 
                                      insulator_count_c1_t=?, insulator_count_c2_r=?, insulator_count_c2_s=?, 
                                      insulator_count_c2_t=?, longitude=?, latitude=?
                    WHERE id=?
                    """,
                    (
                        tower_data['line_name'], tower_data['tower_number'], tower_data['tower_structure'],
                        tower_data['tower_type'], tower_data['base_type'], tower_data['height_leg_a'],
                        tower_data['height_leg_b'], tower_data['height_leg_c'], tower_data['height_leg_d'],
                        tower_data['insulator_type_c1_r'], tower_data['insulator_type_c1_s'],
                        tower_data['insulator_type_c1_t'], tower_data['insulator_type_c2_r'],
                        tower_data['insulator_type_c2_s'], tower_data['insulator_type_c2_t'],
                        tower_data['insulator_count_c1_r'], tower_data['insulator_count_c1_s'],
                        tower_data['insulator_count_c1_t'], tower_data['insulator_count_c2_r'],
                        tower_data['insulator_count_c2_s'], tower_data['insulator_count_c2_t'],
                        tower_data['longitude'], tower_data['latitude'],
                        tower_data['id']
                    )
                )
                self.load_table()
                QMessageBox.information(self, "موفقیت", "دکل با موفقیت ویرایش شد.")
        except Exception as e:
            logging.error(f"Error in edit_tower: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در ویرایش دکل: {str(e)}")

    def delete_tower(self):
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()))
        if not selected_rows:
            QMessageBox.warning(self, "خطا", "دکلی انتخاب نشده است!")
            return
        row_count = len(selected_rows)
        msg = f"آیا از حذف {row_count} دکل مطمئن هستید؟"
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("تأیید حذف")
        msg_box.setText(msg)
        msg_box.setStandardButtons(QMessageBox.NoButton)
        yes_button = msg_box.addButton("بله", QMessageBox.YesRole)
        no_button = msg_box.addButton("خیر", QMessageBox.RejectRole)
        yes_button.setFont(QFont("Vazir", 12))
        no_button.setFont(QFont("Vazir", 12))
        msg_box.setDefaultButton(no_button)
        msg_box.setLayoutDirection(Qt.RightToLeft)
        msg_box.exec_()
        if msg_box.clickedButton() != yes_button:
            return
        try:
            for row in selected_rows:
                tower_number = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
                line_name = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
                self.db.execute_query("DELETE FROM towers WHERE tower_number=? AND line_name=?", (tower_number, line_name))
            self.load_table()
            QMessageBox.information(self, "موفقیت", f"{row_count} دکل با موفقیت حذف شد.")
        except Exception as e:
            logging.error(f"Error in delete_tower: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")

    def load_row_data(self):
        pass

    def generate_report(self):
        try:
            rows = self.db.fetch_all("""
                SELECT line_name, tower_number, tower_structure, tower_type, base_type,
                       height_leg_a, height_leg_b, height_leg_c, height_leg_d,
                       insulator_type_c1_r, insulator_type_c1_s, insulator_type_c1_t,
                       insulator_type_c2_r, insulator_type_c2_s, insulator_type_c2_t,
                       insulator_count_c1_r, insulator_count_c1_s, insulator_count_c1_t,
                       insulator_count_c2_r, insulator_count_c2_s, insulator_count_c2_t
                FROM towers
            """)
            with open("towers_report.csv", "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.original_headers)
                writer.writerows(rows)
            QMessageBox.information(self, "موفقیت", "گزارش با نام towers_report.csv ذخیره شد.")
        except Exception as e:
            logging.error(f"Error in generate_report: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در تولید گزارش: {str(e)}")

    def format_number(self, value):
        if pd.notna(value):
            try:
                num = float(value)
                return str(int(num)) if num.is_integer() else str(num).rstrip('0').rstrip('.')
            except (ValueError, TypeError):
                return str(value)
        return ""

    def import_from_excel(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل اکسل", "", "Excel Files (*.xlsx *.xls)")
            if not file_path:
                return
            df = pd.read_excel(file_path)
            expected_columns = self.original_headers
            if not all(col in df.columns for col in expected_columns):
                missing_cols = [col for col in expected_columns if col not in df.columns]
                QMessageBox.critical(self, "خطا", f"ستون‌های زیر در فایل اکسل یافت نشدند: {', '.join(missing_cols)}")
                return
            existing_towers = {(row[0], row[1]) for row in self.db.fetch_all("SELECT line_name, tower_number FROM towers") if row[0] and row[1]}
            valid_lines = {row[0] for row in self.db.fetch_all("SELECT line_name FROM lines") if row[0]}
            inserted_count = 0
            errors = []
            for index, row in df.iterrows():
                line_name = str(row["نام خط"]) if pd.notna(row["نام خط"]) else ""
                tower_number = str(row["شماره دکل"]) if pd.notna(row["شماره دکل"]) else ""
                if not line_name:
                    errors.append(f"ردیف {index + 2}: نام خط خالی است")
                    continue
                if not tower_number:
                    errors.append(f"ردیف {index + 2}: شماره دکل خالی است")
                    continue
                if line_name not in valid_lines:
                    errors.append(f"ردیف {index + 2}: نام خط '{line_name}' نامعتبر است")
                    continue
                if (line_name, tower_number) in existing_towers:
                    errors.append(f"ردیف {index + 2}: دکل '{tower_number}' برای خط '{line_name}' تکراری است")
                    continue
                height_leg_a = str(row["ارتفاع پایه A"]) if pd.notna(row["ارتفاع پایه A"]) else ""
                if height_leg_a and not re.match(r"^\d*\.?\d*$", height_leg_a):
                    errors.append(f"ردیف {index + 2}: ارتفاع پایه A باید عدد باشد")
                    continue
                height_leg_b = str(row["ارتفاع پایه B"]) if pd.notna(row["ارتفاع پایه B"]) else ""
                if height_leg_b and not re.match(r"^\d*\.?\d*$", height_leg_b):
                    errors.append(f"ردیف {index + 2}: ارتفاع پایه B باید عدد باشد")
                    continue
                height_leg_c = str(row["ارتفاع پایه C"]) if pd.notna(row["ارتفاع پایه C"]) else ""
                if height_leg_c and not re.match(r"^\d*\.?\d*$", height_leg_c):
                    errors.append(f"ردیف {index + 2}: ارتفاع پایه C باید عدد باشد")
                    continue
                height_leg_d = str(row["ارتفاع پایه D"]) if pd.notna(row["ارتفاع پایه D"]) else ""
                if height_leg_d and not re.match(r"^\d*\.?\d*$", height_leg_d):
                    errors.append(f"ردیف {index + 2}: ارتفاع پایه D باید عدد باشد")
                    continue
                insulator_count_c1_r = str(row["تعداد R مدار اول"]) if pd.notna(row["تعداد R مدار اول"]) else ""
                if insulator_count_c1_r and not insulator_count_c1_r.isdigit():
                    errors.append(f"ردیف {index + 2}: تعداد R مدار اول باید عدد باشد")
                    continue
                insulator_count_c1_s = str(row["تعداد S مدار اول"]) if pd.notna(row["تعداد S مدار اول"]) else ""
                if insulator_count_c1_s and not insulator_count_c1_s.isdigit():
                    errors.append(f"ردیف {index + 2}: تعداد S مدار اول باید عدد باشد")
                    continue
                insulator_count_c1_t = str(row["تعداد T مدار اول"]) if pd.notna(row["تعداد T مدار اول"]) else ""
                if insulator_count_c1_t and not insulator_count_c1_t.isdigit():
                    errors.append(f"ردیف {index + 2}: تعداد T مدار اول باید عدد باشد")
                    continue
                insulator_count_c2_r = str(row["تعداد R مدار دوم"]) if pd.notna(row["تعداد R مدار دوم"]) else ""
                if insulator_count_c2_r and not insulator_count_c2_r.isdigit():
                    errors.append(f"ردیف {index + 2}: تعداد R مدار دوم باید عدد باشد")
                    continue
                insulator_count_c2_s = str(row["تعداد S مدار دوم"]) if pd.notna(row["تعداد S مدار دوم"]) else ""
                if insulator_count_c2_s and not insulator_count_c2_s.isdigit():
                    errors.append(f"ردیف {index + 2}: تعداد S مدار دوم باید عدد باشد")
                    continue
                insulator_count_c2_t = str(row["تعداد T مدار دوم"]) if pd.notna(row["تعداد T مدار دوم"]) else ""
                if insulator_count_c2_t and not insulator_count_c2_t.isdigit():
                    errors.append(f"ردیف {index + 2}: تعداد T مدار دوم باید عدد باشد")
                    continue
                self.db.execute_query(
                    """
                    INSERT INTO towers (line_name, tower_number, tower_structure, tower_type, base_type,
                                    height_leg_a, height_leg_b, height_leg_c, height_leg_d,
                                    insulator_type_c1_r, insulator_type_c1_s, insulator_type_c1_t,
                                    insulator_type_c2_r, insulator_type_c2_s, insulator_type_c2_t,
                                    insulator_count_c1_r, insulator_count_c1_s, insulator_count_c1_t,
                                    insulator_count_c2_r, insulator_count_c2_s, insulator_count_c2_t,
                                    longitude, latitude)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                    (
                        line_name,
                        tower_number,
                        str(row["ساختار دکل"]) if pd.notna(row["ساختار دکل"]) else "",
                        str(row["نوع دکل"]) if pd.notna(row["نوع دکل"]) else "",
                        str(row["نوع پایه"]) if pd.notna(row["نوع پایه"]) else "",
                        self.format_number(row["ارتفاع پایه A"]),
                        self.format_number(row["ارتفاع پایه B"]),
                        self.format_number(row["ارتفاع پایه C"]),
                        self.format_number(row["ارتفاع پایه D"]),
                        str(row["نوع مقره R مدار اول"]) if pd.notna(row["نوع مقره R مدار اول"]) else "",
                        str(row["نوع مقره S مدار اول"]) if pd.notna(row["نوع مقره S مدار اول"]) else "",
                        str(row["نوع مقره T مدار اول"]) if pd.notna(row["نوع مقره T مدار اول"]) else "",
                        str(row["نوع مقره R مدار دوم"]) if pd.notna(row["نوع مقره R مدار دوم"]) else "",
                        str(row["نوع مقره S مدار دوم"]) if pd.notna(row["نوع مقره S مدار دوم"]) else "",
                        str(row["نوع مقره T مدار دوم"]) if pd.notna(row["نوع مقره T مدار دوم"]) else "",
                        insulator_count_c1_r,
                        insulator_count_c1_s,
                        insulator_count_c1_t,
                        insulator_count_c2_r,
                        insulator_count_c2_s,
                        insulator_count_c2_t,
                        str(row["طول جغرافیایی"]) if pd.notna(row["طول جغرافیایی"]) else None,
                        str(row["عرض جغرافیایی"]) if pd.notna(row["عرض جغرافیایی"]) else None
                    )
                )
                inserted_count += 1
                existing_towers.add((line_name, tower_number))
            self.load_table()
            if errors:
                QMessageBox.warning(self, "هشدار", f"{inserted_count} دکل وارد شد، اما {len(errors)} خطا رخ داد:\n" + "\n".join(errors[:5]))
            else:
                QMessageBox.information(self, "موفقیت", f"{inserted_count} دکل با موفقیت از فایل اکسل وارد شد.")
        except Exception as e:
            logging.error(f"Error in import_from_excel: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در وارد کردن اطلاعات از اکسل: {str(e)}")

    def show_context_menu(self, position):
        try:
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu { 
                    background-color: white; 
                    border: 1px solid #ccc; 
                    direction: ltr; 
                }
                QMenu::item { 
                    padding: 5px 20px; 
                    color: black; 
                    direction: ltr; 
                }
                QMenu::item:selected { 
                    background-color: #d0d0d0; 
                    color: black; 
                }
            """)
            copy_action = QAction("کپی", self)
            copy_action.triggered.connect(self.copy_selected_cells)
            menu.addAction(copy_action)
            edit_action = QAction("ویرایش", self)
            edit_action.triggered.connect(self.edit_tower)
            menu.addAction(edit_action)
            delete_action = QAction("حذف", self)
            delete_action.triggered.connect(self.delete_tower)
            menu.addAction(delete_action)
            selected_items = bool(self.table.selectedItems())
            copy_action.setEnabled(selected_items)
            edit_action.setEnabled(selected_items)
            delete_action.setEnabled(selected_items)
            menu.exec_(self.table.viewport().mapToGlobal(position))
        except Exception as e:
            logging.error(f"Error in show_context_menu: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در نمایش منوی راست‌کلیک: {str(e)}")

    def copy_selected_cells(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        rows = sorted(set(item.row() for item in selected_items))
        cols = sorted(set(item.column() for item in selected_items))
        text = ""
        for row in rows:
            row_data = []
            for col in cols:
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            text += "\t".join(row_data) + "\n"
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "موفقیت", "محتوای سلول‌های انتخاب‌شده کپی شد.")

    def save_cell(self, row, col):
        try:
            item = self.table.item(row, col)
            if not item:
                return
            new_value = item.text().strip()
            tower_id = self.table.item(row, 0).data(Qt.UserRole)
            if not tower_id:
                logging.error("No tower_id found for row")
                return
            column_name = self.column_names[col]
            if column_name in ['height_leg_a', 'height_leg_b', 'height_leg_c', 'height_leg_d']:
                if new_value and not re.match(r"^\d*\.?\d*$", new_value):
                    QMessageBox.critical(self, "خطا", f"مقدار {self.original_headers[col]} باید عدد باشد!")
                    self.load_table()
                    return
            elif column_name in ['insulator_count_c1_r', 'insulator_count_c1_s', 'insulator_count_c1_t',
                                 'insulator_count_c2_r', 'insulator_count_c2_s', 'insulator_count_c2_t']:
                if new_value and not new_value.isdigit():
                    QMessageBox.critical(self, "خطا", f"مقدار {self.original_headers[col]} باید عدد باشد!")
                    self.load_table()
                    return
            elif column_name == 'tower_number':
                if not new_value:
                    QMessageBox.critical(self, "خطا", "شماره دکل اجباری است!")
                    self.load_table()
                    return
                line_name = self.table.item(row, 0).text()
                existing_towers = self.db.fetch_all("SELECT tower_number FROM towers WHERE line_name = ? AND id != ?", (line_name, tower_id))
                if new_value in [tower[0] for tower in existing_towers]:
                    QMessageBox.critical(self, "خطا", "شماره دکل باید یکتا باشد!")
                    self.load_table()
                    return
            elif column_name == 'line_name':
                if not new_value:
                    QMessageBox.critical(self, "خطا", "نام خط اجباری است!")
                    self.load_table()
                    return
                valid_lines = self.db.fetch_all("SELECT line_name FROM lines")
                if new_value not in [line[0] for line in valid_lines]:
                    QMessageBox.critical(self, "خطا", "نام خط نامعتبر است!")
                    self.load_table()
                    return
            query = f"UPDATE towers SET {column_name} = ? WHERE id = ?"
            self.db.execute_query(query, (new_value, tower_id))
            logging.debug(f"Updated {column_name} to '{new_value}' for tower_id {tower_id}")
        except Exception as e:
            logging.error(f"Error in save_cell: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره تغییرات: {str(e)}")
            self.load_table()
