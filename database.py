import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('power_lines.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # ایجاد جدول lines اگه وجود نداشته باشه
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                line_code TEXT NOT NULL UNIQUE,
                voltage_level TEXT,
                line_name TEXT NOT NULL,
                dispatch_code TEXT,
                total_towers TEXT,
                tension_towers TEXT,
                suspension_towers TEXT,
                line_length TEXT,
                circuit_length TEXT
            )
        ''')
        self.conn.commit()

        # بررسی و افزودن ستون‌های جدید اگه وجود نداشته باشن
        new_columns = [
            ('plain_area', 'TEXT'),
            ('semi_mountainous', 'TEXT'),
            ('rough_terrain', 'TEXT'),
            ('supervisor', 'TEXT'),
            ('team_leader', 'TEXT'),
            ('operation_year', 'TEXT'),
            ('wire_type', 'TEXT'),
            ('tower_type', 'TEXT'),
            ('bundle_count', 'TEXT')
        ]

        # دریافت ستون‌های فعلی جدول
        self.cursor.execute("PRAGMA table_info(lines)")
        existing_columns = [col[1] for col in self.cursor.fetchall()]

        # افزودن ستون‌های جدید اگه وجود نداشته باشن
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                self.cursor.execute(f"ALTER TABLE lines ADD COLUMN {column_name} {column_type}")
        
        self.conn.commit()

    def execute_query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def __del__(self):
        self.conn.close()