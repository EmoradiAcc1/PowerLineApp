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

class LineInputDialog(CustomPaper):
    def __init__(self, parent=None, line_data=None, is_edit=False):
        # تنظیم اندازه مناسب برای دیالوگ
        dialog_width = 670  # عرض مناسب
        dialog_height = 900  # ارتفاع زیاد برای نمایش کامل محتوا
        
        super().__init__(parent, background_color="#F5F5F5", corner_radius=15, width=dialog_width, height=dialog_height)
        
        self.setWindowTitle("افزودن خط" if not is_edit else "ویرایش خط")
        self.setLayoutDirection(Qt.RightToLeft)
        self.is_edit = is_edit
        self.current_id = line_data.get('id') if line_data else None
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
        header_text = "افزودن خط" if not is_edit else "ویرایش خط"
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

        # محتوای اصلی با اسکرول
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f5f5f5;
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
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 10, 0, 0)
        content_layout.setSpacing(15)
        
        content_scroll.setWidget(content_widget)
        self.main_layout.addWidget(content_scroll, stretch=1)
        
        # دکمه‌های ذخیره و لغو در پایین دیالوگ (خارج از اسکرول)
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
        self.main_layout.addLayout(self.button_layout)

        # عرض responsive برای ویجت‌ها
        label_width = 120
        widget_width = 150  # عرض فیلدهای معمولی
        combo_width = 200  # افزایش عرض کمبوباکس‌ها
        line_name_width = 462  # عرض نام خط (هم‌راستا با سایر عناصر)

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

        # ردیف ۱: فقط نام خط
        self.line_name = QLineEdit()
        self.line_name.setFont(self.font)
        self.line_name.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.line_name.setFixedWidth(462)  # عرض دقیق برای هم‌راستایی با سایر عناصر
        row1 = QHBoxLayout()
        label1 = QLabel("نام خط:", font=self.font)
        label1.setFixedWidth(label_width)
        label1.setStyleSheet("background-color: #F5F5F5;")
        row1.addWidget(label1)
        row1.addWidget(self.line_name)
        row1.addStretch()
        self.section1_layout.addLayout(row1)

        # ردیف ۲: کد خط و ولتاژ
        self.line_code = QLineEdit()
        self.line_code.setFont(self.font)
        self.line_code.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        # حذف setFixedWidth برای responsive بودن
        self.voltage = NoWheelComboBox()
        self.voltage.setFont(self.font)
        self.voltage.addItems(["","400", "230", "132", "63"])
        self.voltage.setStyleSheet(combo_rtl_style)
        self.voltage.setFixedWidth(widget_width)  # تنظیم عرض کمبوباکس ولتاژ مثل سایر عناصر
        row2 = QHBoxLayout()
        label2_1 = QLabel("کد خط:", font=self.font)
        label2_1.setFixedWidth(label_width)
        label2_1.setStyleSheet("background-color: #F5F5F5;")
        row2.addWidget(label2_1)
        row2.addWidget(self.line_code)
        row2.addSpacing(20)
        label2_2 = QLabel("ولتاژ (kV):", font=self.font)
        label2_2.setFixedWidth(label_width)
        label2_2.setStyleSheet("background-color: #F5F5F5;")
        row2.addWidget(label2_2)
        row2.addWidget(self.voltage)
        row2.addStretch()
        self.section1_layout.addLayout(row2)

        # ردیف ۳: کد دیسپاچینگ و سال بهره برداری
        self.dispatch_code = QLineEdit()
        self.dispatch_code.setFont(self.font)
        self.dispatch_code.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.dispatch_code.setFixedWidth(widget_width)
        self.operation_year = QLineEdit()
        self.operation_year.setFont(self.font)
        self.operation_year.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.operation_year.setFixedWidth(widget_width)
        row3 = QHBoxLayout()
        label3_1 = QLabel("کد دیسپاچینگ:", font=self.font)
        label3_1.setFixedWidth(label_width)
        label3_1.setStyleSheet("background-color: #F5F5F5;")
        row3.addWidget(label3_1)
        row3.addWidget(self.dispatch_code)
        row3.addSpacing(20)
        label3_2 = QLabel("سال بهره‌برداری:", font=self.font)
        label3_2.setFixedWidth(label_width)
        label3_2.setStyleSheet("background-color: #F5F5F5;")
        row3.addWidget(label3_2)
        row3.addWidget(self.operation_year)
        row3.addStretch()
        self.section1_layout.addLayout(row3)

        # ردیف ۴: تعداد مدار و تعداد باندل
        self.circuit_number = NoWheelComboBox()
        self.circuit_number.setFont(self.font)
        self.circuit_number.addItems(["", "1", "2", "3", "4", "5", "6"])
        self.circuit_number.setStyleSheet(combo_rtl_style)
        self.circuit_number.setFixedWidth(widget_width)
        self.bundle_number = NoWheelComboBox()
        self.bundle_number.setFont(self.font)
        self.bundle_number.addItems(["", "1", "2", "3", "4", "5", "6"])
        self.bundle_number.setStyleSheet(combo_rtl_style)
        self.bundle_number.setFixedWidth(widget_width)
        row4 = QHBoxLayout()
        label4_1 = QLabel("تعداد مدار:", font=self.font)
        label4_1.setFixedWidth(label_width)
        label4_1.setStyleSheet("background-color: #F5F5F5;")
        row4.addWidget(label4_1)
        row4.addWidget(self.circuit_number)
        row4.addSpacing(20)
        label4_2 = QLabel("تعداد باندل:", font=self.font)
        label4_2.setFixedWidth(label_width)
        label4_2.setStyleSheet("background-color: #F5F5F5;")
        row4.addWidget(label4_2)
        row4.addWidget(self.bundle_number)
        row4.addStretch()
        self.section1_layout.addLayout(row4)

        # ردیف ۵: نوع دکل و نوع سیم
        self.tower_type = NoWheelComboBox()
        self.tower_type.setFont(self.font)
        self.tower_type.addItems(["", "مشبک فلزی", "تلسکوپی", "تیر بتنی", "تیر چوبی"])
        self.tower_type.setStyleSheet(combo_rtl_style)
        self.tower_type.setFixedWidth(widget_width)
        self.wire_type = NoWheelComboBox()
        self.wire_type.setFont(self.font)
        self.wire_type.addItems(["", "لینکس", "کاناری", "کرلو", "داگ"])
        self.wire_type.setStyleSheet(combo_rtl_style)
        self.wire_type.setFixedWidth(widget_width)
        row5 = QHBoxLayout()
        label5_1 = QLabel("نوع دکل:", font=self.font)
        label5_1.setFixedWidth(label_width)
        label5_1.setStyleSheet("background-color: #F5F5F5;")
        row5.addWidget(label5_1)
        row5.addWidget(self.tower_type)
        row5.addSpacing(20)
        label5_2 = QLabel("نوع سیم:", font=self.font)
        label5_2.setFixedWidth(label_width)
        label5_2.setStyleSheet("background-color: #F5F5F5;")
        row5.addWidget(label5_2)
        row5.addWidget(self.wire_type)
        row5.addStretch()
        self.section1_layout.addLayout(row5)

        # ردیف ۶: طول خط و طول مدار
        self.line_length = QLineEdit()
        self.line_length.setFont(self.font)
        self.line_length.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.line_length.setFixedWidth(widget_width)
        self.circuit_length = QLineEdit()
        self.circuit_length.setFont(self.font)
        self.circuit_length.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.circuit_length.setFixedWidth(widget_width)
        row6 = QHBoxLayout()
        label6_1 = QLabel("طول خط (km):", font=self.font)
        label6_1.setFixedWidth(label_width)
        label6_1.setStyleSheet("background-color: #F5F5F5;")
        row6.addWidget(label6_1)
        row6.addWidget(self.line_length)
        row6.addSpacing(20)
        label6_2 = QLabel("طول مدار (km):", font=self.font)
        label6_2.setFixedWidth(label_width)
        label6_2.setStyleSheet("background-color: #F5F5F5;")
        row6.addWidget(label6_2)
        row6.addWidget(self.circuit_length)
        row6.addStretch()
        self.section1_layout.addLayout(row6)

        content_layout.addWidget(self.section1)

        # سکشن ۲: اطلاعات دکل‌ها
        self.section2 = QGroupBox("اطلاعات دکل‌ها")
        self.section2.setFont(self.font)
        self.section2.setStyleSheet("""
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
        self.section2_layout = QVBoxLayout()
        self.section2_layout.setContentsMargins(15, 10, 15, 10)
        self.section2_layout.setSpacing(10)
        self.section2.setLayout(self.section2_layout)

        # ردیف ۱: تعداد کل دکل‌ها و دکل‌های کششی
        self.total_towers = QLineEdit()
        self.total_towers.setFont(self.font)
        self.total_towers.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.total_towers.setFixedWidth(widget_width)
        self.tension_towers = QLineEdit()
        self.tension_towers.setFont(self.font)
        self.tension_towers.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.tension_towers.setFixedWidth(widget_width)
        row7 = QHBoxLayout()
        label7_1 = QLabel("تعداد کل دکل‌ها:", font=self.font)
        label7_1.setFixedWidth(label_width)
        label7_1.setStyleSheet("background-color: #F5F5F5;")
        row7.addWidget(label7_1)
        row7.addWidget(self.total_towers)
        row7.addSpacing(20)
        label7_2 = QLabel("دکل‌های کششی:", font=self.font)
        label7_2.setFixedWidth(label_width)
        label7_2.setStyleSheet("background-color: #F5F5F5;")
        row7.addWidget(label7_2)
        row7.addWidget(self.tension_towers)
        row7.addStretch()
        self.section2_layout.addLayout(row7)

        # ردیف ۲: دکل‌های آویزی
        self.suspension_towers = QLineEdit()
        self.suspension_towers.setFont(self.font)
        self.suspension_towers.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.suspension_towers.setFixedWidth(widget_width)
        row8 = QHBoxLayout()
        label8_1 = QLabel("دکل‌های آویزی:", font=self.font)
        label8_1.setFixedWidth(label_width)
        label8_1.setStyleSheet("background-color: #F5F5F5;")
        row8.addWidget(label8_1)
        row8.addWidget(self.suspension_towers)
        row8.addStretch()
        self.section2_layout.addLayout(row8)

        content_layout.addWidget(self.section2)

        # سکشن ۳: موقعیت دکل‌ها
        self.section3 = QGroupBox("موقعیت دکل‌ها")
        self.section3.setFont(self.font)
        self.section3.setStyleSheet("""
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
        self.section3_layout = QVBoxLayout()
        self.section3_layout.setContentsMargins(15, 10, 15, 10)
        self.section3_layout.setSpacing(10)
        self.section3.setLayout(self.section3_layout)

        # ردیف جدید: دشت، نيمه کوهستاني، صعب‌العبور در یک ردیف
        small_width = 50  # کاهش عرض برای جلوگیری از اسکرول افقی
        self.plain_area = QLineEdit()
        self.plain_area.setFont(self.font)
        self.plain_area.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.plain_area.setFixedWidth(small_width)
        self.semi_mountainous_area = QLineEdit()
        self.semi_mountainous_area.setFont(self.font)
        self.semi_mountainous_area.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.semi_mountainous_area.setFixedWidth(small_width)
        self.rough_terrain_area = QLineEdit()
        self.rough_terrain_area.setFont(self.font)
        self.rough_terrain_area.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: white;")
        self.rough_terrain_area.setFixedWidth(small_width)
        row9 = QHBoxLayout()
        label9_1 = QLabel("دشت:", font=self.font)
        label9_1.setFixedWidth(label_width)
        label9_1.setStyleSheet("background-color: #F5F5F5;")
        row9.addWidget(label9_1)
        row9.addWidget(self.plain_area)
        row9.addSpacing(20)
        label9_2 = QLabel("نيمه کوهستاني:", font=self.font)
        label9_2.setFixedWidth(label_width)
        label9_2.setStyleSheet("background-color: #F5F5F5;")
        row9.addWidget(label9_2)
        row9.addWidget(self.semi_mountainous_area)
        row9.addSpacing(20)
        label9_3 = QLabel("صعب العبور:", font=self.font)
        label9_3.setFixedWidth(label_width)
        label9_3.setStyleSheet("background-color: #F5F5F5;")
        row9.addWidget(label9_3)
        row9.addWidget(self.rough_terrain_area)
        row9.addStretch()
        self.section3_layout.addLayout(row9)

        content_layout.addWidget(self.section3)

        # سکشن ۴: اطلاعات اشخاص
        self.section4 = QGroupBox("اطلاعات اشخاص")
        self.section4.setFont(self.font)
        self.section4.setStyleSheet("""
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
        self.section4_layout = QVBoxLayout()
        self.section4_layout.setContentsMargins(15, 10, 15, 10)
        self.section4_layout.setSpacing(10)
        self.section4.setLayout(self.section4_layout)

        # ردیف ۱: سرپرست خط و کارشناس خط
        self.team_leader = NoWheelComboBox()
        self.team_leader.setFont(self.font)
        self.team_leader.setStyleSheet(combo_rtl_style)
        self.team_leader.setFixedWidth(widget_width)
        self.line_expert = NoWheelComboBox()
        self.line_expert.setFont(self.font)
        self.line_expert.setStyleSheet(combo_rtl_style)
        self.line_expert.setFixedWidth(widget_width)
        row12 = QHBoxLayout()
        label12_1 = QLabel("سرپرست خط:", font=self.font)
        label12_1.setFixedWidth(label_width)
        label12_1.setStyleSheet("background-color: #F5F5F5;")
        row12.addWidget(label12_1)
        row12.addWidget(self.team_leader)
        row12.addSpacing(20)
        label12_2 = QLabel("کارشناس خط:", font=self.font)
        label12_2.setFixedWidth(label_width)
        label12_2.setStyleSheet("background-color: #F5F5F5;")
        row12.addWidget(label12_2)
        row12.addWidget(self.line_expert)
        row12.addStretch()
        self.section4_layout.addLayout(row12)

        content_layout.addWidget(self.section4)

        # پر کردن ComboBoxهای سرپرست و کارشناس
        self.load_team_members()

        # پر کردن فیلدها در حالت ویرایش
        if line_data:
            self.line_code.setText(str(line_data.get('Line_Code', '')))
            self.voltage.setCurrentText(str(line_data.get('Voltage', '')))
            self.line_name.setText(str(line_data.get('Line_Name', '')))
            self.dispatch_code.setText(str(line_data.get('Dispatch_Code', '')))
            self.circuit_number.setCurrentText(str(line_data.get('Circuit_Number', '')))
            self.bundle_number.setCurrentText(str(line_data.get('Bundle_Number', '')))
            self.line_length.setText(str(line_data.get('Line_Length', '')))
            self.circuit_length.setText(str(line_data.get('Circuit_Length', '')))
            self.tower_type.setCurrentText(str(line_data.get('Tower_Type', '')))
            self.wire_type.setCurrentText(str(line_data.get('Wire_Type', '')))
            self.total_towers.setText(str(line_data.get('Total_Towers', '')))
            self.tension_towers.setText(str(line_data.get('Tension_Towers', '')))
            self.suspension_towers.setText(str(line_data.get('Suspension_Towers', '')))
            self.plain_area.setText(str(line_data.get('Plain_Area', '')))
            self.semi_mountainous_area.setText(str(line_data.get('Semi_Mountainous_Area', '')))
            self.rough_terrain_area.setText(str(line_data.get('Rough_Terrain_Area', '')))
            self.operation_year.setText(str(line_data.get('Operation_Year', '')))
            self.team_leader.setCurrentText(str(line_data.get('Team_Leader', '')))
            self.line_expert.setCurrentText(str(line_data.get('Line_Expert', '')))

        # اتصال سیگنال‌ها
        self.save_button.clicked.connect(self.save_line)
        self.cancel_button.clicked.connect(self.reject)

        # اشاره‌گر موس برای دکمه‌های ذخیره و لغو
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        


    def mousePressEvent(self, event):
        """برای جابجایی دیالوگ"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """برای جابجایی دیالوگ"""
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """برای جابجایی دیالوگ"""
        if event.button() == Qt.LeftButton:
            self.dragging = False





    def load_team_members(self):
        try:
            # سرپرست خط: فقط افراد با پست سرپرست اکیپ
            query_leader = "SELECT DISTINCT first_name || ' ' || last_name FROM teams WHERE position = ? AND first_name IS NOT NULL AND last_name IS NOT NULL"
            leaders = self.db.fetch_all(query_leader, ("سرپرست اکیپ",))
            # کارشناس خط: فقط افراد با پست کارشناس خط
            query_expert = "SELECT DISTINCT first_name || ' ' || last_name FROM teams WHERE position = ? AND first_name IS NOT NULL AND last_name IS NOT NULL"
            experts = self.db.fetch_all(query_expert, ("کارشناس خط",))
            self.team_leader.clear()
            self.line_expert.clear()
            self.team_leader.addItem("")
            self.line_expert.addItem("")
            for row in leaders:
                self.team_leader.addItem(row[0])
            for row in experts:
                self.line_expert.addItem(row[0])
        except Exception as e:
            logging.error(f"Error in load_team_members: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری پرسنل: {str(e)}")

    def validate_inputs(self):
        try:
            if not self.line_code.text():
                return False, "کد خط اجباری است!"
            if not self.line_name.text():
                return False, "نام خط اجباری است!"
            if self.circuit_number.currentText() and not re.match(r"^\d+$", self.circuit_number.currentText()):
                return False, "تعداد مدار باید عدد صحیح باشد!"
            if self.bundle_number.currentText() and not re.match(r"^\d+$", self.bundle_number.currentText()):
                return False, "تعداد باندل باید عدد صحیح باشد!"
            if self.total_towers.text() and not re.match(r"^\d+$", self.total_towers.text()):
                return False, "تعداد کل دکل‌ها باید عدد صحیح باشد!"
            if self.tension_towers.text() and not re.match(r"^\d+$", self.tension_towers.text()):
                return False, "تعداد دکل‌های کششی باید عدد صحیح باشد!"
            if self.suspension_towers.text() and not re.match(r"^\d+$", self.suspension_towers.text()):
                return False, "تعداد دکل‌های آویزی باید عدد صحیح باشد!"
            if self.plain_area.text() and not re.match(r"^\d*\.?\d*$", self.plain_area.text()):
                return False, "دشت باید عدد باشد!"
            if self.semi_mountainous_area.text() and not re.match(r"^\d+$", self.semi_mountainous_area.text()):
                return False, "نيمه کوهستاني باید عدد صحیح باشد!"
            if self.rough_terrain_area.text() and not re.match(r"^\d+$", self.rough_terrain_area.text()):
                return False, "منطقه صعب‌العبور باید عدد صحیح باشد!"
            if self.operation_year.text() and not re.match(r"^\d{4}$", self.operation_year.text()):
                return False, "سال بهره‌برداری باید عدد چهار رقمی باشد!"
            try:
                existing_codes = self.db.fetch_all(
                    "SELECT Line_Code FROM lines WHERE Line_Code != ? AND id != ?",
                    (self.line_code.text(), self.current_id or -1)
                )
            except Exception as e:
                dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در بررسی یکتایی کد خط: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
                dlg.exec_()
                return False, "خطا در بررسی یکتایی کد خط"
            if existing_codes and self.line_code.text() in [code[0] for code in existing_codes]:
                return False, "کد خط باید یکتا باشد!"
            try:
                existing_names = self.db.fetch_all(
                    "SELECT Line_Name FROM lines WHERE Line_Name != ? AND id != ?",
                    (self.line_name.text(), self.current_id or -1)
                )
            except Exception as e:
                dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در بررسی یکتایی نام خط: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
                dlg.exec_()
                return False, "خطا در بررسی یکتایی نام خط"
            if existing_names and self.line_name.text() in [name[0] for name in existing_names]:
                return False, "نام خط باید یکتا باشد!"
            return True, ""
        except Exception as e:
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطای غیرمنتظره در اعتبارسنجی: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()
            return False, "خطای غیرمنتظره در اعتبارسنجی"

    def save_line(self):

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

        self.line_data = {
            'Line_Code': self.line_code.text(),
            'Voltage': self.voltage.currentText(),
            'Line_Name': self.line_name.text(),
            'Dispatch_Code': self.dispatch_code.text(),
            'Circuit_Number': self.circuit_number.currentText(),
            'Bundle_Number': self.bundle_number.currentText(),
            'Line_Length': self.line_length.text(),
            'Circuit_Length': self.circuit_length.text(),
            'Tower_Type': self.tower_type.currentText(),
            'Wire_Type': self.wire_type.currentText(),
            'Total_Towers': self.total_towers.text(),
            'Tension_Towers': self.tension_towers.text(),
            'Suspension_Towers': self.suspension_towers.text(),
            'Plain_Area': format_number(self.plain_area.text()),
            'Semi_Mountainous_Area': format_number(self.semi_mountainous_area.text(), is_integer=True),
            'Rough_Terrain_Area': format_number(self.rough_terrain_area.text(), is_integer=True),
            'Operation_Year': self.operation_year.text(),
            'Team_Leader': self.team_leader.currentText(),
            'Line_Expert': self.line_expert.currentText(),
            'id': self.current_id
        }
        self.accept()

class LinesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)  # کاهش margins
        self.layout.setSpacing(10)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet("background-color: #F5F5F5;")

        self.column_filters = {}
        self.original_headers = [
            "کد خط", "ولتاژ", "نام خط", "کد دیسپاچینگ", "تعداد مدار", "تعداد باندل",
            "طول خط", "طول مدار", "نوع دکل", "نوع سیم", "تعداد کل دکل‌ها",
            "دکل‌های کششی", "دکل‌های آویزی", "دشت", "نيمه کوهستاني",
            "منطقه صعب‌العبور", "سال بهره‌برداری", "سرپرست خط", "کارشناس خط"
        ]
        self.column_names = [
            "Line_Code", "Voltage", "Line_Name", "Dispatch_Code", "Circuit_Number", "Bundle_Number",
            "Line_Length", "Circuit_Length", "Tower_Type", "Wire_Type", "Total_Towers",
            "Tension_Towers", "Suspension_Towers", "Plain_Area", "Semi_Mountainous_Area",
            "Rough_Terrain_Area", "Operation_Year", "Team_Leader", "Line_Expert"
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

        self.add_action = QAction(QIcon("resources/Icons/Add_Item.png"), "افزودن خط جدید", self)
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

        # تنظیم اشاره‌گر موس به حالت دست برای دکمه‌های نوار ابزار
        for action in [self.add_action, self.copy_action, self.delete_action, self.edit_action, self.import_excel_action, self.report_action, self.back_action]:
            btn = self.toolbar.widgetForAction(action)
            if btn is not None:
                btn.setCursor(Qt.PointingHandCursor)

        self.add_action.triggered.connect(self.add_line)
        self.copy_action.triggered.connect(lambda: self.safe_copy())
        self.delete_action.triggered.connect(self.delete_line)
        self.edit_action.triggered.connect(self.edit_line)
        self.import_excel_action.triggered.connect(self.import_from_excel)
        self.report_action.triggered.connect(self.generate_report)
        self.back_action.triggered.connect(self.close)

        # Table
        self.table = CustomTableWidget(
            table_name="lines",
            headers=self.original_headers,
            column_names=self.column_names,
            db=self.db
        )
        self.layout.addWidget(self.table, 1)  # stretch factor = 1
        self.table.table.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.table.table.customContextMenuRequested.connect(self.show_context_menu)  # حذف شد
        self.table.load_table()
        self.table._custom_edit_callback = self.edit_line
        self.table._custom_clear_filters_callback = self.clear_all_filters

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
            
            logging.debug("Lines window column filters cleared successfully")
        except Exception as e:
            logging.error(f"Error in clear_all_filters: {str(e)}", exc_info=True)

    def load_table(self, global_filter=""):
        try:
            query = """
                SELECT Line_Code, Voltage, Line_Name, Dispatch_Code, Circuit_Number, Bundle_Number,
                       Line_Length, Circuit_Length, Tower_Type, Wire_Type, Total_Towers,
                       Tension_Towers, Suspension_Towers, Plain_Area, Semi_Mountainous_Area,
                       Rough_Terrain_Area, Operation_Year, Team_Leader, Line_Expert, id
                FROM lines
            """
            params = []
            conditions = []
            if global_filter:
                conditions.append("""
                    (Line_Code LIKE ? OR Voltage LIKE ? OR Line_Name LIKE ? OR Dispatch_Code LIKE ?
                    OR Circuit_Number LIKE ? OR Bundle_Number LIKE ? OR Line_Length LIKE ?
                    OR Circuit_Length LIKE ? OR Tower_Type LIKE ? OR Wire_Type LIKE ?
                    OR Total_Towers LIKE ? OR Tension_Towers LIKE ? OR Suspension_Towers LIKE ?
                    OR Plain_Area LIKE ? OR Semi_Mountainous_Area LIKE ? OR Rough_Terrain_Area LIKE ?
                    OR Operation_Year LIKE ? OR Team_Leader LIKE ? OR Line_Expert LIKE ?)
                """)
                params.extend([f"%{global_filter}%"] * 19)
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
                    if col_idx in [13, 14, 15]:
                        try:
                            num = float(data)
                            if col_idx in [14, 15]:
                                data = str(int(num))
                            else:
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

    def add_line(self):
        dialog = LineInputDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            line_data = dialog.line_data
            try:
                self.db.execute_query(
                    """
                    INSERT INTO lines (Line_Code, Voltage, Line_Name, Dispatch_Code, Circuit_Number,
                                       Bundle_Number, Line_Length, Circuit_Length, Tower_Type,
                                       Wire_Type, Total_Towers, Tension_Towers, Suspension_Towers,
                                       Plain_Area, Semi_Mountainous_Area, Rough_Terrain_Area,
                                       Operation_Year, Team_Leader, Line_Expert)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        line_data['Line_Code'], line_data['Voltage'], line_data['Line_Name'],
                        line_data['Dispatch_Code'], line_data['Circuit_Number'], line_data['Bundle_Number'],
                        line_data['Line_Length'], line_data['Circuit_Length'], line_data['Tower_Type'],
                        line_data['Wire_Type'], line_data['Total_Towers'], line_data['Tension_Towers'],
                        line_data['Suspension_Towers'], line_data['Plain_Area'], line_data['Semi_Mountainous_Area'],
                        line_data['Rough_Terrain_Area'], line_data['Operation_Year'], line_data['Team_Leader'],
                        line_data['Line_Expert']
                    )
                )
                self.load_table()
                dlg = CustomDialog_Flexible(header_text="موفقیت", main_text="خط با موفقیت اضافه شد.", ok_text="باشه", parent=self)
                dlg.exec_()
            except Exception as e:
                logging.error(f"Error in add_line: {str(e)}")
                dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در افزودن خط: {str(e)}", ok_text="باشه", parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical)))
                dlg.exec_()

    def edit_line(self):
        selected = self.table.table.selectedItems()
        if not selected:
            # Use top-level import for CustomDialog_Flexible
            dlg = CustomDialog_Flexible(
                header_text="هشدار",
                main_text="لطفاً ابتدا خط مورد نظر را انتخاب کنید.",
                ok_text="باشه",
                parent=self,
                icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            )
            dlg.exec_()
            return
        row = self.table.table.currentRow()
        line_code = self.table.table.item(row, 0).text() if self.table.table.item(row, 0) else ""
        try:
            result = self.db.fetch_all("SELECT id FROM lines WHERE Line_Code=?", (line_code,))
            if not result:
                QMessageBox.critical(self, "خطا", "خط موردنظر یافت نشد!")
                return
            current_id = result[0][0]
            line_data = {
                'id': current_id,
                'Line_Code': line_code,
                'Voltage': self.table.table.item(row, 1).text() if self.table.table.item(row, 1) else "",
                'Line_Name': self.table.table.item(row, 2).text() if self.table.table.item(row, 2) else "",
                'Dispatch_Code': self.table.table.item(row, 3).text() if self.table.table.item(row, 3) else "",
                'Circuit_Number': self.table.table.item(row, 4).text() if self.table.table.item(row, 4) else "",
                'Bundle_Number': self.table.table.item(row, 5).text() if self.table.table.item(row, 5) else "",
                'Line_Length': self.table.table.item(row, 6).text() if self.table.table.item(row, 6) else "",
                'Circuit_Length': self.table.table.item(row, 7).text() if self.table.table.item(row, 7) else "",
                'Tower_Type': self.table.table.item(row, 8).text() if self.table.table.item(row, 8) else "",
                'Wire_Type': self.table.table.item(row, 9).text() if self.table.table.item(row, 9) else "",  
                'Total_Towers': self.table.table.item(row, 10).text() if self.table.table.item(row, 10) else "",
                'Tension_Towers': self.table.table.item(row, 11).text() if self.table.table.item(row, 11) else "",
                'Suspension_Towers': self.table.table.item(row, 12).text() if self.table.table.item(row, 12) else "",
                'Plain_Area': self.table.table.item(row, 13).text() if self.table.table.item(row, 13) else "",
                'Semi_Mountainous_Area': self.table.table.item(row, 14).text() if self.table.table.item(row, 14) else "",
                'Rough_Terrain_Area': self.table.table.item(row, 15).text() if self.table.table.item(row, 15) else "",
                'Operation_Year': self.table.table.item(row, 16).text() if self.table.table.item(row, 16) else "",
                'Team_Leader': self.table.table.item(row, 17).text() if self.table.table.item(row, 17) else "",
                'Line_Expert': self.table.table.item(row, 18).text() if self.table.table.item(row, 18) else ""
            }
            dialog = LineInputDialog(self, line_data, is_edit=True)
            if dialog.exec_() == QDialog.Accepted:
                line_data = dialog.line_data
                # بررسی تکراری نبودن Line_Code برای رکوردهای دیگر
                duplicate = self.db.fetch_all(
                    "SELECT id FROM lines WHERE Line_Code=? AND id<>?",
                    (line_data['Line_Code'], line_data['id'])
                )
                if duplicate:
                    dlg = CustomDialog_Flexible(header_text="خطا", main_text="کد خط وارد شده قبلاً برای خط دیگری ثبت شده است!", ok_text="باشه", parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical)))
                    dlg.exec_()
                    return
                try:
                    self.db.execute_query(
                        """
                        UPDATE lines SET Line_Code=?, Voltage=?, Line_Name=?, Dispatch_Code=?,
                                         Circuit_Number=?, Bundle_Number=?, Line_Length=?, Circuit_Length=?,
                                         Tower_Type=?, Wire_Type=?, Total_Towers=?, Tension_Towers=?,
                                         Suspension_Towers=?, Plain_Area=?, Semi_Mountainous_Area=?,
                                         Rough_Terrain_Area=?, Operation_Year=?, Team_Leader=?,
                                         Line_Expert=?
                        WHERE id=?
                        """,
                        (
                            line_data['Line_Code'], line_data['Voltage'], line_data['Line_Name'],
                            line_data['Dispatch_Code'], line_data['Circuit_Number'], line_data['Bundle_Number'],
                            line_data['Line_Length'], line_data['Circuit_Length'], line_data['Tower_Type'],
                            line_data['Wire_Type'], line_data['Total_Towers'], line_data['Tension_Towers'],
                            line_data['Suspension_Towers'], line_data['Plain_Area'], line_data['Semi_Mountainous_Area'],
                            line_data['Rough_Terrain_Area'], line_data['Operation_Year'], line_data['Team_Leader'],
                            line_data['Line_Expert'], line_data['id']
                        )
                    )
                    self.table.load_table()
                    dlg = CustomDialog_Flexible(header_text="موفقیت", main_text="خط با موفقیت ویرایش شد.", ok_text="باشه", parent=self)
                    dlg.exec_()
                except Exception as e:
                    logging.error(f"Error in edit_line: {str(e)}")
                    dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در ویرایش خط: {str(e)}", ok_text="باشه", parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical)))
                    dlg.exec_()
        except Exception as e:
            logging.error(f"Error in edit_line: {str(e)}")
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در ویرایش خط: {str(e)}", ok_text="باشه", parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical)))
            dlg.exec_()

    def safe_copy(self):
        """کپی کردن خط انتخاب شده - مشابه عملکرد کلیک راست"""
        try:
            TableActions.copy_selected(self.table.table, self.db, self, "lines", self.table.load_table)
        except Exception as e:
            logging.error(f"Exception in safe_copy: {str(e)}", exc_info=True)
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در کپی: {str(e)}", ok_text="باشه", parent=self)
            dlg.exec_()

    def delete_line(self):
        selected_rows = sorted(set(index.row() for index in self.table.table.selectedIndexes()))
        if not selected_rows:
            # Use top-level import for CustomDialog_Flexible
            dlg = CustomDialog_Flexible(
                header_text="هشدار",
                main_text="لطفاً ابتدا خط مورد نظر را انتخاب کنید.",
                ok_text="باشه",
                parent=self,
                icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            )
            dlg.exec_()
            return

        row_count = len(selected_rows)
        msg = f"آیا از حذف این {row_count} خط مطمئن هستید؟"
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
            progress = CustomDialog_Progress(header_text="در حال حذف خطوط...", cancel_text="لغو عملیات", parent=self)
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
            # ابتدا کدهای خطوط انتخاب شده را جمع‌آوری کنیم
            line_codes_to_delete = []
            for row in selected_rows:
                line_code = self.table.table.item(row, 0).text() if self.table.table.item(row, 0) else ""
                if line_code:
                    line_codes_to_delete.append(line_code)
            
            # حالا حذف را انجام دهیم
            for i, line_code in enumerate(line_codes_to_delete):
                try:
                    QApplication.processEvents()
                    if self.deletion_cancelled:
                        break
                    progress.set_progress(i + 1)
                    progress.set_text(f"{i+1} از {row_count}")
                    self.db.execute_query("DELETE FROM lines WHERE Line_Code=?", (line_code,))
                    deleted_count += 1
                except Exception as e:
                    logging.error(f"Error deleting line {line_code}: {str(e)}")
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
                msg = f"عملیات لغو شد و {deleted_count} خط تا این لحظه حذف شد."
                self.table.table.clearSelection()
                dlg = CustomDialog_Flexible(header_text="لغو عملیات", main_text=msg, ok_text="باشه", parent=self)
                dlg.exec_()
            elif deleted_count > 0:
                self.table.table.clearSelection()
                dlg = CustomDialog_Flexible(header_text="موفقیت", main_text=f"{deleted_count} خط با موفقیت حذف شد.", ok_text="باشه", parent=self)
                dlg.exec_()
        except Exception as e:
            logging.error(f"Error in delete_line: {str(e)}\n{traceback.format_exc()}")
            try:
                progress.close()
            except:
                pass
            self.table.table.clearSelection()
            QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")

    def load_row_data(self, row, col):
        pass

    def generate_report(self):
        try:
            rows = self.db.fetch_all("""
                SELECT Line_Code, Voltage, Line_Name, Dispatch_Code, Circuit_Number, Bundle_Number,
                       Line_Length, Circuit_Length, Tower_Type, Wire_Type, Total_Towers,
                       Tension_Towers, Suspension_Towers, Plain_Area, Semi_Mountainous_Area,
                       Rough_Terrain_Area, Operation_Year, Team_Leader, Line_Expert
                FROM lines
            """)
            import pandas as pd
            from PyQt5.QtWidgets import QFileDialog
            df = pd.DataFrame(rows, columns=self.original_headers)
            default_name = "Line_Report.xlsx"
            file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره گزارش خطوط", default_name, "Excel Files (*.xlsx)")
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
            existing_codes = self.db.fetch_all("SELECT Line_Code FROM lines")
            existing_code_set = {row[0] for row in existing_codes if row[0]}

            duplicate_names = []
            invalid_rows = []
            valid_rows = []
            seen_codes = set()
            for index, row in df.iterrows():
                line_code = str(row["کد خط"]).strip() if pd.notna(row["کد خط"]) else ""
                line_name = str(row["نام خط"]).strip() if pd.notna(row["نام خط"]) else ""
                # سطر نامعتبر: کد خط یا نام خط خالی
                if not line_code or not line_name:
                    invalid_rows.append(f"سطر {index+1}: کد خط یا نام خط خالی است")
                    continue
                # تکراری در دیتابیس یا فایل
                if line_code in existing_code_set or line_code in seen_codes:
                    duplicate_names.append(line_name)
                    continue
                seen_codes.add(line_code)
                valid_rows.append(row)

            error_messages = []
            if duplicate_names:
                summarized = '\n'.join(sorted(set(duplicate_names)))
                error_messages.append(f"نام خط تکراری ({len(duplicate_names)} مورد):\n{summarized}")
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
                    question_text="آیا می‌خواهید خطوط معتبر را وارد کنید؟",
                    parent=self
                )
                dlg.adjustSize()
                if dlg.exec_() != dlg.Accepted:
                    return
            if not valid_rows:
                dlg = CustomDialog_Flexible(header_text="هشدار", main_text="هیچ خط معتبری برای وارد کردن یافت نشد.", ok_text="باشه", cancel_text=None, parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning)))
                dlg.exec_()
                return
            inserted_count = 0
            progress = CustomDialog_Progress(header_text="در حال وارد کردن اطلاعات خطوط...", cancel_text="لغو عملیات", parent=self)
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
                line_code = str(row["کد خط"]) if pd.notna(row["کد خط"]) else ""
                self.db.execute_query(
                    """
                    INSERT INTO lines (Line_Code, Voltage, Line_Name, Dispatch_Code, Circuit_Number,
                                       Bundle_Number, Line_Length, Circuit_Length, Tower_Type,
                                       Wire_Type, Total_Towers, Tension_Towers, Suspension_Towers,
                                       Plain_Area, Semi_Mountainous_Area, Rough_Terrain_Area,
                                       Operation_Year, Team_Leader, Line_Expert)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        line_code, str(row["ولتاژ"]) if pd.notna(row["ولتاژ"]) else "",
                        str(row["نام خط"]) if pd.notna(row["نام خط"]) else "",
                        str(row["کد دیسپاچینگ"]) if pd.notna(row["کد دیسپاچینگ"]) else "",
                        str(row["تعداد مدار"]) if pd.notna(row["تعداد مدار"]) else "",
                        str(row["تعداد باندل"]) if pd.notna(row["تعداد باندل"]) else "",
                        str(row["طول خط"]) if pd.notna(row["طول خط"]) else "",
                        str(row["طول مدار"]) if pd.notna(row["طول مدار"]) else "",
                        str(row["نوع دکل"]) if pd.notna(row["نوع دکل"]) else "",
                        str(row["نوع سیم"]) if pd.notna(row["نوع سیم"]) else "",
                        str(row["تعداد کل دکل‌ها"]) if pd.notna(row["تعداد کل دکل‌ها"]) else "",
                        str(row["دکل‌های کششی"]) if pd.notna(row["دکل‌های کششی"]) else "",
                        str(row["دکل‌های آویزی"]) if pd.notna(row["دکل‌های آویزی"]) else "",
                        str(row["دشت"]) if pd.notna(row["دشت"]) else "",
                        str(row["نيمه کوهستاني"]) if pd.notna(row["نيمه کوهستاني"]) else "",
                        str(row["منطقه صعب‌العبور"]) if pd.notna(row["منطقه صعب‌العبور"]) else "",
                        str(row["سال بهره‌برداری"]) if pd.notna(row["سال بهره‌برداری"]) else "",
                        str(row["سرپرست خط"]) if pd.notna(row["سرپرست خط"]) else "",
                        str(row["کارشناس خط"]) if pd.notna(row["کارشناس خط"]) else ""
                    )
                )
                inserted_count += 1
            progress.accept()
            self.load_table()
            dlg = CustomDialog_Flexible(header_text="موفقیت", main_text=f"{inserted_count} خط با موفقیت وارد شد.", ok_text="باشه", parent=self)
            dlg.exec_()
        except Exception as e:
            logging.error(f"Error in import_from_excel: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در وارد کردن اطلاعات از اکسل: {str(e)}")
