from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QToolBar, QAction, QLineEdit, QHBoxLayout, QLabel, QMessageBox, QStyle, QDialog, QFormLayout, QPushButton, QFileDialog, QHeaderView, QSizePolicy, QMenu, QApplication, QProgressDialog, QScrollArea
from PyQt5.QtCore import Qt, QEvent, QPoint, QTimer
from PyQt5.QtCore import QSizeF
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtGui import QFontMetrics
from modules.database import Database
import csv
import re
import pandas as pd
import logging
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtGui import QTextDocument
from PyQt5.QtGui import QPainter
from bs4 import BeautifulSoup
from modules.custom_widgets import CustomDialog_Progress, CustomDialog_Flexible, CustomTableWidget, TableActions

# تنظیم لاگ برای دیباگ
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



class TeamInputDialog(QDialog):
    def __init__(self, parent=None, team_data=None, is_edit=False):
        super().__init__(parent)
        self.setWindowTitle("افزودن پرسنل" if not is_edit else "ویرایش پرسنل")
        self.setFixedSize(400, 500)
        self.setLayoutDirection(Qt.RightToLeft)
        self.is_edit = is_edit
        self.current_id = team_data.get('id') if team_data else None
        self.db = Database()

        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        font = QFont("Vazir", 12)
        input_style = "padding: 5px; border: 1px solid #ccc; background-color: white; border-radius: 5px;"

        self.national_code = QLineEdit()
        self.national_code.setFont(font)
        self.national_code.setStyleSheet(input_style)
        self.layout.addRow("کد ملی:", self.national_code)

        self.first_name = QLineEdit()
        self.first_name.setFont(font)
        self.first_name.setStyleSheet(input_style)
        self.layout.addRow("نام:", self.first_name)

        self.last_name = QLineEdit()
        self.last_name.setFont(font)
        self.last_name.setStyleSheet(input_style)
        self.layout.addRow("نام خانوادگی:", self.last_name)

        self.father_name = QLineEdit()
        self.father_name.setFont(font)
        self.father_name.setStyleSheet(input_style)
        self.layout.addRow("نام پدر:", self.father_name)

        self.position = QLineEdit()
        self.position.setFont(font)
        self.position.setStyleSheet(input_style)
        self.layout.addRow("پست:", self.position)

        self.hire_date = QLineEdit()
        self.hire_date.setFont(font)
        self.hire_date.setStyleSheet(input_style)
        self.hire_date.setPlaceholderText("YYYY/MM/DD")
        self.layout.addRow("تاریخ استخدام:", self.hire_date)

        self.phone_number = QLineEdit()
        self.phone_number.setFont(font)
        self.phone_number.setStyleSheet(input_style)
        self.layout.addRow("شماره همراه:", self.phone_number)

        self.team_leader = QLineEdit()
        self.team_leader.setFont(font)
        self.team_leader.setStyleSheet(input_style)
        self.layout.addRow("سرپرست:", self.team_leader)

        if team_data:
            self.national_code.setText(str(team_data.get('national_code', '')))
            self.first_name.setText(str(team_data.get('first_name', '')))
            self.last_name.setText(str(team_data.get('last_name', '')))
            self.father_name.setText(str(team_data.get('father_name', '')))
            self.position.setText(str(team_data.get('position', '')))
            self.hire_date.setText(str(team_data.get('hire_date', '')))
            self.phone_number.setText(str(team_data.get('phone_number', '')))
            self.team_leader.setText(str(team_data.get('team_leader', '')))

        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("ذخیره")
        self.save_button.setFont(font)
        self.save_button.setStyleSheet("padding: 8px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;")
        self.cancel_button = QPushButton("لغو")
        self.cancel_button.setFont(font)
        self.cancel_button.setStyleSheet("padding: 8px 20px; background-color: #f44336; color: white; border: none; border-radius: 5px;")
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addRow(self.button_layout)

        self.save_button.clicked.connect(self.save_team)
        self.cancel_button.clicked.connect(self.reject)

        # اشاره‌گر موس برای دکمه‌های ذخیره و لغو
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setCursor(Qt.PointingHandCursor)

    def validate_inputs(self):
        if not self.first_name.text():
            return False, "نام اجباری است!"
        if not self.last_name.text():
            return False, "نام خانوادگی اجباری است!"
        if not self.team_leader.text():
            return False, "سرپرست اجباری است!"
        if self.national_code.text() and not (self.national_code.text().isdigit() and len(self.national_code.text()) == 10):
            return False, "کد ملی باید ۱۰ رقم باشد!"
        if self.phone_number.text() and not (self.phone_number.text().isdigit() and len(self.phone_number.text()) == 11):
            return False, "شماره همراه باید ۱۱ رقم باشد!"
        if self.hire_date.text() and not re.match(r"^\d{4}/\d{2}/\d{2}$", self.hire_date.text()):
            return False, "تاریخ استخدام باید به فرمت YYYY/MM/DD باشد!"
        if self.national_code.text():
            existing_codes = self.db.fetch_all(
                "SELECT national_code FROM teams WHERE national_code != ? AND id != ?",
                (self.national_code.text(), self.current_id or -1)
            )
            if existing_codes and self.national_code.text() in [str(code[0]) for code in existing_codes]:
                return False, "کد ملی باید یکتا باشد!"
        return True, ""

    def save_team(self):
        is_valid, error_msg = self.validate_inputs()
        if not is_valid:
            dlg = CustomDialog_Flexible(
                header_text="خطا",
                main_text=error_msg,
                ok_text="باشه",
                parent=self,
                icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            )
            dlg.exec_()
            return

        self.team_data = {
            'national_code': self.national_code.text(),
            'first_name': self.first_name.text(),
            'last_name': self.last_name.text(),
            'father_name': self.father_name.text(),
            'position': self.position.text(),
            'hire_date': self.hire_date.text(),
            'phone_number': self.phone_number.text(),
            'team_leader': self.team_leader.text(),
            'id': self.current_id
        }
        self.accept()

