import os
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QApplication

def load_font(app):
    # ساخت مسیر مطلق به فایل فونت
    base_path = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_path, "..", "fonts", "Vazir.ttf")
    print(f"Attempting to load font from: {font_path}")
    
    # بررسی وجود فایل
    if not os.path.exists(font_path):
        print(f"Error: Font file not found at {font_path}")
        font_family = "Tahoma"  # فونت جایگزین
    else:
        font_db = QFontDatabase()
        font_id = font_db.addApplicationFont(font_path)
        if font_id == -1:
            print("Warning: Vazir font not loaded. Using default font.")
            font_family = "Tahoma"  # فونت جایگزین
        else:
            font_families = font_db.applicationFontFamilies(font_id)
            font_family = font_families[0] if font_families else "Tahoma"
            print(f"Font loaded successfully: {font_family}")
    
    # اعمال فونت به صورت جهانی
    default_font = QFont(font_family, 12)
    app.setFont(default_font)
    
    return font_family
