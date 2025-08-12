import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from modules.custom_widgets import CustomFilter, CustomDialog_Info, CustomModernComboBox
from PyQt5.QtCore import Qt

class TestComponentPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window)
        self.showMaximized()
        layout = QVBoxLayout(self)
        # افزودن نمونه کمبوباکس سفارشی
        combo = CustomModernComboBox(["گزینه اول", "گزینه دوم", "گزینه سوم", "گزینه چهارم"])
        combo.setFixedWidth(220)
        combo.setFixedHeight(40)
        combo.valueChanged.connect(lambda val: print("انتخاب شد:", val))
        layout.addWidget(combo, alignment=Qt.AlignCenter)
        btn = QPushButton("نمایش دیالوگ اطلاعات (CustomDialog_Info)")
        btn.clicked.connect(self.show_info_dialog)
        layout.addWidget(btn)
    def show_info_dialog(self):
        long_text = """
این یک متن تستی طولانی است.

""" + "\n".join([f"این خط شماره {i+1} از متن تستی است." for i in range(50)]) + """

پایان متن تستی.
"""
        dlg = CustomDialog_Info(
            header_text="نمونه دیالوگ اطلاعات",
            main_text=long_text,
            parent=self,
            dialog_height=340
        )
        dlg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestComponentPage()
    window.show()
    sys.exit(app.exec_()) 