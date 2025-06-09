import sqlite3

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.conn = sqlite3.connect('power_lines.db', check_same_thread=False)
            cls._instance.cursor = cls._instance.conn.cursor()
            cls._instance.create_tables()
        return cls._instance

    def create_tables(self):
        # Create lines table if not exists
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
                circuit_length TEXT,
                plain_area TEXT,
                semi_mountainous TEXT,
                rough_terrain TEXT,
                supervisor TEXT,
                team_leader TEXT,
                operation_year TEXT,
                wire_type TEXT,
                tower_type TEXT,
                bundle_count TEXT
            )
        ''')
        self.conn.commit()

        # Create teams table if not exists
        self.cursor.execute('''
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
        self.conn.commit()

        # Create towers table if not exists
        self.cursor.execute('''
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
                UNIQUE(line_name, tower_number)
            )
        ''')
        self.conn.commit()

    def execute_query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")

    def fetch_all(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")

    def close(self):
        self.conn.close()

    def __del__(self):
        pass  # Avoid closing connection since it's shared
