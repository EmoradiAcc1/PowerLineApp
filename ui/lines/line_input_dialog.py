from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QHBoxLayout, QLabel, QMessageBox, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import re

class LineInputDialog(QDialog):
    def __init__(self, parent=None, line_data=None, is_edit=False, font_family="Vazir"):
        super().__init__(parent)
        self.setWindowTitle("افزودن خط" if not is_edit else "ویرایش خط")
        self.setFixedSize(450, 750)
        self.setLayoutDirection(Qt.RightToLeft)
        self.is_edit = is_edit
        self.current_id = line_data.get('id') if line_data else None

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)

        # Form layout
        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        self.form_layout.setFormAlignment(Qt.AlignRight)
        self.form_layout.setSpacing(8)

        # Font
        font = QFont(font_family, 14)

        # Line code
        self.line_code = QLineEdit()
        self.line_code.setFont(font)
        self.line_code.setMaxLength(20)
        line_code_layout = QHBoxLayout()
        line_code_layout.addWidget(self.line_code)
        line_code_layout.addStretch()
        self.form_layout.addRow(QLabel("کد خط:"), line_code_layout)

        # Voltage level
        self.voltage_level = QLineEdit()
        self.voltage_level.setFont(font)
        self.voltage_level.setMaxLength(3)
        voltage_layout = QHBoxLayout()
        voltage_layout.addWidget(self.voltage_level)
        voltage_layout.addStretch()
        self.form_layout.addRow(QLabel("سطح ولتاژ:"), voltage_layout)

        # Line name
        self.line_name = QLineEdit()
        self.line_name.setFont(font)
        self.line_name.setMaxLength(50)
        line_name_layout = QHBoxLayout()
        line_name_layout.addWidget(self.line_name)
        line_name_layout.addStretch()
        self.form_layout.addRow(QLabel("نام خط:"), line_name_layout)

        # Dispatch code
        self.dispatch_code = QLineEdit()
        self.dispatch_code.setFont(font)
        dispatch_layout = QHBoxLayout()
        dispatch_layout.addWidget(self.dispatch_code)
        dispatch_layout.addStretch()
        self.form_layout.addRow(QLabel("کد دیسپاچینگ:"), dispatch_layout)

        # Total towers
        self.total_towers = QLineEdit()
        self.total_towers.setFont(font)
        total_towers_layout = QHBoxLayout()
        total_towers_layout.addWidget(self.total_towers)
        total_towers_layout.addStretch()
        self.form_layout.addRow(QLabel("تعداد کل دکل‌ها:"), total_towers_layout)

        # Tension towers
        self.tension_towers = QLineEdit()
        self.tension_towers.setFont(font)
        tension_towers_layout = QHBoxLayout()
        tension_towers_layout.addWidget(self.tension_towers)
        tension_towers_layout.addStretch()
        self.form_layout.addRow(QLabel("دکل‌های کششی:"), tension_towers_layout)

        # Suspension towers
        self.suspension_towers = QLineEdit()
        self.suspension_towers.setFont(font)
        suspension_towers_layout = QHBoxLayout()
        suspension_towers_layout.addWidget(self.suspension_towers)
        suspension_towers_layout.addStretch()
        self.form_layout.addRow(QLabel("دکل‌های آویزی:"), suspension_towers_layout)

        # Line length
        self.line_length = QLineEdit()
        self.line_length.setFont(font)
        line_length_layout = QHBoxLayout()
        line_length_layout.addWidget(self.line_length)
        line_length_layout.addStretch()
        self.form_layout.addRow(QLabel("طول خط:"), line_length_layout)

        # Circuit length
        self.circuit_length = QLineEdit()
        self.circuit_length.setFont(font)
        circuit_length_layout = QHBoxLayout()
        circuit_length_layout.addWidget(self.circuit_length)
        circuit_length_layout.addStretch()
        self.form_layout.addRow(QLabel("طول مدار:"), circuit_length_layout)

        # Plain area
        self.plain_area = QLineEdit()
        self.plain_area.setFont(font)
        plain_area_layout = QHBoxLayout()
        plain_area_layout.addWidget(self.plain_area)
        plain_area_layout.addStretch()
        self.form_layout.addRow(QLabel("دشت:"), plain_area_layout)

        # Semi-mountainous
        self.semi_mountainous = QLineEdit()
        self.semi_mountainous.setFont(font)
        semi_mountainous_layout = QHBoxLayout()
        semi_mountainous_layout.addWidget(self.semi_mountainous)
        semi_mountainous_layout.addStretch()
        self.form_layout.addRow(QLabel("نیمه کوهستانی:"), semi_mountainous_layout)

        # Rough terrain
        self.rough_terrain = QLineEdit()
        self.rough_terrain.setFont(font)
        rough_terrain_layout = QHBoxLayout()
        rough_terrain_layout.addWidget(self.rough_terrain)
        rough_terrain_layout.addStretch()
        self.form_layout.addRow(QLabel("صعب العبور:"), rough_terrain_layout)

        # Supervisor
        self.supervisor = QLineEdit()
        self.supervisor.setFont(font)
        supervisor_layout = QHBoxLayout()
        supervisor_layout.addWidget(self.supervisor)
        supervisor_layout.addStretch()
        self.form_layout.addRow(QLabel("ناظر:"), supervisor_layout)

        # Team leader
        self.team_leader = QLineEdit()
        self.team_leader.setFont(font)
        team_leader_layout = QHBoxLayout()
        team_leader_layout.addWidget(self.team_leader)
        team_leader_layout.addStretch()
        self.form_layout.addRow(QLabel("سرپرست اکیپ:"), team_leader_layout)

        # Operation year
        self.operation_year = QLineEdit()
        self.operation_year.setFont(font)
        operation_year_layout = QHBoxLayout()
        operation_year_layout.addWidget(self.operation_year)
        operation_year_layout.addStretch()
        self.form_layout.addRow(QLabel("سال بهره‌برداری:"), operation_year_layout)

        # Wire type
        self.wire_type = QLineEdit()
        self.wire_type.setFont(font)
        wire_type_layout = QHBoxLayout()
        wire_type_layout.addWidget(self.wire_type)
        wire_type_layout.addStretch()
        self.form_layout.addRow(QLabel("نوع سیم:"), wire_type_layout)

        # Tower type
        self.tower_type = QLineEdit()
        self.tower_type.setFont(font)
        tower_type_layout = QHBoxLayout()
        tower_type_layout.addWidget(self.tower_type)
        tower_type_layout.addStretch()
        self.form_layout.addRow(QLabel("نوع دکل:"), tower_type_layout)

        # Bundle count
        self.bundle_count = QLineEdit()
        self.bundle_count.setFont(font)
        bundle_count_layout = QHBoxLayout()
        bundle_count_layout.addWidget(self.bundle_count)
        bundle_count_layout.addStretch()
        self.form_layout.addRow(QLabel("تعداد باندل:"), bundle_count_layout)

        # Load data if editing
        if line_data:
            self.line_code.setText(str(line_data.get('line_code', '')))
            self.voltage_level.setText(str(line_data.get('voltage_level', '')))
            self.line_name.setText(str(line_data.get('line_name', '')))
            self.dispatch_code.setText(str(line_data.get('dispatch_code', '')))
            self.total_towers.setText(str(line_data.get('total_towers', '')))
            self.tension_towers.setText(str(line_data.get('tension_towers', '')))
            self.suspension_towers.setText(str(line_data.get('suspension_towers', '')))
            self.line_length.setText(str(line_data.get('line_length', '')))
            self.circuit_length.setText(str(line_data.get('circuit_length', '')))
            self.plain_area.setText(str(line_data.get('plain_area', '')))
            self.semi_mountainous.setText(str(line_data.get('semi_mountainous', '')))
            self.rough_terrain.setText(str(line_data.get('rough_terrain', '')))
            self.supervisor.setText(str(line_data.get('supervisor', '')))
            self.team_leader.setText(str(line_data.get('team_leader', '')))
            self.operation_year.setText(str(line_data.get('operation_year', '')))
            self.wire_type.setText(str(line_data.get('wire_type', '')))
            self.tower_type.setText(str(line_data.get('tower_type', '')))
            self.bundle_count.setText(str(line_data.get('bundle_count', '')))

        self.layout.addLayout(self.form_layout)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("ذخیره")
        self.save_button.setFont(font)
        self.save_button.setObjectName("saveButton")
        self.cancel_button = QPushButton("لغو")
        self.cancel_button.setFont(font)
        self.cancel_button.setObjectName("cancelButton")
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.button_layout)

        # Connect buttons
        self.save_button.clicked.connect(self.save_line)
        self.cancel_button.clicked.connect(self.reject)

    def validate_inputs(self):
        if not self.line_code.text():
            return False, "کد خط اجباری است!"
        if not self.line_name.text():
            return False, "نام خط اجباری است!"
        if self.total_towers.text() and not self.total_towers.text().isdigit():
            return False, "تعداد کل دکل‌ها باید عدد باشد!"
        if self.tension_towers.text() and not self.tension_towers.text().isdigit():
            return False, "تعداد دکل‌های کششی باید عدد باشد!"
        if self.suspension_towers.text() and not self.suspension_towers.text().isdigit():
            return False, "تعداد دکل‌های آویزی باید عدد باشد!"
        if self.line_length.text() and not re.match(r"^\d*\.?\d*$", self.line_length.text()):
            return False, "طول خط باید عدد باشد!"
        if self.circuit_length.text() and not re.match(r"^\d*\.?\d*$", self.circuit_length.text()):
            return False, "طول مدار باید عدد باشد!"
        if self.voltage_level.text() and not self.voltage_level.text().isdigit():
            return False, "سطح ولتاژ باید عدد باشد!"
        if self.operation_year.text() and not (self.operation_year.text().isdigit() and len(self.operation_year.text()) == 4):
            return False, "سال بهره‌برداری باید عدد ۴ رقمی باشد!"
        if self.bundle_count.text() and not self.bundle_count.text().isdigit():
            return False, "تعداد باندل باید عدد باشد!"
        existing_codes = self.parent().db.fetch_all("SELECT line_code FROM lines WHERE id != ?", (self.current_id or -1,))
        if self.line_code.text() in [code[0] for code in existing_codes]:
            return False, "کد خط باید یکتا باشد!"
        return True, ""

    def save_line(self):
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

        self.line_data = {
            'line_code': self.line_code.text(),
            'voltage_level': self.voltage_level.text(),
            'line_name': self.line_name.text(),
            'dispatch_code': self.dispatch_code.text(),
            'total_towers': self.total_towers.text(),
            'tension_towers': self.tension_towers.text(),
            'suspension_towers': self.suspension_towers.text(),
            'line_length': format_number(self.line_length.text()),
            'circuit_length': format_number(self.circuit_length.text()),
            'plain_area': self.plain_area.text(),
            'semi_mountainous': self.semi_mountainous.text(),
            'rough_terrain': self.rough_terrain.text(),
            'supervisor': self.supervisor.text(),
            'team_leader': self.team_leader.text(),
            'operation_year': self.operation_year.text(),
            'wire_type': self.wire_type.text(),
            'tower_type': self.tower_type.text(),
            'bundle_count': self.bundle_count.text(),
            'id': self.current_id
        }
        self.accept()
