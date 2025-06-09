# emoradiacc1/powerlineapp/PowerLineApp-fdbcef7fc87678177f786819d0b9aeed5ed41779/map_window.py

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt

class MapWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # چیدمان اصلی بدون حاشیه
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # ویجت WebEngine برای نمایش نقشه
        self.web_view = QWebEngineView()

        # --- شروع تغییر ---
        # اضافه کردن پخ (گوشه‌های گرد) به ویجت نمایش‌دهنده نقشه
        self.web_view.setStyleSheet("border-radius: 8px;")
        # --- پایان تغییر ---

        self.layout.addWidget(self.web_view, stretch=1)

        # لود فایل HTML نقشه
        html_path = os.path.join(os.getcwd(), "map.html")
        self.web_view.load(QUrl.fromLocalFile(html_path))
