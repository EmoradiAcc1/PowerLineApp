# emoradiacc1/powerlineapp/PowerLineApp-fdbcef7fc87678177f786819d0b9aeed5ed41779/main.py

import sys
# --- شروع تغییر ۱ ---
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QMenuBar, QAction, QMessageBox, QSpacerItem, QSizePolicy
# --- پایان تغییر ۱ ---
from PyQt5.QtGui import QFontDatabase, QFont, QCursor
from PyQt5.QtCore import Qt
from lines_window import LinesWindow
from teams_window import TeamsWindow
from towers_window import TowersWindow
from map_window import MapWindow
from database import Database

# -----------------------------------------------
# Main Window: Creates the main application window with a menu bar for lines, teams, towers, map, and settlement
# -----------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("مدیریت خطوط برق")
        self.setWindowState(Qt.WindowMaximized)  # Fullscreen

        # Load Vazir font with fallback
        font_db = QFontDatabase()
        font_id = font_db.addApplicationFont("fonts/Vazir.ttf")
        if font_id == -1:
            print("Warning: Vazir font not loaded. Using default font.")
            font_family = "Tahoma"  # Fallback font
        else:
            font_family = font_db.applicationFontFamilies(font_id)[0]
        self.default_font = QFont(font_family, 12)
        QApplication.setFont(self.default_font)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Create menu bar (RTL)
        self.menu_bar = QMenuBar()
        self.menu_bar.setLayoutDirection(Qt.RightToLeft)
        self.menu_bar.setFont(QFont(font_family, 12))
        self.menu_bar.setCursor(Qt.PointingHandCursor)
        
        # --- شروع تغییر ۲ ---
        self.menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: white;
                padding: 5px;
                border-radius: 5px;
            }
            QMenuBar::item {
                padding: 8px 15px;
                background-color: transparent;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #f0f0f0;
            }
            QMenuBar::item:pressed {
                background-color: #e0e0e0;
            }
        """)
        # --- پایان تغییر ۲ ---

        self.layout.addWidget(self.menu_bar)

        # --- شروع تغییر ۳ ---
        # اضافه کردن یک فاصله ثابت ۱۰ پیکسلی زیر منو
        self.layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        # --- پایان تغییر ۳ ---

        # Menu actions
        self.home_action = QAction("صفحه اصلی", self)
        self.lines_action = QAction("اطلاعات خطوط", self)
        self.teams_action = QAction("پرسنل پیمانکار", self)
        self.towers_action = QAction("اطلاعات دکل‌ها", self)
        self.settlement_action = QAction("تسویه حساب جنسی", self)

        # Add actions to menu bar
        self.menu_bar.addAction(self.home_action)
        self.menu_bar.addAction(self.lines_action)
        self.menu_bar.addAction(self.teams_action)
        self.menu_bar.addAction(self.towers_action)
        self.menu_bar.addAction(self.settlement_action)

        # Connect actions to functions
        self.home_action.triggered.connect(self.open_home_window)
        self.lines_action.triggered.connect(self.open_lines_window)
        self.teams_action.triggered.connect(self.open_teams_window)
        self.towers_action.triggered.connect(self.open_towers_window)
        self.settlement_action.triggered.connect(self.open_settlement_window)

        # Current window widget
        self.current_window = None

        # Open home window by default
        self.open_home_window()


    def open_home_window(self):
        try:
            self.clear_current_window()
            self.current_window = MapWindow(self.central_widget)
            self.layout.addWidget(self.current_window)
            self.current_window.show()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن صفحه اصلی: {str(e)}")
            print(f"Error in open_home_window: {str(e)}")


    def open_lines_window(self):
        try:
            self.clear_current_window()
            self.current_window = LinesWindow(self.central_widget)
            self.current_window.back_action.triggered.disconnect()
            self.current_window.back_action.triggered.connect(self.open_home_window)
            self.layout.addWidget(self.current_window)
            self.current_window.show()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن پنجره اطلاعات خطوط: {str(e)}")
            print(f"Error in open_lines_window: {str(e)}")

    def open_teams_window(self):
        try:
            self.clear_current_window()
            self.current_window = TeamsWindow(self.central_widget)
            self.current_window.back_action.triggered.disconnect()
            self.current_window.back_action.triggered.connect(self.open_home_window)
            self.layout.addWidget(self.current_window)
            self.current_window.show()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن پنجره پرسنل پیمانکار: {str(e)}")
            print(f"Error in open_teams_window: {str(e)}")

    def open_towers_window(self):
        try:
            self.clear_current_window()
            self.current_window = TowersWindow(self.central_widget)
            self.current_window.back_action.triggered.disconnect()
            self.current_window.back_action.triggered.connect(self.open_home_window)
            self.layout.addWidget(self.current_window)
            self.current_window.show()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن پنجره اطلاعات دکل‌ها: {str(e)}")
            print(f"Error in open_towers_window: {str(e)}")

    def open_settlement_window(self):
        try:
            self.clear_current_window()
            QMessageBox.information(self, "تسویه حساب جنسی", "پنجره تسویه حساب جنسی هنوز پیاده‌سازی نشده است.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن پنجره تسویه حساب جنسی: {str(e)}")
            print(f"Error in open_settlement_window: {str(e)}")

    def clear_current_window(self):
        try:
            if self.current_window:
                self.layout.removeWidget(self.current_window)
                self.current_window.hide()
                self.current_window.deleteLater()
                self.current_window = None
        except Exception as e:
            print(f"Error in clear_current_window: {str(e)}")

    def closeEvent(self, event):
        try:
            db = Database()
            db.close()
            event.accept()
        except Exception as e:
            print(f"Error closing database: {str(e)}")
            event.accept()

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application error: {str(e)}")
