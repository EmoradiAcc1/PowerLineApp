# emoradiacc1/powerlineapp/PowerLineApp-fdbcef7fc87678177f786819d0b9aeed5ed41779/map_window.py

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from database import Database
import json

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

        # لود فایل HTML نقشه
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(current_dir, "map.html")
        self.web_view.load(QUrl.fromLocalFile(html_path))
        self.web_view.loadFinished.connect(self.on_load_finished)

    def show_towers(self):
        try:
            # دریافت همه دکل‌ها به همراه سطح ولتاژ
            query = """
                SELECT t.tower_number, t.latitude, t.longitude, t.line_name, l.voltage_level 
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
                            'voltage': voltage
                        })
                except (ValueError, TypeError):
                    continue

            # ارسال به نقشه
            if towers_data:
                js_code = f"updateTowers({json.dumps(towers_data)});"
                self.web_view.page().runJavaScript(js_code)

        except Exception as e:
            print(f"خطا در نمایش دکل‌ها: {e}")

    def on_load_finished(self, ok):
        if ok:
            self.show_towers()
