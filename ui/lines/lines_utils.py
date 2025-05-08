from PyQt5.QtWidgets import QMenu, QApplication, QMessageBox
from PyQt5.QtCore import Qt

def filter_table(table):
    table.load_table(table.filter_input.text())

def copy_selected_cells(table, position):
    menu = QMenu(table.parent)
    copy_action = QAction("کپی", table.parent)
    copy_action.triggered.connect(lambda: perform_copy(table))
    menu.addAction(copy_action)
    copy_action.setEnabled(bool(table.widget.selectedItems()))
    menu.exec_(table.widget.viewport().mapToGlobal(position))

def perform_copy(table):
    selected_items = table.widget.selectedItems()
    if not selected_items:
        return
    rows = sorted(set(item.row() for item in selected_items))
    cols = sorted(set(item.column() for item in selected_items))
    text = ""
    for row in rows:
        row_data = []
        for col in cols:
            item = table.widget.item(row, col)
            row_data.append(item.text() if item else "")
        text += "\t".join(row_data) + "\n"
    clipboard = QApplication.clipboard()
    clipboard.setText(text)
    QMessageBox.information(table.parent, "موفقیت", "محتوای سلول‌های انتخاب‌شده کپی شد.")
