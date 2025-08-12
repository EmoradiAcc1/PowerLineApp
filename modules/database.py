import os
import sys
import sqlite3
import logging

# تنظیم لاگ برای دیباگ
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
    if sys.platform == 'win32':
        return os.path.join(os.environ['APPDATA'], 'PowerLineApp')
    else:
        return os.path.expanduser('~/.local/share/PowerLineApp')

class Database:
    _instance = None
    _db_path = os.path.join(get_user_appdata_dir(), 'power_lines.db')

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            # اطمینان از وجود پوشه دیتابیس
            os.makedirs(os.path.dirname(cls._db_path), exist_ok=True)
            # اگر دیتابیس وجود ندارد، آن را از سورس کنار برنامه کپی کن
            if not os.path.exists(cls._db_path):
                try:
                    src_path = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), '_internal', 'database', 'power_lines.db')
                    if os.path.exists(src_path):
                        import shutil
                        shutil.copy(src_path, cls._db_path)
                except Exception as e:
                    logging.error(f"Failed to copy initial database: {e}")
            # اتصال اولیه برای ایجاد جداول
            try:
                with sqlite3.connect(cls._db_path) as conn:
                    cursor = conn.cursor()
                    cls._instance.create_tables(cursor)
                    conn.commit()
                logging.info("Database tables checked/created successfully.")
            except sqlite3.Error as e:
                logging.error(f"Failed to create/check tables: {e}")
                raise
        return cls._instance

    def _get_connection(self):
        """یک اتصال جدید به پایگاه داده برمی‌گرداند."""
        try:
            conn = sqlite3.connect(self._db_path, check_same_thread=False)
            return conn
        except sqlite3.Error as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def create_tables(self, cursor):
        """جداول را در صورت عدم وجود ایجاد می‌کند."""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Line_Code TEXT NOT NULL UNIQUE,
                Voltage TEXT,
                Line_Name TEXT NOT NULL,
                Dispatch_Code TEXT,
                Circuit_Number INTEGER,
                Bundle_Number INTEGER,
                Line_length INTEGER,
                Circuit_length INTEGER,
                Total_Towers INTEGER,
                Tension_Towers INTEGER,
                Suspension_Towers INTEGER,
                Plain_Area INTEGER,
                Semi_Mountainous_Area INTEGER,
                Rough_Terrain_Area INTEGER,
                Operation_Year INTEGER,
                Wire_Type TEXT,
                Tower_Type TEXT,
                Team_Leader TEXT,
                Line_Expert TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                national_code TEXT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                father_name TEXT,
                position TEXT,
                hire_date TEXT,
                phone_number TEXT,
                team_leader TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS towers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                line_name TEXT NOT NULL,
                tower_number TEXT NOT NULL,
                tower_structure TEXT,
                tower_type TEXT,
                base_type TEXT,
                height_leg_a TEXT,
                height_leg_b TEXT,
                height_leg_c TEXT,
                height_leg_d TEXT,
                insulator_type_c1_r TEXT,
                insulator_type_c1_s TEXT,
                insulator_type_c1_t TEXT,
                insulator_type_c2_r TEXT,
                insulator_type_c2_s TEXT,
                insulator_type_c2_t TEXT,
                insulator_count_c1_r TEXT,
                insulator_count_c1_s TEXT,
                insulator_count_c1_t TEXT,
                insulator_count_c2_r TEXT,
                insulator_count_c2_s TEXT,
                insulator_count_c2_t TEXT,
                FOREIGN KEY (line_name) REFERENCES lines(line_name) ON DELETE CASCADE,
                UNIQUE(line_name, tower_number)            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS circuits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Circuit_Code TEXT NOT NULL UNIQUE,
                Circuit_Name TEXT NOT NULL,
                Line_Name TEXT,
                Voltage TEXT,
                Dispatch_Code TEXT,
                Circuit_Number INTEGER,
                Bundle_Number INTEGER,
                Circuit_length INTEGER,
                Total_Towers INTEGER,
                Tension_Towers INTEGER,
                Suspension_Towers INTEGER,
                Plain_Area INTEGER,
                Semi_Mountainous_Area INTEGER,
                Rough_Terrain_Area INTEGER,
                Operation_Year INTEGER,
                Wire_Type TEXT,
                Insulator_Type TEXT,
                Tower_Type TEXT,
                Team_Leader TEXT,
                Circuit_Expert TEXT,
                Status TEXT,
                Capacity TEXT,
                Current_Rating TEXT,
                Emergency_Rating TEXT,
                FOREIGN KEY (Line_Name) REFERENCES lines(Line_Name) ON DELETE SET NULL
            )
        ''')
        
        # Add longitude and latitude columns if they don't exist
        try:
            cursor.execute('ALTER TABLE towers ADD COLUMN longitude REAL')
        except sqlite3.OperationalError:
            pass  # Column already exists
            
        try:
            cursor.execute('ALTER TABLE towers ADD COLUMN latitude REAL')
        except sqlite3.OperationalError:
            pass  # Column already exists
            
        # Add Insulator_Type column to circuits table if it doesn't exist
        try:
            cursor.execute('ALTER TABLE circuits ADD COLUMN Insulator_Type TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
            


    def execute_query(self, query, params=()):
        """یک کوئری اجرا کرده و تغییرات را ثبت می‌کند (برای INSERT, UPDATE, DELETE)."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                logging.debug(f"Executed query: {query}")
        except sqlite3.Error as e:
            logging.error(f"Query failed: {query} - {e}")
            raise Exception(f"Database error: {str(e)}")

    def fetch_all(self, query, params=()):
        """تمام نتایج یک کوئری SELECT را برمی‌گرداند."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Fetch failed: {query} - {e}")
            raise Exception(f"Database error: {str(e)}")

    def close(self):
        # این متد دیگر نیازی به کاری ندارد چون اتصال در هر عملیات باز و بسته می‌شود.
        logging.info("Database instance is being cleaned up.")
        pass
