from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from .lines_table import LinesTable
from .lines_toolbar import LinesToolbar
from .line_input_dialog import LineInputDialog
from .lines_utils import filter_table, copy_selected_cells
from database import Database

class LinesWindow(QWidget):
    def __init__(self, parent=None, font_family="Vazir"):
        super().__init__(parent)
        self.db = Database()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        self.setLayoutDirection(Qt.RightToLeft)

        # Toolbar
        self.toolbar = LinesToolbar(self)
        self.layout.addWidget(self.toolbar.widget)

        # Table and filter
        self.table = LinesTable(self, font_family=font_family)
        self.layout.addLayout(self.table.filter_layout)
        self.layout.addWidget(self.table.widget)

        # Connect toolbar actions
        self.toolbar.add_action.triggered.connect(self.add_line)
        self.toolbar.delete_action.triggered.connect(self.delete_line)
        self.toolbar.edit_action.triggered.connect(self.edit_line)
        self.toolbar.import_excel_action.triggered.connect(self.table.import_from_excel)
        self.toolbar.report_action.triggered.connect(self.table.generate_report)
        self.toolbar.back_action.triggered.connect(self.close)

        # Connect table utilities
        self.table.filter_input.textChanged.connect(lambda: filter_table(self.table))
        self.table.widget.customContextMenuRequested.connect(lambda pos: copy_selected_cells(self.table, pos))

    def add_line(self):
        dialog = LineInputDialog(self)
        if dialog.exec_() == dialog.Accepted:
            line_data = dialog.line_data
            try:
                self.db.execute_query(
                    """
                    INSERT INTO lines (line_code, voltage_level, line_name, dispatch_code, total_towers, 
                                       tension_towers, suspension_towers, line_length, circuit_length,
                                       plain_area, semi_mountainous, rough_terrain, supervisor, team_leader,
                                       operation_year, wire_type, tower_type, bundle_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        line_data['line_code'], line_data['voltage_level'], line_data['line_name'], 
                        line_data['dispatch_code'], line_data['total_towers'], line_data['tension_towers'], 
                        line_data['suspension_towers'], line_data['line_length'], line_data['circuit_length'],
                        line_data['plain_area'], line_data['semi_mountainous'], line_data['rough_terrain'],
                        line_data['supervisor'], line_data['team_leader'], line_data['operation_year'],
                        line_data['wire_type'], line_data['tower_type'], line_data['bundle_count']
                    )
                )
                self.table.load_table()
                QMessageBox.information(self, "موفقیت", "خط با موفقیت اضافه شد.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در افزودن خط: {str(e)}")

    def edit_line(self):
        selected = self.table.widget.selectedItems()
        if not selected:
            QMessageBox.warning(self, "خطا", "خطی انتخاب نشده است!")
            return
        row = self.table.widget.currentRow()
        current_id = self.db.fetch_all("SELECT id FROM lines WHERE line_name=?", (self.table.widget.item(row, 2).text(),))[0][0]
        line_data = {
            'id': current_id,
            'line_code': self.table.widget.item(row, 0).text(),
            'voltage_level': self.table.widget.item(row, 1).text(),
            'line_name': self.table.widget.item(row, 2).text(),
            'dispatch_code': self.table.widget.item(row, 3).text(),
            'total_towers': self.table.widget.item(row, 4).text(),
            'tension_towers': self.table.widget.item(row, 5).text(),
            'suspension_towers': self.table.widget.item(row, 6).text(),
            'line_length': self.table.widget.item(row, 7).text(),
            'circuit_length': self.table.widget.item(row, 8).text(),
            'plain_area': self.table.widget.item(row, 9).text(),
            'semi_mountainous': self.table.widget.item(row, 10).text(),
            'rough_terrain': self.table.widget.item(row, 11).text(),
            'supervisor': self.table.widget.item(row, 12).text(),
            'team_leader': self.table.widget.item(row, 13).text(),
            'operation_year': self.table.widget.item(row, 14).text(),
            'wire_type': self.table.widget.item(row, 15).text(),
            'tower_type': self.table.widget.item(row, 16).text(),
            'bundle_count': self.table.widget.item(row, 17).text()
        }
        dialog = LineInputDialog(self, line_data, is_edit=True)
        if dialog.exec_() == dialog.Accepted:
            line_data = dialog.line_data
            try:
                self.db.execute_query(
                    """
                    UPDATE lines SET line_code=?, voltage_level=?, line_name=?, dispatch_code=?, 
                                     total_towers=?, tension_towers=?, suspension_towers=?, 
                                     line_length=?, circuit_length=?, plain_area=?, semi_mountainous=?, 
                                     rough_terrain=?, supervisor=?, team_leader=?, operation_year=?, 
                                     wire_type=?, tower_type=?, bundle_count=?
                    WHERE id=?
                    """,
                    (
                        line_data['line_code'], line_data['voltage_level'], line_data['line_name'], 
                        line_data['dispatch_code'], line_data['total_towers'], line_data['tension_towers'], 
                        line_data['suspension_towers'], line_data['line_length'], line_data['circuit_length'],
                        line_data['plain_area'], line_data['semi_mountainous'], line_data['rough_terrain'],
                        line_data['supervisor'], line_data['team_leader'], line_data['operation_year'],
                        line_data['wire_type'], line_data['tower_type'], line_data['bundle_count'],
                        line_data['id']
                    )
                )
                self.table.load_table()
                QMessageBox.information(self, "موفقیت", "خط با موفقیت ویرایش شد.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ویرایش خط: {str(e)}")

    def delete_line(self):
        selected_rows = sorted(set(index.row() for index in self.table.widget.selectedIndexes()))
        if not selected_rows:
            QMessageBox.warning(self, "خطا", "خطی انتخاب نشده است!")
            return

        row_count = len(selected_rows)
        msg = f"آیا از حذف {row_count} خط مطمئن هستید؟"
        reply = QMessageBox.question(
            self, "تأیید حذف", msg,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            for row in selected_rows:
                line_name = self.table.widget.item(row, 2).text()
                self.db.execute_query("DELETE FROM lines WHERE line_name=?", (line_name,))
            self.table.load_table()
            QMessageBox.information(self, "موفقیت", f"{row_count} خط با موفقیت حذف شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")
