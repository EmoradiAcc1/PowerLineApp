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
        self.layout.setContentsMargins(0, 0, 0, 0)  # حذف حاشیه‌ها
        self.layout.setSpacing(0)  # حذف فاصله بین ویجت‌ها

        # ویجت WebEngine برای نمایش نقشه
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view, stretch=1)  # گسترش کامل ویجت

        # لود فایل HTML نقشه
        html_path = os.path.join(os.getcwd(), "map.html")
        self.web_view.load(QUrl.fromLocalFile(html_path))
