import sys
import logging
import traceback
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QMenuBar, QAction, QMenu, QMessageBox, QLabel, QPushButton
from PyQt5.QtGui import QFontDatabase, QFont, QCursor, QIcon
from PyQt5.QtCore import Qt
from modules.lines_window import LinesWindow
from modules.circuits_window import CircuitsWindow
from modules.teams_window import TeamsWindow
from modules.towers_window import TowersWindow
from modules.Maps.OSM.map_window import MapWindow
from modules.database import Database
import time
from modules.custom_widgets import CustomPaper, NoWheelComboBox, CustomDialog_Progress, CustomDialog_Flexible, CustomTableWidget, CustomRightClick, CustomFilter
# from custom_widgets import CustomDialogWidget  # حذف چون دیگر استفاده نمی‌شود
from PyQt5.QtWidgets import QStyle




# تنظیم لاگ برای دیباگ
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
print("1")
# -----------------------------------------------
# Main Window: Creates the main application window with a menu bar for lines, teams, towers, map, and settlement
# -----------------------------------------------


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("مدیریت خطوط برق")
        self.setWindowState(Qt.WindowMaximized)  # Fullscreen
        print("2")
        # Load Vazir font with fallback
        font_db = QFontDatabase()
        # لود فونت:
        font_path = external_path("fonts/Vazir.ttf")
        font_id = font_db.addApplicationFont(font_path)
        if font_id == -1:
            logging.warning("Vazir font not loaded. Using default font (Tahoma).")
            font_family = "Tahoma"  # Fallback font
        else:
            font_family = font_db.applicationFontFamilies(font_id)[0]
        self.default_font = QFont(font_family, 12)
        QApplication.setFont(self.default_font)
        print("3")
        # Main widget and layout
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background: #f0f0f0;")
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        print("4")
        # Create menu bar (RTL)
        self.menu_bar = QMenuBar()
        self.menu_bar.setLayoutDirection(Qt.RightToLeft)
        self.menu_bar.setFont(QFont(font_family, 12))
        self.menu_bar.setCursor(Qt.PointingHandCursor)
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
        self.layout.addWidget(self.menu_bar)

        # Menu actions
        self.home_action = QAction("صفحه اصلی", self)
        self.lines_action = QAction("اطلاعات کلی خطوط", self)
        self.circuits_action = QAction("اطلاعات مدارها", self)
        self.towers_action = QAction("اطلاعات ثابت دکل ها", self)
        self.teams_action = QAction("پرسنل پیمانکار", self)
        # self.test_action = QAction("صفحه تست", self)  # حذف شد



        # Add actions to menu bar
        self.menu_bar.addAction(self.home_action)
        self.menu_bar.addAction(self.lines_action)
        self.menu_bar.addAction(self.circuits_action)
        self.menu_bar.addAction(self.towers_action)
        self.menu_bar.addAction(self.teams_action)
        # self.menu_bar.addAction(self.test_action)  # حذف شد


        print("5")
        # ایجاد منوی اشکالات خط با زیرمنو (راست‌چین و با پس‌زمینه سفید)
        self.faults_menu = QMenu("اشکالات خط ▾", self)
        self.faults_menu.setLayoutDirection(Qt.RightToLeft)
        self.faults_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border-radius: 0px;
                padding: 6px;
                border: 0px solid #e0e0e0;
                box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            }
            QMenu::item {
                text-align: right;
                border-radius: 8px;
                padding: 6px 16px;
                background: transparent;
            }
            QMenu::item:selected {
                background: #f0f0f0;
            }
            QMenu::viewport {
                border-radius: 0px;
                background: transparent;
            }
        """)
        self.electric_faults_action = QAction("اشکالات الکتریکی", self)
        self.mechanical_faults_action = QAction("اشکالات مکانیکی", self)
        self.faults_menu.addAction(self.electric_faults_action)
        self.faults_menu.addAction(self.mechanical_faults_action)
        self.menu_bar.addMenu(self.faults_menu)
        # اتصال اکشن‌ها به پیام ساده
        self.electric_faults_action.triggered.connect(lambda: self.show_custom_info_dialog("اشکالات الکتریکی", "در آینده پیاده‌سازی می‌شود."))
        self.mechanical_faults_action.triggered.connect(lambda: self.show_custom_info_dialog("اشکالات مکانیکی", "در آینده پیاده‌سازی می‌شود."))

        # ایجاد منوی تعمیرات خط با زیرمنو (راست‌چین و استایل مشابه)
        self.repairs_menu = QMenu("تعمیرات خط ▾", self)
        self.repairs_menu.setLayoutDirection(Qt.RightToLeft)
        self.repairs_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border-radius: 0px;
                padding: 6px;
                border: 0px solid #e0e0e0;
                box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            }
            QMenu::item {
                text-align: right;
                border-radius: 8px;
                padding: 6px 16px;
                background: transparent;
            }
            QMenu::item:selected {
                background: #f0f0f0;
            }
            QMenu::viewport {
                border-radius: 0px;
                background: transparent;
            }
        """)
        self.electric_repairs_action = QAction("تعمیرات الکتریکی", self)
        self.mechanical_repairs_action = QAction("تعمیرات مکانیکی", self)
        self.repairs_menu.addAction(self.electric_repairs_action)
        self.repairs_menu.addAction(self.mechanical_repairs_action)
        self.menu_bar.addMenu(self.repairs_menu)
        self.electric_repairs_action.triggered.connect(lambda: self.show_custom_info_dialog("تعمیرات الکتریکی", "در آینده پیاده‌سازی می‌شود."))
        self.mechanical_repairs_action.triggered.connect(lambda: self.show_custom_info_dialog("تعمیرات مکانیکی", "در آینده پیاده‌سازی می‌شود."))

        # Connect actions to functions
        self.home_action.triggered.connect(self.open_home_window)
        self.lines_action.triggered.connect(self.open_lines_window)
        self.circuits_action.triggered.connect(self.open_circuits_window)
        self.towers_action.triggered.connect(self.open_towers_window)
        self.teams_action.triggered.connect(self.open_teams_window)
        # self.test_action.triggered.connect(self.open_test_page)  # حذف شد



        # Current window widget
        self.current_window = None

        # Open home window by default
        self.open_home_window()
    print("6")
    def open_home_window(self):
        try:
            self.clear_current_window()
            self.current_window = MapWindow(self.central_widget)
            self.layout.addWidget(self.current_window)
            self.current_window.show()
            logging.debug("Home window opened successfully")
        except Exception as e:
            logging.error(f"Error in open_home_window: {str(e)}\n{traceback.format_exc()}")
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در باز کردن صفحه اصلی: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()
    print("7")
    def open_lines_window(self):
        try:
            self.clear_current_window()
            self.current_window = LinesWindow(self.central_widget)
            self.current_window.back_action.triggered.disconnect()
            self.current_window.back_action.triggered.connect(self.open_home_window)
            self.layout.addWidget(self.current_window)
            self.current_window.show()
            logging.debug("Lines window opened successfully")
        except Exception as e:
            logging.error(f"Error in open_lines_window: {str(e)}\n{traceback.format_exc()}")
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در باز کردن پنجره اطلاعات خطوط: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()

    def open_circuits_window(self):
        try:
            self.clear_current_window()
            self.current_window = CircuitsWindow(self.central_widget)
            self.current_window.back_action.triggered.disconnect()
            self.current_window.back_action.triggered.connect(self.open_home_window)
            self.layout.addWidget(self.current_window)
            self.current_window.show()
            logging.debug("Circuits window opened successfully")
        except Exception as e:
            logging.error(f"Error in open_circuits_window: {str(e)}\n{traceback.format_exc()}")
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در باز کردن پنجره اطلاعات مدارها: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()

    def open_teams_window(self):
        try:
            self.clear_current_window()
            self.current_window = TeamsWindow(self.central_widget)
            self.current_window.back_action.triggered.disconnect()
            self.current_window.back_action.triggered.connect(self.open_home_window)
            self.layout.addWidget(self.current_window)
            self.current_window.show()
            logging.debug("Teams window opened successfully")
        except Exception as e:
            logging.error(f"Error in open_teams_window: {str(e)}\n{traceback.format_exc()}")
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در باز کردن پنجره پرسنل پیمانکار: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()

    def open_towers_window(self):
        try:
            self.clear_current_window()
            self.current_window = TowersWindow(self.central_widget)
            self.current_window.back_action.triggered.disconnect()
            self.current_window.back_action.triggered.connect(self.open_home_window)
            self.layout.addWidget(self.current_window)
            self.current_window.show()
            logging.debug("Towers window opened successfully")
        except Exception as e:
            logging.error(f"Error in open_towers_window: {str(e)}\n{traceback.format_exc()}")
            dlg = CustomDialog_Flexible(header_text="خطا", main_text=f"خطا در باز کردن پنجره اطلاعات دکل‌ها: {str(e)}", ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxCritical))
            dlg.exec_()
    print("8")
    def clear_current_window(self):
        try:
            # اگر منوی راست‌کلیک باز است، آن را ببند
            from modules.custom_widgets import CustomRightClick
            if CustomRightClick._open_instance is not None:
                CustomRightClick._open_instance.close()
            if self.current_window:
                self.layout.removeWidget(self.current_window)
                self.current_window.hide()
                self.current_window.deleteLater()
                self.current_window = None
                logging.debug("Current window cleared successfully")
        except Exception as e:
            logging.error(f"Error in clear_current_window: {str(e)}\n{traceback.format_exc()}")

    def open_test_page(self):
        pass  # حذف شد


    def closeEvent(self, event):
        try:
            db = Database()
            db.close()
            event.accept()
            logging.debug("Database closed and application exited")
        except Exception as e:
            logging.error(f"Error closing database: {str(e)}\n{traceback.format_exc()}")
            event.accept()
    print("9")

class TestPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #f0f0f0;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)  # تغییر از AlignCenter به AlignTop
        self._custom_dialog = None
        self._dialog_event_filter_installed = False
        # عنوان بزرگ
        title = QLabel("صفحه تست کامپوننت‌ها")
        title.setFont(QFont("Vazir", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        # توضیح کوتاه
        desc = QLabel("در این صفحه می‌توانید کامپوننت‌های سفارشی را تست و مشاهده کنید.")
        desc.setFont(QFont("Vazir", 13))
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #555; margin-bottom: 18px;")
        layout.addWidget(desc)
        # (دکمه‌ها و جدول تستی حذف شدند)

    def contextMenuEvent(self, event):
        if self._custom_dialog is not None:
            self._custom_dialog.close()
        from PyQt5.QtWidgets import QVBoxLayout, QLabel
        from PyQt5.QtCore import Qt
        item_style = """
            QLabel {
                font-size: 16px;
                color: #222;
                padding: 10px 5px;
                background: transparent;
                border: none;
                text-align: right;
                border-radius: 12px;
            }
            QLabel:hover {
                background: #f0f0f0;
                color: #017BCC;
                border-radius: 12px;
            }
        """
        items = [
            ("کپی", "Resources\Icons\RightClick_Copy.png"),
            ("حذف", "Resources\Icons\RightClick_Delete.png"),
            ("ویرایش", "Resources\Icons\RightClick_Edit.png"),
        ]
        self._custom_dialog = CustomPaper(self, background_color="#FFFFFF", corner_radius=8, width=120, height=160)
        layout = QVBoxLayout(self._custom_dialog.frame)
        layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.setSpacing(0)
        for text, icon_path in items:
            item = QLabel()
            item.setTextFormat(Qt.RichText)
            # فاصله مناسب بین آیکون و متن (margin-left: 12px)
            item.setText(
                f"<table style='border:none;' dir='rtl' align='right'><tr>"
                f"<td style='border:none; padding-left:0; padding-right:12px; font-size:16px; color:#222; text-align:right;'>{text}</td>"
                f"<td style='border:none; padding-left:0; padding-right:0;'><img src='{icon_path}' width='18' height='18'></td>"
                f"</tr></table>"
            )
            item.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setStyleSheet(item_style)
            item.setCursor(Qt.PointingHandCursor)
            def make_mouse_press(label):
                def handler(event):
                    self._custom_dialog.close()
                return handler
            item.mousePressEvent = make_mouse_press(item)
            layout.addWidget(item)
        self._custom_dialog.setFixedSize(120, 160)
        # نمایش دیالوگ در محل کلیک راست
        pos = event.globalPos()
        self._custom_dialog.move(pos.x(), pos.y())
        self._custom_dialog.show()
        if not self._dialog_event_filter_installed:
            self.installEventFilter(self)
            self._dialog_event_filter_installed = True

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent
        if self._custom_dialog is not None and self._custom_dialog.isVisible():
            if event.type() == QEvent.MouseButtonPress:
                # اگر کلیک خارج از دیالوگ بود، دیالوگ را ببند
                if not self._custom_dialog.geometry().contains(event.globalPos()):
                    self._custom_dialog.close()
                    self._custom_dialog = None
        return super().eventFilter(obj, event)

    def show_custom_info_dialog(self, title, msg):
        dlg = CustomDialog_Flexible(header_text=title, main_text=msg, ok_text="باشه", parent=self, icon=self.style().standardIcon(QStyle.SP_MessageBoxInformation))
        dlg.exec_()

    def show_custom_filter(self):
        from PyQt5.QtCore import QPoint
        dialog = CustomFilter(self)
        # نمایش دیالوگ در بالای صفحه تست (زیر دکمه)
        btn_geom = self.filter_btn.geometry()
        btn_pos = self.filter_btn.mapToGlobal(btn_geom.bottomLeft())
        dialog.show_at(btn_pos, self)

    def show_custom_filter2(self):
        from PyQt5.QtCore import QPoint
        from custom_widgets import CustomFilter2
        dialog = CustomFilter2(self)
        # نمایش دیالوگ در بالای صفحه تست (زیر دکمه)
        btn_geom = self.filter2_btn.geometry()
        btn_pos = self.filter2_btn.mapToGlobal(btn_geom.bottomLeft())
        dialog.show_at(btn_pos, self)

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)

def external_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)

