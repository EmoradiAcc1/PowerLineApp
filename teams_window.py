from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QToolBar, QAction, QLineEdit, QHBoxLayout, QLabel, QMessageBox, QStyle, QDialog, QFormLayout, QPushButton, QFileDialog, QHeaderView, QSizePolicy, QMenu, QApplication
from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QFont, QIcon
from database import Database
import csv
import re
import pandas as pd
import logging

# تنظیم لاگ برای دیباگ
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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

        self.filter_input = QLineEdit()
        self.filter_input.setFont(QFont("Vazir", 10))
        self.filter_input.setPlaceholderText(f"فیلتر {column_name}")
        self.filter_input.setStyleSheet("padding: 3px; border: 1px solid #ccc; border-radius: 4px;")
        self.filter_input.setFixedWidth(150)
        self.filter_input.setText(current_filter or "")
        self.filter_input.textChanged.connect(self.apply_filter)
        self.layout().addWidget(self.filter_input)

        self.adjustSize()

    def apply_filter(self):
        try:
            filter_text = self.filter_input.text().strip()
            logging.debug(f"Applying filter for column {self.column_index}: {filter_text}")
            self.on_filter_changed(self.column_index, filter_text)
        except Exception as e:
            logging.error(f"Error in apply_filter: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در اعمال فیلتر: {str(e)}")

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.close()

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
        self.layout.addRow("کدملی:", self.national_code)

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
            QMessageBox.warning(self, "خطا", error_msg)
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

class TeamsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.column_filters = {}
        self.original_headers = [
            "کدملی", "نام", "نام خانوادگی", "نام پدر",
            "پست", "تاریخ شروع همکاری", "شماره همراه", "سرپرست"
        ]
        self.column_names = [
            "national_code", "first_name", "last_name", "father_name",
            "position", "hire_date", "phone_number", "team_leader"
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

        self.add_action = QAction(QIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder)), "افزودن پرسنل جدید", self)
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

        self.add_action.triggered.connect(self.add_team)
        self.delete_action.triggered.connect(self.delete_team)
        self.edit_action.triggered.connect(self.edit_team)
        self.import_excel_action.triggered.connect(self.import_from_excel)
        self.report_action.triggered.connect(self.generate_report)
        self.back_action.triggered.connect(self.close)

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

        self.table = QTableWidget()
        self.table.setColumnCount(8)
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
        self.table.cellClicked.connect(self.load_row_data)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.horizontalHeader().sectionClicked.connect(self.show_filter_popover)
        self.table.itemChanged.connect(self.save_cell_edit)  # اتصال سیگنال itemChanged
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
            scroll_value = self.table.horizontalScrollBar().value()
            adjusted_pos = section_pos - scroll_value
            total_width = viewport.width()
            if adjusted_pos < 0:
                adjusted_pos = 0
            elif adjusted_pos + section_width > total_width:
                adjusted_pos = total_width - section_width
            local_pos = QPoint(adjusted_pos, header_height)
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
            logging.debug(f"Filter popover for column {logical_index} (visual_index {visual_index}) at global_pos {global_pos}, adjusted_pos {adjusted_pos}, scroll_value {scroll_value}, section_pos {section_pos}, total_width {total_width}")
        except Exception as e:
            logging.error(f"Error in show_filter_popover: {str(e)}")
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
            logging.error(f"Error in update_column_filter: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در به‌روزرسانی فیلتر: {str(e)}")

    def load_table(self, global_filter=""):
        try:
            query = """
                SELECT national_code, first_name, last_name, father_name,
                       position, hire_date, phone_number, team_leader, id
                FROM teams
            """
            params = []
            conditions = []
            if global_filter:
                conditions.append("""
                    (national_code LIKE ? OR first_name LIKE ? OR last_name LIKE ?
                    OR father_name LIKE ? OR position LIKE ? OR hire_date LIKE ?
                    OR phone_number LIKE ? OR team_leader LIKE ?)
                """)
                params.extend([f"%{global_filter}%"] * 8)
            for column, filter_text in self.column_filters.items():
                if filter_text:
                    conditions.append(f"{column} LIKE ?")
                    params.append(f"%{filter_text}%")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            logging.debug(f"Executing query: {query} with params: {params}")
            rows = self.db.fetch_all(query, tuple(params))
            self.table.setRowCount(len(rows))
            self.table.blockSignals(True)  # جلوگیری از ارسال سیگنال در حین پر کردن جدول
            for row_idx, row_data in enumerate(rows):
                for col_idx, data in enumerate(row_data[:-1]):  # بدون ستون id
                    data = str(data) if data is not None else ""
                    item = QTableWidgetItem(data)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() | Qt.ItemIsEditable)  # فعال کردن ویرایش
                    self.table.setItem(row_idx, col_idx, item)
                # ذخیره id در داده‌های آیتم برای استفاده در save_cell_edit
                self.table.item(row_idx, 0).setData(Qt.UserRole, row_data[-1])  # id در ستون آخر
            self.table.blockSignals(False)  # بازگرداندن سیگنال‌ها
            self.table.resizeColumnsToContents()
            for col in range(self.table.columnCount()):
                if self.table.columnWidth(col) < 100:
                    self.table.setColumnWidth(col, 100)
            self.table.resizeRowsToContents()
            self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            logging.debug(f"Table loaded with {len(rows)} rows")
        except Exception as e:
            logging.error(f"Error in load_table: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری جدول: {str(e)}")

    def filter_table(self):
        try:
            self.load_table(self.filter_input.text())
        except Exception as e:
            logging.error(f"Error in filter_table: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در فیلتر جدول: {str(e)}")

    def add_team(self):
        dialog = TeamInputDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            team_data = dialog.team_data
            try:
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
                self.load_table()
                QMessageBox.information(self, "موفقیت", "پرسنل با موفقیت اضافه شد.")
            except Exception as e:
                logging.error(f"Error in add_team: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در افزودن پرسنل: {str(e)}")

    def edit_team(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "خطا", "پرسنلی انتخاب نشده است!")
            return
        row = self.table.currentRow()
        national_code = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
        try:
            result = self.db.fetch_all(
                "SELECT id FROM teams WHERE national_code=?",
                (national_code,)
            )
            if not result:
                QMessageBox.critical(self, "خطا", "پرسنل موردنظر یافت نشد!")
                return
            current_id = result[0][0]
            team_data = {
                'id': current_id,
                'national_code': national_code,
                'first_name': self.table.item(row, 1).text() if self.table.item(row, 1) else "",
                'last_name': self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                'father_name': self.table.item(row, 3).text() if self.table.item(row, 3) else "",
                'position': self.table.item(row, 4).text() if self.table.item(row, 4) else "",
                'hire_date': self.table.item(row, 5).text() if self.table.item(row, 5) else "",
                'phone_number': self.table.item(row, 6).text() if self.table.item(row, 6) else "",
                'team_leader': self.table.item(row, 7).text() if self.table.item(row, 7) else ""
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
                self.load_table()
                QMessageBox.information(self, "موفقیت", "پرسنل با موفقیت ویرایش شد.")
        except Exception as e:
            logging.error(f"Error in edit_team: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در ویرایش پرسنل: {str(e)}")

    def delete_team(self):
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()))
        if not selected_rows:
            QMessageBox.warning(self, "خطا", "پرسنلی انتخاب نشده است!")
            return

        row_count = len(selected_rows)
        msg = f"آیا از حذف {row_count} پرسنل مطمئن هستید؟"
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("تأیید حذف")
        msg_box.setText(msg)
        msg_box.setStandardButtons(QMessageBox.NoButton)
        yes_button = msg_box.addButton("بله", QMessageBox.AcceptRole)
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
                national_code = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
                self.db.execute_query(
                    "DELETE FROM teams WHERE national_code=?",
                    (national_code,)
                )
            self.load_table()
            QMessageBox.information(self, "موفقیت", f"{row_count} پرسنل با موفقیت حذف شد.")
        except Exception as e:
            logging.error(f"Error in delete_team: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")

    def load_row_data(self, row, col):
        pass

    def generate_report(self):
        try:
            rows = self.db.fetch_all("""
                SELECT national_code, first_name, last_name, father_name,
                       position, hire_date, phone_number, team_leader
                FROM teams
            """)
            with open("teams_report.csv", "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.original_headers)
                writer.writerows(rows)
            QMessageBox.information(self, "موفقیت", "گزارش با نام teams_report.csv ذخیره شد.")
        except Exception as e:
            logging.error(f"Error in generate_report: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در تولید گزارش: {str(e)}")

    def import_from_excel(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل اکسل", "", "Excel Files (*.xlsx *.xls)")
            if not file_path:
                return

            df = pd.read_excel(file_path)
            expected_columns = self.original_headers
            if not all(col in df.columns for col in expected_columns):
                QMessageBox.critical(self, "خطا", "ساختار فایل اکسل نادرست است! ستون‌های مورد انتظار: " + ", ".join(expected_columns))
                return

            existing_codes = self.db.fetch_all("SELECT national_code FROM teams")
            existing_code_set = {str(row[0]) for row in existing_codes if row[0]}

            inserted_count = 0
            for _, row in df.iterrows():
                national_code = str(row["کدملی"]) if pd.notna(row["کدملی"]) else ""
                if not row["نام"] or not row["نام خانوادگی"] or not row["سرپرست"]:
                    continue
                if national_code and national_code in existing_code_set:
                    continue
                if national_code and not (national_code.isdigit() and len(national_code) == 10):
                    continue
                phone_number = str(row["شماره همراه"]) if pd.notna(row["شماره همراه"]) else ""
                if phone_number and not (phone_number.isdigit() and len(phone_number) == 11):
                    continue
                hire_date = str(row["تاریخ شروع همکاری"]) if pd.notna(row["تاریخ شروع همکاری"]) else ""
                if hire_date and not re.match(r"^\d{4}/\d{2}/\d{2}$", hire_date):
                    continue

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
                        hire_date,
                        phone_number,
                        str(row["سرپرست"]) if pd.notna(row["سرپرست"]) else ""
                    )
                )
                inserted_count += 1
                if national_code:
                    existing_code_set.add(national_code)

            self.load_table()
            QMessageBox.information(self, "موفقیت", f"{inserted_count} پرسنل با موفقیت از فایل اکسل وارد شد.")
        except Exception as e:
            logging.error(f"Error in import_from_excel: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در وارد کردن اطلاعات از اکسل: {str(e)}")

    def show_context_menu(self, position):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { 
                background-color: white; 
                border: 1px solid #ccc; 
                direction: rtl; 
            }
            QMenu::item { 
                padding: 5px 20px; 
                padding-right: 30px; 
                margin-right: 10px; 
                color: black; 
                direction: rtl; 
                text-align: right; 
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
        edit_action.triggered.connect(self.edit_team)
        menu.addAction(edit_action)
        delete_action = QAction("حذف", self)
        delete_action.triggered.connect(self.delete_team)
        menu.addAction(delete_action)
        selected_items = bool(self.table.selectedItems())
        copy_action.setEnabled(selected_items)
        edit_action.setEnabled(selected_items)
        delete_action.setEnabled(selected_items)
        menu.exec_(self.table.viewport().mapToGlobal(position))

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

    def save_cell_edit(self, item):
        try:
            row = item.row()
            col = item.column()
            new_value = item.text().strip()
            column_name = self.column_names[col]
            team_id = self.table.item(row, 0).data(Qt.UserRole)  # گرفتن id

            # اعتبارسنجی
            if column_name == "first_name" and not new_value:
                QMessageBox.warning(self, "خطا", "نام اجباری است!")
                self.load_table()
                return
            if column_name == "last_name" and not new_value:
                QMessageBox.warning(self, "خطا", "نام خانوادگی اجباری است!")
                self.load_table()
                return
            if column_name == "team_leader" and not new_value:
                QMessageBox.warning(self, "خطا", "سرپرست اجباری است!")
                self.load_table()
                return
            if column_name == "national_code" and new_value:
                if not (new_value.isdigit() and len(new_value) == 10):
                    QMessageBox.warning(self, "خطا", "کد ملی باید ۱۰ رقم باشد!")
                    self.load_table()
                    return
                existing_codes = self.db.fetch_all(
                    "SELECT national_code FROM teams WHERE national_code != ? AND id != ?",
                    (new_value, team_id)
                )
                if existing_codes and new_value in [str(code[0]) for code in existing_codes]:
                    QMessageBox.warning(self, "خطا", "کد ملی باید یکتا باشد!")
                    self.load_table()
                    return
            if column_name == "phone_number" and new_value:
                if not (new_value.isdigit() and len(new_value) == 11):
                    QMessageBox.warning(self, "خطا", "شماره همراه باید ۱۱ رقم باشد!")
                    self.load_table()
                    return
            if column_name == "hire_date" and new_value:
                if not re.match(r"^\d{4}/\d{2}/\d{2}$", new_value):
                    QMessageBox.warning(self, "خطا", "تاریخ استخدام باید به فرمت YYYY/MM/DD باشد!")
                    self.load_table()
                    return

            # به‌روزرسانی دیتابیس
            query = f"UPDATE teams SET {column_name} = ? WHERE id = ?"
            self.db.execute_query(query, (new_value, team_id))
            logging.debug(f"Updated {column_name} to {new_value} for team id {team_id}")
            # به‌روزرسانی جدول
            item.setText(new_value)
        except Exception as e:
            logging.error(f"Error in save_cell_edit: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره تغییرات: {str(e)}")
            self.load_table()
