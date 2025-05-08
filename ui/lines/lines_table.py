from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QLineEdit, QHBoxLayout, QLabel, QFileDialog, QMessageBox, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import Database
import csv
import pandas as pd
import re

class LinesTable:
    def __init__(self, parent=None, font_family="Vazir"):
        self.db = Database()
        self.parent = parent

        # Filter
        self.filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setObjectName("filterInput")
        self.filter_input.setPlaceholderText("جستجو در تمام ستون‌ها...")
        self.filter_input.setFont(QFont(font_family, 12))
        self.filter_input.setFixedWidth(300)
        self.filter_input.mousePressEvent = self.clear_placeholder
        self.filter_layout.addWidget(QLabel("فیلتر:"))
        self.filter_layout.addWidget(self.filter_input)
        self.filter_layout.addStretch()

        # Table
        self.widget = QTableWidget()
        self.widget.setColumnCount(18)
        self.widget.setHorizontalHeaderLabels([
            "کد خط", "سطح ولتاژ", "نام خط", "کد دیسپاچینگ", "تعداد کل دکل‌ها",
            "دکل‌های کششی", "دکل‌های آویزی", "طول خط", "طول مدار",
            "دشت", "نیمه کوهستانی", "صعب العبور", "ناظر", "سرپرست اکیپ",
            "سال بهره‌برداری", "نوع سیم", "نوع دکل", "تعداد باندل"
        ])
        self.widget.setFont(QFont(font_family, 12))
        self.widget.setSelectionMode(QTableWidget.ExtendedSelection)
        self.widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.load_table()

    def clear_placeholder(self, event):
        if not self.filter_input.text() or self.filter_input.text() == self.filter_input.placeholderText():
            self.filter_input.clear()
        super(QLineEdit, self.filter_input).mousePressEvent(event)

    def load_table(self, filter_text=""):
        query = """
            SELECT line_code, voltage_level, line_name, dispatch_code, total_towers, 
                   tension_towers, suspension_towers, line_length, circuit_length,
                   plain_area, semi_mountainous, rough_terrain, supervisor, team_leader,
                   operation_year, wire_type, tower_type, bundle_count
            FROM lines
        """
        if filter_text:
            query += """
                WHERE line_code LIKE ? OR voltage_level LIKE ? OR line_name LIKE ? 
                OR dispatch_code LIKE ? OR total_towers LIKE ? OR tension_towers LIKE ? 
                OR suspension_towers LIKE ? OR line_length LIKE ? OR circuit_length LIKE ?
                OR plain_area LIKE ? OR semi_mountainous LIKE ? OR rough_terrain LIKE ?
                OR supervisor LIKE ? OR team_leader LIKE ? OR operation_year LIKE ?
                OR wire_type LIKE ? OR tower_type LIKE ? OR bundle_count LIKE ?
            """
            params = tuple(f"%{filter_text}%" for _ in range(18))
        else:
            params = ""
        rows = self.db.fetch_all(query, params)
        self.widget.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, data in enumerate(row_data):
                if col_idx in [7, 8]:
                    try:
                        num = float(data)
                        data = str(int(num)) if num.is_integer() else str(num).rstrip('0').rstrip('.')
                    except (ValueError, TypeError):
                        data = str(data)
                else:
                    data = str(data)
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter)
                self.widget.setItem(row_idx, col_idx, item)
        
        self.widget.resizeColumnsToContents()
        for col in range(self.widget.columnCount()):
            if self.widget.columnWidth(col) < 100:
                self.widget.setColumnWidth(col, 100)
        self.widget.resizeRowsToContents()
        self.widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def generate_report(self):
        rows = self.db.fetch_all("""
            SELECT line_code, voltage_level, line_name, dispatch_code, total_towers, 
                   tension_towers, suspension_towers, line_length, circuit_length,
                   plain_area, semi_mountainous, rough_terrain, supervisor, team_leader,
                   operation_year, wire_type, tower_type, bundle_count
            FROM lines
        """)
        try:
            with open("lines_report.csv", "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "کد خط", "سطح ولتاژ", "نام خط", "کد دیسپاچینگ", "تعداد کل دکل‌ها",
                    "دکل‌های کششی", "دکل‌های آویزی", "طول خط", "طول مدار",
                    "دشت", "نیمه کوهستانی", "صعب العبور", "ناظر", "سرپرست اکیپ",
                    "سال بهره‌برداری", "نوع سیم", "نوع دکل", "تعداد باندل"
                ])
                writer.writerows(rows)
            QMessageBox.information(self.parent, "موفقیت", "گزارش با نام lines_report.csv ذخیره شد.")
        except Exception as e:
            QMessageBox.critical(self.parent, "خطا", f"خطا در تولید گزارش: {str(e)}")

    def import_from_excel(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self.parent, "انتخاب فایل اکسل", "", "Excel Files (*.xlsx *.xls)")
            if not file_path:
                return

            df = pd.read_excel(file_path)
            expected_columns = [
                "کد خط", "سطح ولتاژ", "نام خط", "کد دیسپاچینگ", "تعداد کل دکل‌ها",
                "دکل‌های کششی", "دکل‌های آویزی", "طول خط", "طول مدار",
                "دشت", "نیمه کوهستانی", "صعب العبور", "ناظر", "سرپرست اکیپ",
                "سال بهره‌برداری", "نوع سیم", "نوع دکل", "تعداد باندل"
            ]
            if not all(col in df.columns for col in expected_columns):
                QMessageBox.critical(self.parent, "خطا", "ساختار فایل اکسل نادرست است! ستون‌های مورد انتظار: " + ", ".join(expected_columns))
                return

            existing_codes = self.db.fetch_all("SELECT line_code FROM lines")
            existing_line_codes = {row[0] for row in existing_codes if row[0]}

            def format_number(value):
                if pd.notna(value):
                    try:
                        num = float(value)
                        return str(int(num)) if num.is_integer() else str(num).rstrip('0').rstrip('.')
                    except (ValueError, TypeError):
                        return str(value)
                return ""

            inserted_count = 0
            for _, row in df.iterrows():
                line_code = str(row["کد خط"]) if pd.notna(row["کد خط"]) else ""
                if not line_code or line_code in existing_line_codes:
                    continue
                if not str(row["نام خط"]):
                    continue
                if pd.notna(row["تعداد کل دکل‌ها"]) and not str(row["تعداد کل دکل‌ها"]).isdigit():
                    continue
                if pd.notna(row["دکل‌های کششی"]) and not str(row["دکل‌های کششی"]).isdigit():
                    continue
                if pd.notna(row["دکل‌های آویزی"]) and not str(row["دکل‌های آویزی"]).isdigit():
                    continue
                if pd.notna(row["طول خط"]) and not re.match(r"^\d*\.?\d*$", str(row["طول خط"])):
                    continue
                if pd.notna(row["طول مدار"]) and not re.match(r"^\d*\.?\d*$", str(row["طول مدار"])):
                    continue
                if pd.notna(row["سطح ولتاژ"]) and not str(row["سطح ولتاژ"]).isdigit():
                    continue
                if pd.notna(row["سال بهره‌برداری"]) and not (str(row["سال بهره‌برداری"]).isdigit() and len(str(row["سال بهره‌برداری"])) == 4):
                    continue
                if pd.notna(row["تعداد باندل"]) and not str(row["تعداد باندل"]).isdigit():
                    continue

                self.db.execute_query(
                    """
                    INSERT INTO lines (line_code, voltage_level, line_name, dispatch_code, total_towers, 
                                       tension_towers, suspension_towers, line_length, circuit_length,
                                       plain_area, semi_mountainous, rough_terrain, supervisor, team_leader,
                                       operation_year, wire_type, tower_type, bundle_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        line_code,
                        str(row["سطح ولتاژ"]) if pd.notna(row["سطح ولتاژ"]) else "",
                        str(row["نام خط"]),
                        str(row["کد دیسپاچینگ"]) if pd.notna(row["کد دیسپاچینگ"]) else "",
                        str(row["تعداد کل دکل‌ها"]) if pd.notna(row["تعداد کل دکل‌ها"]) else "",
                        str(row["دکل‌های کششی"]) if pd.notna(row["دکل‌های کششی"]) else "",
                        str(row["دکل‌های آویزی"]) if pd.notna(row["دکل‌های آویزی"]) else "",
                        format_number(row["طول خط"]),
                        format_number(row["طول مدار"]),
                        str(row["دشت"]) if pd.notna(row["دشت"]) else "",
                        str(row["نیمه کوهستانی"]) if pd.notna(row["نیمه کوهستانی"]) else "",
                        str(row["صعب العبور"]) if pd.notna(row["صعب العبور"]) else "",
                        str(row["ناظر"]) if pd.notna(row["ناظر"]) else "",
                        str(row["سرپرست اکیپ"]) if pd.notna(row["سرپرست اکیپ"]) else "",
                        str(row["سال بهره‌برداری"]) if pd.notna(row["سال بهره‌برداری"]) else "",
                        str(row["نوع سیم"]) if pd.notna(row["نوع سیم"]) else "",
                        str(row["نوع دکل"]) if pd.notna(row["نوع دکل"]) else "",
                        str(row["تعداد باندل"]) if pd.notna(row["تعداد باندل"]) else ""
                    )
                )
                inserted_count += 1
                existing_line_codes.add(line_code)

            self.load_table()
            QMessageBox.information(self.parent, "موفقیت", f"{inserted_count} خط با موفقیت از فایل اکسل وارد شد.")
        except Exception as e:
            QMessageBox.critical(self.parent, "خطا", f"خطا در وارد کردن اطلاعات از اکسل: {str(e)}")