def get_user_documents_dir():
    if sys.platform == 'win32':
        from ctypes import windll, create_unicode_buffer
        CSIDL_PERSONAL = 5
        SHGFP_TYPE_CURRENT = 0
        buf = create_unicode_buffer(260)
        windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        return buf.value
    else:
        return os.path.expanduser('~/Documents')

def get_user_appdata_dir():
    import sys, os
    if sys.platform == 'win32':
        return os.path.join(os.environ['APPDATA'], 'PowerLineApp')
    else:
        return os.path.expanduser('~/.local/share/PowerLineApp')

if __name__ == "__main__":
    try:
        import os
        import signal
        print("شروع اجرای برنامه...")
        start_time = time.time()
        logging.debug(f"[TIME] Program start: {start_time}")
        # اگر QApplication قبلاً ساخته شده باشد، دوباره نساز
        app = QApplication.instance()
        print(10)
        if app is None:
            print(11)
            app = QApplication(sys.argv)
        print("QApplication ساخته شد")
        logging.debug(f"[TIME] QApplication created: {time.time() - start_time:.3f} s")
        window = MainWindow()
        logging.debug(f"[TIME] MainWindow created: {time.time() - start_time:.3f} s")
        window.show()
        logging.debug(f"[TIME] Window shown: {time.time() - start_time:.3f} s")
        # هندل سیگنال Ctrl+C برای بستن تمیز برنامه
        signal.signal(signal.SIGINT, lambda *args: app.quit())
        sys.exit(app.exec_())
    except Exception as e:
        import traceback
        log_dir = get_user_appdata_dir()
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'error.log')
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise
