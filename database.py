import sqlite3
import logging

# تنظیم لاگ برای دیباگ
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:
    _instance = None
    _db_path = 'power_lines.db'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
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
                line_code TEXT NOT NULL UNIQUE,
                voltage_level INTEGER,
                line_name TEXT NOT NULL,
                dispatch_code TEXT,
                total_towers INTEGER,
                tension_towers INTEGER,
                suspension_towers INTEGER,
                line_length REAL,
                circuit_length REAL,
                plain_area TEXT,
                semi_mountainous TEXT,
                rough_terrain TEXT,
                team_leader TEXT NOT NULL,
                operation_year INTEGER,
                wire_type TEXT,
                tower_type TEXT,
                bundle_count INTEGER,
                circuit_count INTEGER
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
        
        # Add longitude and latitude columns if they don't exist
        try:
            cursor.execute('ALTER TABLE towers ADD COLUMN longitude REAL')
        except sqlite3.OperationalError:
            pass  # Column already exists
            
        try:
            cursor.execute('ALTER TABLE towers ADD COLUMN latitude REAL')
        except sqlite3.OperationalError:
            pass  # Column already exists
            
        # Add supervisor column to lines table if it doesn't exist
        try:
            cursor.execute('ALTER TABLE lines ADD COLUMN supervisor TEXT')
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