class ReportPreviewDialog(QDialog):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.setWindowTitle("گزارش پرسنل پیمانکار - پیش‌نمایش چاپ")
        self.setMinimumSize(900, 700)
        self.resize(900, 700)
        self.setStyleSheet("background: white;")
        layout = QVBoxLayout(self)
        title = QLabel("""
            <div style='text-align:center;'>
                <h3 style='margin-bottom: 0; font-size: 16px; color: #222;'>گزارش پرسنل پیمانکار</h3>
                <hr style='border: 1px solid #aaa; margin: 10px 0 20px 0;'>
            </div>
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        # ساخت جدول HTML با همه ستون‌ها (ستون‌ها معکوس)
        html = """
        <style>
        table { border-collapse: collapse; width: 100vw !important; min-width: 100vw !important; font-family: Vazir, Tahoma, sans-serif; }
        th, td { border: 1px solid #888; padding: 8px 12px; text-align: center; font-size: 13px !important; }
        th { background: #e0e0e0; font-size: 14px !important; color: #222; }
        tr:nth-child(even) { background: #f9f9f9; }
        tr:hover { background: #e3f2fd; }
        caption { caption-side: top; font-size: 20px; margin-bottom: 10px; }
        @media print {
            html, body { width: 100vw; height: 100vh; margin: 0; padding: 0; }
            table { width: 100vw !important; min-width: 100vw !important; font-size: 13px !important; }
            th, td { font-size: 13px !important; padding: 8px 12px !important; }
        }
        </style>
        <table>
        <tr>
            <th>سرپرست</th>
            <th>شماره همراه</th>
            <th>تاریخ شروع همکاری</th>
            <th>پست</th>
            <th>نام پدر</th>
            <th>نام خانوادگی</th>
            <th>نام</th>
            <th>کد ملی</th>
        </tr>
        """
        for row in data:
            html += f"<tr>"
            html += f"<td>{row[7]}</td>"  # سرپرست
            html += f"<td>{row[6]}</td>"  # شماره همراه
            html += f"<td>{row[5]}</td>"  # تاریخ شروع همکاری
            html += f"<td>{row[4]}</td>"  # پست
            html += f"<td>{row[3]}</td>"  # نام پدر
            html += f"<td>{row[2]}</td>"  # نام خانوادگی
            html += f"<td>{row[1]}</td>"  # نام
            html += f"<td>{row[0]}</td>"  # کد ملی
            html += "</tr>"
        html += "</table>"
        self.doc = QTextDocument()
        self.doc.setHtml(html)
        # پیش‌نمایش در QLabel با QScrollArea
        preview = QLabel()
        preview.setTextInteractionFlags(Qt.TextSelectableByMouse)
        preview.setText(self.doc.toHtml())
        preview.setStyleSheet("font-family: Vazir, Tahoma, sans-serif; font-size: 13px; background: white;")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.addWidget(preview)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        # دکمه پرینت و بستن
        btn_layout = QHBoxLayout()
        print_btn = QPushButton("پرینت گزارش")
        close_btn = QPushButton("بستن")
        print_btn.setStyleSheet("padding: 10px 32px; font-size: 18px; background: #1976D2; color: white; border-radius: 8px; font-family: Vazir;")
        close_btn.setStyleSheet("padding: 10px 32px; font-size: 18px; background: #f44336; color: white; border-radius: 8px; font-family: Vazir;")
        btn_layout.addStretch()
        btn_layout.addWidget(print_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        print_btn.clicked.connect(self.print_report)
        close_btn.clicked.connect(self.reject)
    def print_report(self):
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOrientation(QPrinter.Landscape)
            printer.setPaperSize(QPrinter.A4)
            printer.setFullPage(True)
            printer.setDocName("Persons_Report.pdf")
            dialog = QPrintDialog(printer, self)
            if dialog.exec_() == QPrintDialog.Accepted:
                painter = QPainter(printer)
                page_rect = printer.pageRect()
                margin = int(2 / 2.54 * printer.resolution())  # 2cm margin
                usable_width = page_rect.width() - 2 * margin
                usable_height = page_rect.height() - 2 * margin
                headers = ["سرپرست", "شماره همراه", "تاریخ شروع همکاری", "پست", "نام پدر", "نام خانوادگی", "نام", "کد ملی"]
                rows = []
                for row in self.parent().db.fetch_all("""
                    SELECT national_code, first_name, last_name, father_name, position, hire_date, phone_number, team_leader FROM teams
                """):
                    rows.append([
                        str(row[7]), str(row[6]), str(row[5]), str(row[4]), str(row[3]), str(row[2]), str(row[1]), str(row[0])
                    ])
                font = QFont("Vazir", 12)
                painter.setFont(font)
                metrics = painter.fontMetrics()
                col_widths = []
                min_col_width = 120  # حداقل عرض هر ستون
                for col in range(len(headers)):
                    max_width = metrics.width(headers[col])
                    for row in rows:
                        if col < len(row):
                            max_width = max(max_width, metrics.width(row[col]))
                    col_widths.append(max(max_width + 48, min_col_width))  # padding بیشتر و حداقل عرض
                total_width = sum(col_widths)
                if total_width == 0:
                    QMessageBox.critical(self, "خطا", "جدول برای چاپ خالی است یا مشکلی در داده‌ها وجود دارد.")
                    painter.end()
                    return
                scale = usable_width / total_width
                col_widths = [int(w * scale) for w in col_widths]
                diff = usable_width - sum(col_widths)
                if diff != 0:
                    col_widths[-1] += diff
                total_width = sum(col_widths)
                row_height = metrics.height() + 20
                header_height = row_height + 6
                y = page_rect.y() + margin
                x = page_rect.x() + margin  # جدول از ابتدای usable_width شروع شود
                title_font = QFont("Vazir", 16, QFont.Bold)
                title_metrics = QFont("Vazir", 16, QFont.Bold)
                title_height = painter.fontMetrics().height() + 30

                rows_per_page = (usable_height - header_height - 30) // row_height
                if rows_per_page < 1:
                    rows_per_page = 1
                total_pages = (len(rows) + rows_per_page - 1) // rows_per_page

                for page in range(total_pages):
                    if page > 0:
                        printer.newPage()
                        y = page_rect.y() + margin
                    # هدر جدول
                    col_x = x
                    painter.setPen(Qt.black)
                    for i, header in enumerate(headers):
                        painter.setBrush(Qt.white)
                        painter.setPen(Qt.black)
                        painter.drawRect(col_x, y, col_widths[i], header_height)
                        painter.fillRect(col_x, y, col_widths[i], header_height, Qt.lightGray)
                        text_rect = painter.boundingRect(col_x, y, col_widths[i], header_height, Qt.AlignCenter, header)
                        painter.drawText(text_rect, Qt.AlignCenter, header)
                        col_x += col_widths[i]
                    y += header_height
                    # ردیف‌های جدول
                    start_row = page * rows_per_page
                    end_row = min(start_row + rows_per_page, len(rows))
                    for row in rows[start_row:end_row]:
                        col_x = x
                        for i, cell in enumerate(row):
                            painter.setBrush(Qt.white)
                            painter.setPen(Qt.black)
                            painter.drawRect(col_x, y, col_widths[i], row_height)
                            painter.fillRect(col_x, y, col_widths[i], row_height, Qt.white)
                            text_rect = painter.boundingRect(col_x, y, col_widths[i], row_height, Qt.AlignCenter, cell)
                            painter.drawText(text_rect, Qt.AlignCenter, cell)
                            col_x += col_widths[i]
                        y += row_height
                    # جدول‌بندی خطوط افقی و عمودی
                    table_top = page_rect.y() + margin + (0)
                    table_left = x
                    table_bottom = y
                    table_right = x + total_width
                    painter.setPen(Qt.black)
                    # خطوط افقی
                    row_count = end_row - start_row
                    for i in range(row_count + 2):  # +2 برای هدر و آخرین خط
                        y_line = table_top + i * row_height if i > 0 else table_top
                        painter.drawLine(table_left, y_line, table_right, y_line)
                    # خطوط عمودی
                    col_x = table_left
                    for w in col_widths:
                        painter.drawLine(col_x, table_top, col_x, table_bottom)
                        col_x += w
                    painter.drawLine(table_right, table_top, table_right, table_bottom)
                    # شماره صفحه پایین هر صفحه
                    page_num_text = f" صفحه {page+1} از {total_pages}"
                    painter.setFont(QFont("Vazir", 11))
                    page_num_rect = painter.boundingRect(page_rect.x(), page_rect.bottom() - margin//2 - 10, page_rect.width(), 30, Qt.AlignCenter, page_num_text)
                    painter.drawText(page_num_rect, Qt.AlignCenter, page_num_text)
                painter.end()
        except Exception as e:
            import traceback
            logging.error(f"Error in print_report: {str(e)}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطا", f"خطا در پرینت گزارش: {str(e)}")

class TeamsWindow(QWidget):
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
            "کد ملی", "نام", "نام خانوادگی", "نام پدر", "پست", "تاریخ استخدام", "شماره همراه", "سرپرست"
        ]
        self.column_names = [
            "national_code", "first_name", "last_name", "father_name", "position", "hire_date", "phone_number", "team_leader"
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

        self.add_action = QAction(QIcon("resources/Icons/Add_Item.png"), "افزودن پرسنل جدید", self)
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

        self.add_action.triggered.connect(self.add_team_member)
        self.copy_action.triggered.connect(lambda: self.safe_copy())
        self.delete_action.triggered.connect(self.delete_team_member)
        self.edit_action.triggered.connect(self.edit_team_member)
        self.import_excel_action.triggered.connect(self.import_from_excel)
        self.report_action.triggered.connect(self.generate_report)
        self.back_action.triggered.connect(self.close)

        # Table
        self.table = CustomTableWidget(
            table_name="teams",
            headers=self.original_headers,
            column_names=self.column_names,
            db=self.db
        )
        self.layout.addWidget(self.table, 1)  # stretch factor = 1
        self.table.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.load_table()
        self.table._custom_edit_callback = self.edit_team_member
        self.table._custom_clear_filters_callback = self.clear_all_filters

    def clear_all_filters(self):
        """حذف تمام فیلترهای ستون‌ها"""
        try:
            # پاک کردن فیلترهای ستون‌ها
            self.column_filters.clear()
            
            # بارگذاری مجدد جدول
            self.table.load_table()
            
            logging.debug("Teams window column filters cleared successfully")
        except Exception as e:
            logging.error(f"Error in clear_all_filters: {str(e)}", exc_info=True)



    def add_team_member(self):
        dialog = TeamInputDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            team_data = dialog.team_data
            try:
                # بررسی یکتایی کد ملی قبل از درج
                if team_data['national_code']:
                    existing = self.db.fetch_all(
                        "SELECT 1 FROM teams WHERE national_code=?",
                        (team_data['national_code'],)
                    )
                    if existing:
                        dlg = CustomDialog_Flexible(
                            header_text="خطا",
                            main_text="کد ملی وارد شده قبلاً ثبت شده است و باید یکتا باشد.",
                            ok_text="باشه",
                            parent=self,
                            icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                        )
                        dlg.exec_()
                        return
                self.db.execute_query(
                    """
                    INSERT INTO teams (national_code, first_name, last_name, father_name,
                                       position, hire_date, phone_number, team_leader)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        team_data['national_code'], team_data['first_name'], team_data['last_name'],
                        team_data['father_name'], team_data['position'], team_data['hire_date'],
                        team_data['phone_number'], team_data['team_leader']
                    )
                )
                self.table.load_table()
                dlg = CustomDialog_Flexible(
                    header_text="موفقیت",
                    main_text="پرسنل با موفقیت اضافه شد.",
                    ok_text="باشه",
                    parent=self
                )
                dlg.exec_()
            except Exception as e:
                logging.error(f"Error in add_team: {str(e)}")
                dlg = CustomDialog_Flexible(
                    header_text="خطا",
                    main_text=f"خطا در افزودن پرسنل: {str(e)}",
                    ok_text="باشه",
                    parent=self,
                    icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical))
                )
                dlg.exec_()

    def edit_team_member(self):
        selected = self.table.table.selectedItems()
        if not selected:
            dlg = CustomDialog_Flexible(
                header_text="هشدار",
                main_text="لطفاً ابتدا پرسنل مورد نظر را انتخاب کنید.",
                ok_text="باشه",
                parent=self,
                icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            )
            dlg.exec_()
            return
        row = self.table.table.currentRow()
        national_code = self.table.table.item(row, 0).text() if self.table.table.item(row, 0) else ""
        try:
            result = self.db.fetch_all(
                "SELECT id FROM teams WHERE national_code=?",
                (national_code,)
            )
            if not result:
                dlg = CustomDialog_Flexible(
                    header_text="خطا",
                    main_text="پرسنل موردنظر یافت نشد!",
                    ok_text="باشه",
                    parent=self,
                    icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical))
                )
                dlg.exec_()
                return
            current_id = result[0][0]
            team_data = {
                'id': current_id,
                'national_code': national_code,
                'first_name': self.table.table.item(row, 1).text() if self.table.table.item(row, 1) else "",
                'last_name': self.table.table.item(row, 2).text() if self.table.table.item(row, 2) else "",
                'father_name': self.table.table.item(row, 3).text() if self.table.table.item(row, 3) else "",
                'position': self.table.table.item(row, 4).text() if self.table.table.item(row, 4) else "",
                'hire_date': self.table.table.item(row, 5).text() if self.table.table.item(row, 5) else "",
                'phone_number': self.table.table.item(row, 6).text() if self.table.table.item(row, 6) else "",
                'team_leader': self.table.table.item(row, 7).text() if self.table.table.item(row, 7) else ""
            }
            dialog = TeamInputDialog(self, team_data, is_edit=True)
            if dialog.exec_() == QDialog.Accepted:
                team_data = dialog.team_data
                self.db.execute_query(
                    """
                    UPDATE teams SET national_code=?, first_name=?, last_name=?, father_name=?,
                                     position=?, hire_date=?, phone_number=?, team_leader=?
                    WHERE id=?
                    """,
                    (
                        team_data['national_code'], team_data['first_name'], team_data['last_name'],
                        team_data['father_name'], team_data['position'], team_data['hire_date'],
                        team_data['phone_number'], team_data['team_leader'], team_data['id']
                    )
                )
                self.table.load_table()
                dlg = CustomDialog_Flexible(
                    header_text="موفقیت",
                    main_text="پرسنل با موفقیت ویرایش شد.",
                    ok_text="باشه",
                    parent=self
                )
                dlg.exec_()
        except Exception as e:
            logging.error(f"Error in edit_team: {str(e)}")
            dlg = CustomDialog_Flexible(
                header_text="خطا",
                main_text=f"خطا در ویرایش پرسنل: {str(e)}",
                ok_text="باشه",
                parent=self,
                icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            )
            dlg.exec_()

    def safe_copy(self):
        """کپی کردن پرسنل انتخاب شده - مشابه عملکرد کلیک راست"""
        try:
            TableActions.copy_selected(self.table.table, self.db, self, "teams", self.table.load_table)
        except Exception as e:
            logging.error(f"Exception in safe_copy: {str(e)}", exc_info=True)
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در کپی: {str(e)}", ok_text="باشه", parent=self)
            dlg.exec_()

    def delete_team_member(self):
        selected_items = self.table.table.selectedItems()
        if not selected_items:
            dlg = CustomDialog_Flexible(
                header_text="هشدار",
                main_text="لطفاً ابتدا پرسنل مورد نظر را انتخاب کنید.",
                ok_text="باشه",
                parent=self,
                icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            )
            dlg.exec_()
            return
        selected_rows = sorted(set(item.row() for item in selected_items))
        row_count = len(selected_rows)
        msg = f"آیا از حذف این {row_count} پرسنل مطمئن هستید؟"
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
            progress = CustomDialog_Progress(header_text="در حال حذف پرسنل...", cancel_text="لغو عملیات", parent=self)
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
            # جمع‌آوری کد ملی پرسنل انتخاب شده
            codes_to_delete = []
            for row in selected_rows:
                national_code = self.table.table.item(row, 0).text() if self.table.table.item(row, 0) else ""
                if national_code:
                    codes_to_delete.append(national_code)
            for i, national_code in enumerate(codes_to_delete):
                try:
                    QApplication.processEvents()
                    if self.deletion_cancelled:
                        break
                    progress.set_progress(i + 1)
                    progress.set_text(f"{i+1} از {row_count}")
                    self.db.execute_query("DELETE FROM teams WHERE national_code=?", (national_code,))
                    deleted_count += 1
                except Exception as e:
                    logging.error(f"Error deleting team {national_code}: {str(e)}")
                    continue
            try:
                progress.close()
            except:
                pass
            try:
                self.table.load_table()
            except Exception as e:
                logging.error(f"Error in load_table after deletion: {str(e)}")
            if self.deletion_cancelled:
                msg = f"عملیات لغو شد و {deleted_count} پرسنل تا این لحظه حذف شد."
                self.table.table.clearSelection()
                dlg = CustomDialog_Flexible(header_text="لغو عملیات", main_text=msg, ok_text="باشه", parent=self)
                dlg.exec_()
            elif deleted_count > 0:
                self.table.table.clearSelection()
                dlg = CustomDialog_Flexible(header_text="موفقیت", main_text=f"{deleted_count} پرسنل با موفقیت حذف شد.", ok_text="باشه", parent=self)
                dlg.exec_()
        except Exception as e:
            logging.error(f"Error in delete_team: {str(e)}")
            try:
                progress.close()
            except:
                pass
            self.table.table.clearSelection()
            QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")

    def load_row_data(self, row, col):
        """برای سازگاری با CustomTableWidget"""
        pass

    def generate_report(self):
        try:
            rows = self.db.fetch_all("""
                SELECT national_code, first_name, last_name, father_name,
                       position, hire_date, phone_number, team_leader
                FROM teams
            """)
            import pandas as pd
            from PyQt5.QtWidgets import QFileDialog
            df = pd.DataFrame(rows, columns=self.original_headers)
            default_name = "Teams_Report.xlsx"
            file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره گزارش پرسنل", default_name, "Excel Files (*.xlsx)")
            if not file_path:
                return
            if not file_path.endswith(".xlsx"):
                file_path += ".xlsx"
            df.to_excel(file_path, index=False)
            from modules.custom_widgets import CustomDialog_Flexible
            dlg = CustomDialog_Flexible(header_text="موفقیت", main_text=f"گزارش با نام {file_path} ذخیره شد.", ok_text="باشه", cancel_text=None, parent=self)
            dlg.exec_()
        except Exception as e:
            import logging
            logging.error(f"Error in generate_report: {str(e)}")
            from modules.custom_widgets import CustomDialog_Flexible
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

            existing_codes = self.db.fetch_all("SELECT national_code FROM teams")
            existing_code_set = {str(row[0]) for row in existing_codes if row[0]}

            duplicate_codes = []
            invalid_rows = []
            valid_rows = []
            seen_codes = set()
            for index, row in df.iterrows():
                national_code = str(row["کد ملی"]).strip() if pd.notna(row["کد ملی"]) else ""
                first_name = str(row["نام"]).strip() if pd.notna(row["نام"]) else ""
                last_name = str(row["نام خانوادگی"]).strip() if pd.notna(row["نام خانوادگی"]) else ""
                # سطر نامعتبر: کد ملی یا نام یا نام خانوادگی خالی
                if not national_code or not first_name or not last_name:
                    invalid_rows.append(f"سطر {index+1}: کد ملی یا نام یا نام خانوادگی خالی است")
                    continue
                # تکراری در دیتابیس یا فایل
                if national_code in existing_code_set or national_code in seen_codes:
                    duplicate_codes.append(national_code)
                    continue
                seen_codes.add(national_code)
                valid_rows.append(row)

            error_messages = []
            if duplicate_codes:
                summarized = ', '.join(sorted(set(duplicate_codes)))
                error_messages.append(f"کد ملی تکراری ({len(duplicate_codes)} مورد):\n{summarized}")
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
                    question_text="آیا می‌خواهید پرسنل معتبر را وارد کنید؟",
                    parent=self
                )
                dlg.adjustSize()
                if dlg.exec_() != dlg.Accepted:
                    return
            if not valid_rows:
                dlg = CustomDialog_Flexible(header_text="هشدار", main_text="هیچ پرسنل معتبری برای وارد کردن یافت نشد.", ok_text="باشه", cancel_text=None, parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning)))
                dlg.exec_()
                return
            inserted_count = 0
            progress = CustomDialog_Progress(header_text="در حال وارد کردن اطلاعات پرسنل...", cancel_text="لغو عملیات", parent=self)
            progress.set_maximum(len(valid_rows))
            progress.set_progress(0)
            progress.set_text(f"0 از {len(valid_rows)}")
            progress.show()
            QApplication.processEvents()
            self.import_cancelled = False
            def cancel():
                self.import_cancelled = True
            progress.cancel_btn.clicked.connect(cancel)
            for i, row in enumerate(valid_rows):
                QApplication.processEvents()
                if self.import_cancelled:
                    break
                progress.set_progress(i + 1)
                progress.set_text(f"{i+1} از {len(valid_rows)}")
                national_code = str(row["کد ملی"]) if pd.notna(row["کد ملی"]) else ""
                self.db.execute_query(
                    """
                    INSERT INTO teams (national_code, first_name, last_name, father_name,
                                       position, hire_date, phone_number, team_leader)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        national_code,
                        str(row["نام"]) if pd.notna(row["نام"]) else "",
                        str(row["نام خانوادگی"]) if pd.notna(row["نام خانوادگی"]) else "",
                        str(row["نام پدر"]) if pd.notna(row["نام پدر"]) else "",
                        str(row["پست"]) if pd.notna(row["پست"]) else "",
                        str(row["تاریخ شروع همکاری"]) if pd.notna(row["تاریخ شروع همکاری"]) else "",
                        str(row["شماره همراه"]) if pd.notna(row["شماره همراه"]) else "",
                        str(row["سرپرست"]) if pd.notna(row["سرپرست"]) else ""
                    )
                )
                inserted_count += 1
            progress.accept()
            self.table.load_table()
            msg = f"{inserted_count} پرسنل با موفقیت وارد شد."
            dlg = CustomDialog_Flexible(header_text="موفقیت", main_text=msg, ok_text="باشه", parent=self)
            dlg.exec_()
        except Exception as e:
            logging.error(f"Error in import_from_excel: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در وارد کردن اطلاعات از اکسل: {str(e)}")

    def show_context_menu(self, position):
        """منوی راست کلیک - برای سازگاری با CustomTableWidget"""
        from modules.custom_widgets import CustomRightClick
        menu = CustomRightClick(self)
        menu.deleteRequested.connect(self.delete_team_member)
        menu.editRequested.connect(self.edit_team_member)
        menu.copyRequested.connect(self.copy_selected_cells)
        global_pos = self.table.table.viewport().mapToGlobal(position)
        menu.show_at(global_pos, self)

    def copy_selected_cells(self):
        """کپی سلول‌های انتخاب شده - برای سازگاری با CustomTableWidget"""
        selected_items = self.table.table.selectedItems()
        if not selected_items:
            return
        rows = sorted(set(item.row() for item in selected_items))
        cols = sorted(set(item.column() for item in selected_items))
        text = ""
        for row in rows:
            row_data = []
            for col in cols:
                item = self.table.table.item(row, col)
                row_data.append(item.text() if item else "")
            text += "\t".join(row_data) + "\n"
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        dlg = CustomDialog_Flexible(header_text="موفقیت", main_text="محتوای سلول‌های انتخاب‌شده کپی شد.", ok_text="باشه", parent=self, icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation)))
        dlg.exec_()

    def save_cell_edit(self, item):
        try:
            row = item.row()
            col = item.column()
            new_value = item.text().strip()
            column_name = self.column_names[col]
            team_id = self.table.table.item(row, 0).data(Qt.UserRole)  # گرفتن id

            # اعتبارسنجی
            if column_name == "first_name" and not new_value:
                dlg = CustomDialog_Flexible(
                    header_text="خطا",
                    main_text="نام اجباری است!",
                    ok_text="باشه",
                    parent=self,
                    icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                )
                dlg.exec_()
                self.table.load_table()
                return
            if column_name == "last_name" and not new_value:
                dlg = CustomDialog_Flexible(
                    header_text="خطا",
                    main_text="نام خانوادگی اجباری است!",
                    ok_text="باشه",
                    parent=self,
                    icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                )
                dlg.exec_()
                self.table.load_table()
                return
            if column_name == "team_leader" and not new_value:
                dlg = CustomDialog_Flexible(
                    header_text="خطا",
                    main_text="سرپرست اجباری است!",
                    ok_text="باشه",
                    parent=self,
                    icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                )
                dlg.exec_()
                self.table.load_table()
                return
            if column_name == "national_code" and new_value:
                if not (new_value.isdigit() and len(new_value) == 10):
                    dlg = CustomDialog_Flexible(
                        header_text="خطا",
                        main_text="کد ملی باید ۱۰ رقم باشد!",
                        ok_text="باشه",
                        parent=self,
                        icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    )
                    dlg.exec_()
                    self.table.load_table()
                    return
                existing_codes = self.db.fetch_all(
                    "SELECT national_code FROM teams WHERE national_code != ? AND id != ?",
                    (new_value, team_id)
                )
                if existing_codes and new_value in [str(code[0]) for code in existing_codes]:
                    dlg = CustomDialog_Flexible(
                        header_text="خطا",
                        main_text="کد ملی باید یکتا باشد!",
                        ok_text="باشه",
                        parent=self,
                        icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    )
                    dlg.exec_()
                    self.table.load_table()
                    return
            if column_name == "phone_number" and new_value:
                if not (new_value.isdigit() and len(new_value) == 11):
                    dlg = CustomDialog_Flexible(
                        header_text="خطا",
                        main_text="شماره همراه باید ۱۱ رقم باشد!",
                        ok_text="باشه",
                        parent=self,
                        icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    )
                    dlg.exec_()
                    self.table.load_table()
                    return
            if column_name == "hire_date" and new_value:
                if not re.match(r"^\d{4}/\d{2}/\d{2}$", new_value):
                    dlg = CustomDialog_Flexible(
                        header_text="خطا",
                        main_text="تاریخ استخدام باید به فرمت YYYY/MM/DD باشد!",
                        ok_text="باشه",
                        parent=self,
                        icon=QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    )
                    dlg.exec_()
                    self.table.load_table()
                    return

            # به‌روزرسانی دیتابیس
            query = f"UPDATE teams SET {column_name} = ? WHERE id = ?"
            self.db.execute_query(query, (new_value, team_id))
            logging.debug(f"Updated {column_name} to {new_value} for team id {team_id}")
            # به‌روزرسانی جدول
            item.setText(new_value)
        except Exception as e:
            logging.error(f"Error in save_cell_edit: {str(e)}")
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در ذخیره تغییرات: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()
            self.table.load_table()

    def safe_generate_report(self):
        try:
            self.generate_report()
        except Exception as e:
            import traceback
            logging.error(f"Error in safe_generate_report: {str(e)}\n{traceback.format_exc()}")
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در تولید گزارش: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()
