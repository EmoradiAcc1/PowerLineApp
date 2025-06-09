import sqlite3

def update_database():
    try:
        conn = sqlite3.connect('power_lines.db')
        cursor = conn.cursor()

        # Create a new table with English column names
        cursor.execute('''
            CREATE TABLE towers_new (
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
                longitude REAL,
                latitude REAL,
                FOREIGN KEY (line_name) REFERENCES lines(line_name) ON DELETE CASCADE,
                UNIQUE(line_name, tower_number)
            )
        ''')

        # Copy data from old table to new table
        cursor.execute('''
            INSERT INTO towers_new 
            SELECT 
                id, line_name, tower_number, tower_structure, tower_type, base_type,
                height_leg_a, height_leg_b, height_leg_c, height_leg_d,
                insulator_type_c1_r, insulator_type_c1_s, insulator_type_c1_t,
                insulator_type_c2_r, insulator_type_c2_s, insulator_type_c2_t,
                insulator_count_c1_r, insulator_count_c1_s, insulator_count_c1_t,
                insulator_count_c2_r, insulator_count_c2_s, insulator_count_c2_t,
                longitude, latitude
            FROM towers
        ''')

        # Drop the old table
        cursor.execute('DROP TABLE towers')

        # Rename the new table
        cursor.execute('ALTER TABLE towers_new RENAME TO towers')

        conn.commit()
        print("Database updated successfully!")

    except Exception as e:
        print(f"Error updating database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    update_database()
