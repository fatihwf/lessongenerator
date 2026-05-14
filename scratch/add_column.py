import sqlite3
import os

db_path = r"c:\Users\USER\Desktop\e\services\bloom-api\bloom_local.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE generated_lessons ADD COLUMN generation_info JSON")
        conn.commit()
        print("Column 'generation_info' added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print("Database not found.")
