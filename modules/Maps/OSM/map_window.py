# emoradiacc1/powerlineapp/PowerLineApp-fdbcef7fc87678177f786819d0b9aeed5ed41779/map_window.py

import sys
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import pyqtSlot, QObject
from modules.database import Database
import json
from modules.custom_widgets import CustomDialog_Info

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

class JSBridge(QObject):
    @pyqtSlot(str, str)
    def showLineInfoDialog(self, title, html):
        dlg = CustomDialog_Info(header_text=title, main_text=html, parent=None, dialog_height=420)
        dlg.exec_()

class MapWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        
        # چیدمان اصلی - بدون حاشیه و فاصله
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # ایجاد و تنظیم نمای وب
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # QWebChannel setup
        self.channel = QWebChannel()
        self.js_bridge = JSBridge()
        self.channel.registerObject('pyHandler', self.js_bridge)
        self.web_view.page().setWebChannel(self.channel)

        # لود فایل HTML نقشه
        map_path = resource_path("modules/Maps/OSM/map.html")
        self.web_view.load(QUrl.fromLocalFile(map_path))
        self.web_view.loadFinished.connect(self.on_load_finished)

    def show_towers(self):
        try:
            # دریافت همه دکل‌ها به همراه سطح ولتاژ
            query = """
                SELECT t.tower_number, t.latitude, t.longitude, t.line_name, l.Voltage, t.tower_structure, t.tower_type, t.base_type 
                FROM towers t
                LEFT JOIN lines l ON t.line_name = l.line_name
                WHERE t.latitude IS NOT NULL 
                AND t.longitude IS NOT NULL
                AND t.latitude != ''
                AND t.longitude != ''
            """
            towers = self.db.fetch_all(query)
            
            towers_data = []
            for tower in towers:
                try:
                    lat = float(tower[1])
                    lng = float(tower[2])
                    if -90 <= lat <= 90 and -180 <= lng <= 180:  # اعتبارسنجی مختصات
                        voltage = tower[4] if tower[4] else '0'
                        towers_data.append({
                            'name': f"دکل {tower[0]} - خط {tower[3]} ({voltage} کیلوولت)",
                            'lat': lat,
                            'lng': lng,
                            'voltage': voltage,
                            'tower_structure': tower[5] or '',
                            'tower_type': tower[6] or '',
                            'base_type': tower[7] or ''
                        })
                except (ValueError, TypeError):
                    continue

            # ارسال به نقشه
            if towers_data:
                js_code = f"updateTowers({json.dumps(towers_data)});"
                self.web_view.page().runJavaScript(js_code)

        except Exception as e:
            print(f"خطا در نمایش دکل‌ها: {e}")

    def show_lines(self):
        try:
            # دریافت خطوط از جدول دکل‌ها که مختصات دارند
            query = """
                SELECT DISTINCT t.line_name, l.Voltage 
                FROM towers t
                LEFT JOIN lines l ON t.line_name = l.line_name
                WHERE t.latitude IS NOT NULL 
                AND t.longitude IS NOT NULL
                AND t.latitude != ''
                AND t.longitude != ''
                AND t.line_name IS NOT NULL
                AND t.line_name != ''
                ORDER BY l.Voltage DESC, t.line_name
            """
            lines = self.db.fetch_all(query)
            lines_data = []
            for line in lines:
                lines_data.append({
                    'name': line[0],
                    'voltage': line[1] or ''
                })
            js_code = f"updateLines({json.dumps(lines_data)});"
            self.web_view.page().runJavaScript(js_code)
        except Exception as e:
            print(f"خطا در نمایش خطوط: {e}")

    def send_all_lines_info(self):
        try:
            query = """
                SELECT Line_Code, Voltage, Line_Name, Dispatch_Code, Circuit_Number, Bundle_Number,
                       Line_Length, Circuit_Length, Tower_Type, Wire_Type, Total_Towers,
                       Tension_Towers, Suspension_Towers, Plain_Area, Semi_Mountainous_Area,
                       Rough_Terrain_Area, Operation_Year, Team_Leader, Line_Expert
                FROM lines
            """
            rows = self.db.fetch_all(query)
            columns = [
                "Line_Code", "Voltage", "Line_Name", "Dispatch_Code", "Circuit_Number", "Bundle_Number",
                "Line_Length", "Circuit_Length", "Tower_Type", "Wire_Type", "Total_Towers",
                "Tension_Towers", "Suspension_Towers", "Plain_Area", "Semi_Mountainous_Area",
                "Rough_Terrain_Area", "Operation_Year", "Team_Leader", "Line_Expert"
            ]
            all_lines = []
            for row in rows:
                all_lines.append({col: row[idx] for idx, col in enumerate(columns)})
            js_code = f"window.allLinesInfo = {json.dumps(all_lines, ensure_ascii=False)};"
            self.web_view.page().runJavaScript(js_code)
        except Exception as e:
            print(f"خطا در ارسال اطلاعات کامل خطوط: {e}")

    def on_load_finished(self, ok):
        if ok:
            self.show_towers()
            self.show_lines()
            self.send_all_lines_info()
