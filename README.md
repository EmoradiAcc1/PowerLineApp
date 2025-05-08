# PowerLineApp
برنامه مدیریت خطوط برق با رابط کاربری PyQt5

## ساختار پروژه
- `fonts/`: شامل فونت Vazir.ttf
- `ui/`: فایل‌های رابط کاربری
  - `lines/`: پنجره اطلاعات خطوط (lines_window.py، lines_table.py، lines_toolbar.py، line_input_dialog.py)
  - `main_window.py`: پنجره اصلی برنامه
- `utils/`: ابزارهای کمکی (font_loader.py)
- `database.py`: مدیریت دیتابیس
- `main.py`: فایل اصلی برای اجرای برنامه
- `styles.qss`: استایل‌های ظاهری برنامه

## وابستگی‌ها
- Python 3.8+
- PyQt5
- pandas

## نصب و اجرا
1. وابستگی‌ها رو نصب کن:
   ```bash
   pip install -r requirements.txt
