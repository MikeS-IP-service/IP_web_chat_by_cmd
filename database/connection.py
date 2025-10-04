import sqlite3
from config.settings import DB_CONFIG

class DatabaseConnection:
    def __init__(self):
        self.db_path = DB_CONFIG.DB_PATH
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                service_type TEXT,
                booking_date TEXT,
                booking_time TEXT,
                client_name TEXT,
                client_phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ База данных инициализирована")