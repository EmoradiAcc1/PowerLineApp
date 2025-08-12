from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QToolBar, QAction, QLineEdit, QLabel, QMessageBox, QStyle, QDialog, QFormLayout, QPushButton, QFileDialog, QHeaderView, QSizePolicy, QMenu, QApplication, QSpacerItem, QGroupBox, QScrollArea, QProgressDialog
from PyQt5.QtCore import Qt, QEvent, QPoint, QTimer
from PyQt5.QtGui import QFont, QIcon
from modules.database import Database
from modules.custom_widgets import NoWheelComboBox, CustomDialog_Progress, CustomTableWidget, CustomRightClick, TableActions
from modules.custom_widgets import CustomDialog_Flexible
import csv
import re
import pandas as pd
import logging
import traceback
from collections import defaultdict

# تنظیم لاگ برای دیباگ
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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

        # Apply section title styling
        self.setStyleSheet("""
            QGroupBox {
                font-weight: normal;
            }
            QGroupBox::title {
                color: rgb(1, 123, 204);
            }
        """)
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
        # چیدمان اصلی با اسکرول
        self.scroll = QScrollArea()
        # Set a more compact dialog width and adjust widget sizes
        self.setMinimumWidth(700)  # Reduce dialog width
        self.setMinimumHeight(600)  # Set a minimum height
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)  # Reduce margins
        self.main_layout.setSpacing(10)  # Reduce spacing
        self.scroll.setWidget(self.content_widget)
        self.scroll_layout = QVBoxLayout(self)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.addWidget(self.scroll)

        # سکشن اطلاعات پایه
        self.section1 = QGroupBox("اطلاعات پایه")
        self.section1.setFont(self.font)
        self.section1_layout = QVBoxLayout()
        self.section1_layout.setContentsMargins(15, 10, 15, 10)  # Reduce section margins
        self.section1_layout.setSpacing(10)  # Reduce section spacing
        self.section1.setLayout(self.section1_layout)

        # عرض ثابت برای ویجت‌ها - کاهش اندازه‌ها
        dialog_width = 650  # Reduced from 800
        label_width = 90  # Reduced from 100
        widget_width = 200  # Fixed width for QLineEdit
        combo_width = 400  # Fixed width for QComboBox

        # ردیف اول: فقط نام خط
        self.line_name = NoWheelComboBox()
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
        self.insulator_type_c1_r = NoWheelComboBox()
        self.insulator_type_c1_r.setFont(self.font)
        self.insulator_type_c1_r.addItems(["", "سرامیکی", "شیشه‌ای", "سیلیکونی"])
        self.insulator_type_c1_r.setStyleSheet(combo_rtl_style)
        self.insulator_type_c1_r.setFixedWidth(widget_width)
        self.insulator_type_c2_r = NoWheelComboBox()
        self.insulator_type_c2_r.setFont(self.font)
        self.insulator_type_c2_r.addItems(["", "سرامیکی", "شیشه‌ای", "سیلیکونی"])
        self.insulator_type_c2_r.setStyleSheet(combo_rtl_style)
        self.insulator_type_c2_r.setFixedWidth(widget_width)
        row6 = QHBoxLayout()
        row6.addWidget(QLabel("نوع مقره R مدار اول:", font=self.font))
        row6.addWidget(self.insulator_type_c1_r)
        row6.addSpacing(20)
        row6.addWidget(QLabel("نوع مقره R مدار دوم:", font=self.font))
        row6.addWidget(self.insulator_type_c2_r)
        self.section3_layout.addLayout(row6)

        # ردیف دوم: نوع مقره S مدار اول (راست) و S مدار دوم (چپ)
        self.insulator_type_c1_s = NoWheelComboBox()
        self.insulator_type_c1_s.setFont(self.font)
        self.insulator_type_c1_s.addItems(["", "سرامیکی", "شیشه‌ای", "سیلیکونی"])
        self.insulator_type_c1_s.setStyleSheet(combo_rtl_style)
        self.insulator_type_c1_s.setFixedWidth(widget_width)
        self.insulator_type_c2_s = NoWheelComboBox()
        self.insulator_type_c2_s.setFont(self.font)
        self.insulator_type_c2_s.addItems(["", "سرامیکی", "شیشه‌ای", "سیلیکونی"])
        self.insulator_type_c2_s.setStyleSheet(combo_rtl_style)
        self.insulator_type_c2_s.setFixedWidth(widget_width)
        row7 = QHBoxLayout()
        row7.addWidget(QLabel("نوع مقره S مدار اول:", font=self.font))
        row7.addWidget(self.insulator_type_c1_s)
        row7.addSpacing(20)
        row7.addWidget(QLabel("نوع مقره S مدار دوم:", font=self.font))
        row7.addWidget(self.insulator_type_c2_s)
        self.section3_layout.addLayout(row7)

        # ردیف سوم: نوع مقره T مدار اول (راست) و T مدار دوم (چپ)
        self.insulator_type_c1_t = NoWheelComboBox()
        self.insulator_type_c1_t.setFont(self.font)
        self.insulator_type_c1_t.addItems(["", "سرامیکی", "شیشه‌ای", "سیلیکونی"])
        self.insulator_type_c1_t.setStyleSheet(combo_rtl_style)
        self.insulator_type_c1_t.setFixedWidth(widget_width)
        self.insulator_type_c2_t = NoWheelComboBox()
        self.insulator_type_c2_t.setFont(self.font)
        self.insulator_type_c2_t.addItems(["", "سرامیکی", "شیشه‌ای", "سیلیکونی"])
        self.insulator_type_c2_t.setStyleSheet(combo_rtl_style)
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

        # اشاره‌گر موس برای دکمه‌های ذخیره و لغو
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setCursor(Qt.PointingHandCursor)

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
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=error_msg, ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            dlg.exec_()
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
        self.layout.setContentsMargins(10, 10, 10, 10)  # کاهش margins
        self.layout.setSpacing(10)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet("background-color: #f0f0f0;")

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

        self.add_action = QAction(QIcon("resources/Icons/Add_Item.png"), "افزودن دکل جدید", self)
        self.copy_action = QAction(QIcon("Resources/Icons/Toolsbar_Copy.png"), "کپی", self)
        self.delete_action = QAction(QIcon("resources/Icons/Delete_Table.png"), "حذف", self)
        self.edit_action = QAction(QIcon("resources/Icons/Edit_Table.png"), "ویرایش", self)
        self.import_excel_action = QAction(QIcon("resources/Icons/Import_From_Excel.png"), "ورود اطلاعات از اکسل", self)
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

        self.add_action.triggered.connect(self.add_tower)
        self.copy_action.triggered.connect(lambda: self.safe_copy())
        self.delete_action.triggered.connect(self.delete_tower)
        self.edit_action.triggered.connect(self.edit_tower)
        self.import_excel_action.triggered.connect(self.import_from_excel)
        self.report_action.triggered.connect(self.generate_report)
        self.back_action.triggered.connect(self.close)

        # Table
        self.table = CustomTableWidget(
            table_name="towers",
            headers=self.original_headers,
            column_names=self.column_names,
            db=self.db
        )
        self.layout.addWidget(self.table, 1)  # stretch factor = 1
        self.table.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.load_table()
        self.table._custom_edit_callback = self.edit_tower
        self.table._custom_clear_filters_callback = self.clear_all_filters

        # تنظیم اشاره‌گر موس به حالت دست برای دکمه‌های نوار ابزار
        for action in [self.add_action, self.copy_action, self.delete_action, self.edit_action, self.import_excel_action, self.report_action, self.back_action]:
            btn = self.toolbar.widgetForAction(action)
            if btn is not None:
                btn.setCursor(Qt.PointingHandCursor)

    def update_column_filter(self, column_index, filter_text):
        try:
            column_name = self.column_names[column_index]
            logging.debug(f"Updating filter for column {column_name}: {filter_text}")
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
            logging.error(f"Error in update_column_filter: {str(e)}\n{traceback.format_exc()}")
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
            
            logging.debug("Towers window column filters cleared successfully")
        except Exception as e:
            logging.error(f"Error in clear_all_filters: {str(e)}", exc_info=True)

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
            self.table.table.setRowCount(len(rows))
            self.table.table.blockSignals(True)
            for row_idx, row_data in enumerate(rows):
                for col_idx, data in enumerate(row_data[:-1]):
                    data = str(data) if data is not None else ""
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
            logging.debug(f"Table loaded with {len(rows)} rows")
        except Exception as e:
            logging.error(f"Error in load_table: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری جدول: {str(e)}")
        finally:
            self.table.blockSignals(False)

    def perform_search(self):
        try:
            search_text = self.filter_input.text().strip()
            logging.debug(f"Performing search: {search_text}")
            self.load_table(search_text)
        except Exception as e:
            logging.error(f"Error in perform_search: {str(e)}\n{traceback.format_exc()}")
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در جستجو: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()

    def filter_table(self):
        """برای سازگاری با کد قدیمی - مستقیماً فیلتر می‌کند"""
        self.perform_search()

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
                dlg = CustomDialog_Flexible(header_text="موفقیت", main_text="دکل با موفقیت اضافه شد.", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxInformation))
                dlg.exec_()
            except Exception as e:
                logging.error(f"Error in add_tower: {str(e)}\n{traceback.format_exc()}")
                dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در افزودن دکل: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
                dlg.exec_()

    def edit_tower(self):
        selected = self.table.table.selectedItems()
        if not selected:
            dlg = CustomDialog_Flexible(header_text="هشدار", main_text="لطفاً ابتدا دکل مورد نظر را انتخاب کنید.", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            dlg.exec_()
            return
        row = self.table.table.currentRow()
        tower_number = self.table.table.item(row, 1).text() if self.table.table.item(row, 1) else ""
        line_name = self.table.table.item(row, 0).text() if self.table.table.item(row, 0) else ""
        try:
            result = self.db.fetch_all("SELECT id FROM towers WHERE tower_number=? AND line_name=?", (tower_number, line_name))
            if not result:
                dlg = CustomDialog_Flexible(header_text="خطا", main_text="دکل موردنظر یافت نشد!", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
                dlg.exec_()
                return
            current_id = result[0][0]
            tower_data = {
                'id': current_id,
                'line_name': line_name,
                'tower_number': tower_number,
                'tower_structure': self.table.table.item(row, 2).text() if self.table.table.item(row, 2) else "",
                'tower_type': self.table.table.item(row, 3).text() if self.table.table.item(row, 3) else "",
                'base_type': self.table.table.item(row, 4).text() if self.table.table.item(row, 4) else "",
                'height_leg_a': self.table.table.item(row, 5).text() if self.table.table.item(row, 5) else "",
                'height_leg_b': self.table.table.item(row, 6).text() if self.table.table.item(row, 6) else "",
                'height_leg_c': self.table.table.item(row, 7).text() if self.table.table.item(row, 7) else "",
                'height_leg_d': self.table.table.item(row, 8).text() if self.table.table.item(row, 8) else "",
                'insulator_type_c1_r': self.table.table.item(row, 9).text() if self.table.table.item(row, 9) else "",
                'insulator_type_c1_s': self.table.table.item(row, 10).text() if self.table.table.item(row, 10) else "",
                'insulator_type_c1_t': self.table.table.item(row, 11).text() if self.table.table.item(row, 11) else "",
                'insulator_type_c2_r': self.table.table.item(row, 12).text() if self.table.table.item(row, 12) else "",
                'insulator_type_c2_s': self.table.table.item(row, 13).text() if self.table.table.item(row, 13) else "",
                'insulator_type_c2_t': self.table.table.item(row, 14).text() if self.table.table.item(row, 14) else "",
                'insulator_count_c1_r': self.table.table.item(row, 15).text() if self.table.table.item(row, 15) else "",
                'insulator_count_c1_s': self.table.table.item(row, 16).text() if self.table.table.item(row, 16) else "",
                'insulator_count_c1_t': self.table.table.item(row, 17).text() if self.table.table.item(row, 17) else "",
                'insulator_count_c2_r': self.table.table.item(row, 18).text() if self.table.table.item(row, 18) else "",
                'insulator_count_c2_s': self.table.table.item(row, 19).text() if self.table.table.item(row, 19) else "",
                'insulator_count_c2_t': self.table.table.item(row, 20).text() if self.table.table.item(row, 20) else "",
                'longitude': self.table.table.item(row, 21).text() if self.table.table.item(row, 21) else "",
                'latitude': self.table.table.item(row, 22).text() if self.table.table.item(row, 22) else ""
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
                self.table.load_table()
                dlg = CustomDialog_Flexible(header_text="موفقیت", main_text="دکل با موفقیت ویرایش شد.", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxInformation))
                dlg.exec_()
        except Exception as e:
            logging.error(f"Error in edit_tower: {str(e)}\n{traceback.format_exc()}")
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در ویرایش دکل: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()

    def safe_copy(self):
        """کپی کردن دکل انتخاب شده - مشابه عملکرد کلیک راست"""
        try:
            TableActions.copy_selected(self.table.table, self.db, self, "towers", self.table.load_table)
        except Exception as e:
            logging.error(f"Exception in safe_copy: {str(e)}", exc_info=True)
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در کپی: {str(e)}", ok_text="باشه", parent=self)
            dlg.exec_()

    def delete_tower(self):
        selected_rows = sorted(set(index.row() for index in self.table.table.selectedIndexes()))
        if not selected_rows:
            dlg = CustomDialog_Flexible(header_text="هشدار", main_text="لطفاً ابتدا دکل مورد نظر را انتخاب کنید.", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            dlg.exec_()
            return

        row_count = len(selected_rows)
        msg = f"آیا از حذف این {row_count} دکل مطمئن هستید؟"
        dlg = CustomDialog_Flexible(header_text="تأیید حذف", main_text=msg, ok_text="بله", cancel_text="خیر", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxWarning))
        if dlg.exec_() != dlg.Accepted:
            return

        try:
            progress = CustomDialog_Progress(header_text="در حال حذف دکل‌ها...", cancel_text="لغو عملیات", parent=self)
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
            # ابتدا کلیدهای دکل‌های انتخاب شده را جمع‌آوری کنیم
            towers_to_delete = []
            for row in selected_rows:
                line_name = self.table.table.item(row, 0).text() if self.table.table.item(row, 0) else ""
                tower_number = self.table.table.item(row, 1).text() if self.table.table.item(row, 1) else ""
                if line_name and tower_number:
                    towers_to_delete.append((line_name, tower_number))
            # حالا حذف را انجام دهیم
            for i, (line_name, tower_number) in enumerate(towers_to_delete):
                try:
                    QApplication.processEvents()
                    if self.deletion_cancelled:
                        break
                    progress.set_progress(i + 1)
                    progress.set_text(f"{i+1} از {row_count}")
                    self.db.execute_query("DELETE FROM towers WHERE tower_number=? AND line_name=?", (tower_number, line_name))
                    deleted_count += 1
                except Exception as e:
                    logging.error(f"Error deleting tower {tower_number} from line {line_name}: {str(e)}")
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
                msg = f"عملیات لغو شد و {deleted_count} دکل تا این لحظه حذف شد."
                self.table.table.clearSelection()
                dlg = CustomDialog_Flexible(header_text="لغو عملیات", main_text=msg, ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                dlg.exec_()
            elif deleted_count > 0:
                self.table.table.clearSelection()
                dlg = CustomDialog_Flexible(header_text="موفقیت", main_text=f"{deleted_count} دکل با موفقیت حذف شد.", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxInformation))
                dlg.exec_()
        except Exception as e:
            logging.error(f"Error in delete_tower: {str(e)}\n{traceback.format_exc()}")
            try:
                progress.close()
            except:
                pass
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در حذف: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()

    def load_row_data(self):
        pass

    def generate_report(self):
        self.table.generate_report(parent=self, headers=self.original_headers)

    def import_from_excel(self):
        try:
            from collections import defaultdict
            import re
            def summarize_towers(tower_list):
                line_dict = defaultdict(list)
                for item in tower_list:
                    match = re.match(r"خط (.*?) - دکل (\d+)", item)
                    if match:
                        line_name = match.group(1)
                        tower_num = int(match.group(2))
                        line_dict[line_name].append(tower_num)
                result = []
                for line, towers in line_dict.items():
                    towers = sorted(set(towers))
                    def to_ranges(nums):
                        ranges = []
                        start = end = None
                        for n in nums:
                            if start is None:
                                start = end = n
                            elif n == end + 1:
                                end = n
                            else:
                                if start == end:
                                    ranges.append(str(start))
                                else:
                                    ranges.append(f"{start}-{end}")
                                start = end = n
                        if start is not None:
                            if start == end:
                                ranges.append(str(start))
                            else:
                                ranges.append(f"{start}-{end}")
                        return ", ".join(ranges)
                    range_str = to_ranges(towers)
                    result.append(f"خط {line}: دکل‌های {range_str}")
                return result
            def summarize_invalid_lines(invalid_list):
                line_dict = defaultdict(list)
                for item in invalid_list:
                    match = re.match(r"خط (.*?) - دکل (\d+)", item)
                    if match:
                        line_name = match.group(1)
                        tower_num = int(match.group(2))
                        line_dict[line_name].append(tower_num)
                    else:
                        match2 = re.match(r"خط (.*)", item)
                        if match2:
                            line_name = match2.group(1)
                            line_dict[line_name] = []
                result = []
                for line, towers in line_dict.items():
                    if towers:
                        towers = sorted(set(towers))
                        def to_ranges(nums):
                            ranges = []
                            start = end = None
                            for n in nums:
                                if start is None:
                                    start = end = n
                                elif n == end + 1:
                                    end = n
                                else:
                                    if start == end:
                                        ranges.append(str(start))
                                    else:
                                        ranges.append(f"{start}-{end}")
                                    start = end = n
                            if start is not None:
                                if start == end:
                                    ranges.append(str(start))
                                else:
                                    ranges.append(f"{start}-{end}")
                            return ", ".join(ranges)
                        range_str = to_ranges(towers)
                        result.append(f"خط {line}: دکل‌های {range_str}")
                    else:
                        result.append(f"خط {line}")
                return result
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
            
            # دریافت دکل‌های موجود در دیتابیس
            existing_towers = {(row[0], row[1]) for row in self.db.fetch_all("SELECT line_name, tower_number FROM towers") if row[0] and row[1]}
            
            # دریافت خطوط معتبر
            valid_lines = {row[0] for row in self.db.fetch_all("SELECT line_name FROM lines") if row[0]}
            
            # بررسی داده‌های فایل Excel
            duplicate_in_file = []
            invalid_lines = []
            valid_rows = []
            
            for index, row in df.iterrows():
                line_name = str(row["نام خط"]).strip() if pd.notna(row["نام خط"]) else ""
                tower_number = str(row["شماره دکل"]).strip() if pd.notna(row["شماره دکل"]) else ""
                
                if not line_name or not tower_number:
                    continue
                
                # بررسی تکراری بودن در فایل
                tower_key = (line_name, tower_number)
                if tower_key in [r[0] for r in valid_rows]:
                    duplicate_in_file.append(f"خط {line_name} - دکل {tower_number}")
                    continue
                
                # بررسی وجود در دیتابیس
                if tower_key in existing_towers:
                    duplicate_in_file.append(f"خط {line_name} - دکل {tower_number}")
                    continue
                
                # بررسی معتبر بودن نام خط
                if line_name not in valid_lines:
                    invalid_lines.append(f"خط {line_name}")
                    continue
                
                valid_rows.append((tower_key, row))
            
            # نمایش خطاها
            error_messages = []
            if duplicate_in_file:
                summarized = summarize_towers(duplicate_in_file)
                error_messages.append(f"دکل‌های تکراری ({len(duplicate_in_file)} مورد):\n" + "\n".join(summarized[:10]) + (f"\n... و {len(summarized)-10} خط دیگر" if len(summarized) > 10 else ""))
            if invalid_lines:
                summarized = summarize_invalid_lines(invalid_lines)
                error_messages.append(f"خطوط نامعتبر ({len(invalid_lines)} مورد):\n" + "\n".join(summarized[:10]) + (f"\n... و {len(summarized)-10} خط دیگر" if len(summarized) > 10 else ""))
            
            if error_messages:
                error_text = "\n\n".join(error_messages)
                error_text += f"\n\nاز {len(df)} ردیف، فقط {len(valid_rows)} ردیف قابل وارد کردن است."
                dlg = CustomDialog_Flexible(
                    header_text="خطاهای یافت شده",
                    main_text=error_text,
                    ok_text="بله",
                    cancel_text="خیر",
                    question_text="آیا می‌خواهید دکل‌های معتبر را وارد کنید؟",
                    parent=self
                )
                dlg.adjustSize()
                if dlg.exec_() != dlg.Accepted:
                    return
            if not valid_rows:
                dlg = CustomDialog_Flexible(header_text="هشدار", main_text="هیچ دکل معتبری برای وارد کردن یافت نشد.", ok_text="باشه", cancel_text=None, parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning)))
                dlg.exec_()
                return
            inserted_count = 0
            duplicate_count = 0
            progress = CustomDialog_Progress(header_text="در حال وارد کردن اطلاعات دکل‌ها...", cancel_text="لغو عملیات", parent=self)
            progress.set_maximum(len(valid_rows))
            progress.set_progress(0)
            progress.set_text(f"0 از {len(valid_rows)}")
            progress.show()
            QApplication.processEvents()
            def cancel():
                self.import_cancelled = True
            progress.cancel_btn.clicked.connect(cancel)
            for i, (tower_key, row) in enumerate(valid_rows):
                QApplication.processEvents()
                if self.import_cancelled:
                    break
                progress.set_progress(i + 1)
                progress.set_text(f"{i+1} از {len(valid_rows)}")
                line_name, tower_number = tower_key
                # بررسی تکراری بودن
                if (line_name, tower_number) in existing_towers:
                    duplicate_count += 1
                    continue
                try:
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
                            str(row["ارتفاع پایه A"]) if pd.notna(row["ارتفاع پایه A"]) else "",
                            str(row["ارتفاع پایه B"]) if pd.notna(row["ارتفاع پایه B"]) else "",
                            str(row["ارتفاع پایه C"]) if pd.notna(row["ارتفاع پایه C"]) else "",
                            str(row["ارتفاع پایه D"]) if pd.notna(row["ارتفاع پایه D"]) else "",
                            str(row["نوع مقره R مدار اول"]) if pd.notna(row["نوع مقره R مدار اول"]) else "",
                            str(row["نوع مقره S مدار اول"]) if pd.notna(row["نوع مقره S مدار اول"]) else "",
                            str(row["نوع مقره T مدار اول"]) if pd.notna(row["نوع مقره T مدار اول"]) else "",
                            str(row["نوع مقره R مدار دوم"]) if pd.notna(row["نوع مقره R مدار دوم"]) else "",
                            str(row["نوع مقره S مدار دوم"]) if pd.notna(row["نوع مقره S مدار دوم"]) else "",
                            str(row["نوع مقره T مدار دوم"]) if pd.notna(row["نوع مقره T مدار دوم"]) else "",
                            str(row["تعداد R مدار اول"]) if pd.notna(row["تعداد R مدار اول"]) else "",
                            str(row["تعداد S مدار اول"]) if pd.notna(row["تعداد S مدار اول"]) else "",
                            str(row["تعداد T مدار اول"]) if pd.notna(row["تعداد T مدار اول"]) else "",
                            str(row["تعداد R مدار دوم"]) if pd.notna(row["تعداد R مدار دوم"]) else "",
                            str(row["تعداد S مدار دوم"]) if pd.notna(row["تعداد S مدار دوم"]) else "",
                            str(row["تعداد T مدار دوم"]) if pd.notna(row["تعداد T مدار دوم"]) else "",
                            str(row["طول جغرافیایی"]) if pd.notna(row["طول جغرافیایی"]) else None,
                            str(row["عرض جغرافیایی"]) if pd.notna(row["عرض جغرافیایی"]) else None
                        )
                    )
                    inserted_count += 1
                    existing_towers.add((line_name, tower_number))
                except Exception as e:
                    logging.error(f"Error inserting tower {line_name}-{tower_number}: {str(e)}")
                    continue
            progress.accept()
            if self.import_cancelled:
                self.load_table()
                msg = f"عملیات لغو شد و {inserted_count} دکل تا این لحظه وارد شد."
                if duplicate_count > 0:
                    msg += f" {duplicate_count} دکل به دلیل تکراری بودن وارد نشد."
                dlg = CustomDialog_Flexible(header_text="لغو عملیات", main_text=msg, ok_text="باشه", parent=self)
                dlg.exec_()
                return
            self.load_table()
            msg = f"{inserted_count} دکل با موفقیت وارد شد."
            if duplicate_count > 0:
                msg += f"\n{duplicate_count} دکل به دلیل تکراری بودن وارد نشد."
            dlg = CustomDialog_Flexible(header_text="موفقیت", main_text=msg, ok_text="باشه", parent=self)
            dlg.exec_()
        except Exception as e:
            logging.error(f"Error in import_from_excel: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در وارد کردن اطلاعات از اکسل: {str(e)}")

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
                    dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"مقدار {self.original_headers[col]} باید عدد باشد!", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    dlg.exec_()
                    self.load_table()
                    return
            elif column_name in ['insulator_count_c1_r', 'insulator_count_c1_s', 'insulator_count_c1_t',
                                 'insulator_count_c2_r', 'insulator_count_c2_s', 'insulator_count_c2_t']:
                if new_value and not new_value.isdigit():
                    dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"مقدار {self.original_headers[col]} باید عدد باشد!", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    dlg.exec_()
                    self.load_table()
                    return
            elif column_name == 'tower_number':
                if not new_value:
                    dlg = CustomDialog_Flexible(header_text="خطا", main_text="شماره دکل اجباری است!", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    dlg.exec_()
                    self.load_table()
                    return
                line_name = self.table.item(row, 0).text()
                existing_towers = self.db.fetch_all("SELECT tower_number FROM towers WHERE line_name = ? AND id != ?", (line_name, tower_id))
                if new_value in [tower[0] for tower in existing_towers]:
                    dlg = CustomDialog_Flexible(header_text="خطا", main_text="شماره دکل باید یکتا باشد!", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    dlg.exec_()
                    self.load_table()
                    return
            elif column_name == 'line_name':
                if not new_value:
                    dlg = CustomDialog_Flexible(header_text="خطا", main_text="نام خط اجباری است!", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    dlg.exec_()
                    self.load_table()
                    return
                valid_lines = self.db.fetch_all("SELECT line_name FROM lines")
                if new_value not in [line[0] for line in valid_lines]:
                    dlg = CustomDialog_Flexible(header_text="خطا", main_text="نام خط نامعتبر است!", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    dlg.exec_()
                    self.load_table()
                    return
            query = f"UPDATE towers SET {column_name} = ? WHERE id = ?"
            self.db.execute_query(query, (new_value, tower_id))
            logging.debug(f"Updated {column_name} to '{new_value}' for tower_id {tower_id}")
        except Exception as e:
            logging.error(f"Error in save_cell: {str(e)}\n{traceback.format_exc()}")
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در ذخیره تغییرات: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()
            self.load_table()
