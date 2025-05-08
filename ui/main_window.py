from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMenuBar, QAction, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.lines.lines_window import LinesWindow

class MainWindow(QMainWindow):
    def __init__(self, font_family="Vazir"):
        super().__init__()
        self.setWindowTitle("مدیریت خطوط برق")
        self.setWindowState(Qt.WindowMaximized)  # Fullscreen

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Create menu bar (RTL)
        self.menu_bar = QMenuBar()
        self.menu_bar.setLayoutDirection(Qt.RightToLeft)
        self.menu_bar.setFont(QFont(font_family, 12))  # تنظیم صریح فونت
        self.layout.addWidget(self.menu_bar)

        # Menu actions
        self.lines_action = QAction("اطلاعات خطوط", self)
        self.teams_action = QAction("اکیپ‌ها", self)
        self.settlement_action = QAction("تسویه حساب جنسی", self)

        # تنظیم فونت برای اکشن‌ها
        for action in [self.lines_action, self.teams_action, self.settlement_action]:
            action.setFont(QFont(font_family, 12))

        # Add actions to menu bar
        self.menu_bar.addAction(self.lines_action)
        self.menu_bar.addAction(self.teams_action)
        self.menu_bar.addAction(self.settlement_action)

        # Connect actions to functions
        self.lines_action.triggered.connect(self.open_lines_window)
        self.teams_action.triggered.connect(self.open_teams_window)
        self.settlement_action.triggered.connect(self.open_settlement_window)

        # Add empty widget as default view
        self.empty_widget = QWidget()
        self.layout.addWidget(self.empty_widget)

        # Current window widget
        self.current_window = None

    def open_lines_window(self):
        try:
            self.clear_current_window()
            self.current_window = LinesWindow(self.central_widget)
            self.layout.removeWidget(self.empty_widget)
            self.empty_widget.hide()
            self.layout.addWidget(self.current_window)
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن پنجره اطلاعات خطوط: {str(e)}")
            print(f"Error in open_lines_window: {str(e)}")

    def open_teams_window(self):
        try:
            self.clear_current_window()
            QMessageBox.information(self, "اکیپ‌ها", "پنجره اکیپ‌ها هنوز پیاده‌سازی نشده است.")
            self.layout.addWidget(self.empty_widget)
            self.empty_widget.show()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن پنجره اکیپ‌ها: {str(e)}")
            print(f"Error in open_teams_window: {str(e)}")

    def open_settlement_window(self):
        try:
            self.clear_current_window()
            QMessageBox.information(self, "تسویه حساب جنسی", "پنجره تسویه حساب جنسی هنوز پیاده‌سازی نشده است.")
            self.layout.addWidget(self.empty_widget)
            self.empty_widget.show()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن پنجره تسویه حساب جنسی: {str(e)}")
            print(f"Error in open_settlement_window: {str(e)}")

    def clear_current_window(self):
        try:
            if self.current_window:
                self.layout.removeWidget(self.current_window)
                self.current_window.deleteLater()
                self.current_window = None
            if not self.empty_widget.isVisible():
                self.layout.addWidget(self.empty_widget)
                self.empty_widget.show()
        except Exception as e:
            print(f"Error in clear_current_window: {str(e)}")
