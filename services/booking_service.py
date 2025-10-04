from datetime import datetime, timedelta
from database.connection import DatabaseConnection

class BookingService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.work_hours = [f"{hour:02d}:00" for hour in range(9, 18)]
        self.services = {
            'patent': '📄 Патентование',
            'trademark': '🏢 Товарные знаки', 
            'consultation': '💬 Консультации по вопросам интеллектуальной собственности'
        }
    
    def get_available_dates(self):
        today = datetime.now().date()
        available_dates = []
        
        for i in range(1, 31):
            date = today + timedelta(days=i)
            if date.weekday() < 5:
                available_dates.append((date.strftime("%d.%m.%Y"), date))
        return available_dates
    
    def get_available_times(self, selected_date: str):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT booking_time FROM bookings WHERE booking_date = ?",
            (selected_date,)
        )
        booked_times = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return [time for time in self.work_hours if time not in booked_times]
    
    def save_booking(self, user_data: dict) -> int:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bookings 
            (user_id, username, service_type, booking_date, booking_time, client_name, client_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data['user_id'],
            user_data['username'],
            user_data['service'],
            user_data['date'],
            user_data['time'],
            user_data['client_name'],
            user_data['client_phone']
        ))
        
        booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return booking_id
    
    def get_user_bookings(self, user_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT service_type, booking_date, booking_time, client_name, client_phone, created_at
            FROM bookings 
            WHERE user_id = ? OR client_phone IN (
                SELECT client_phone FROM bookings WHERE user_id = ?
            )
            ORDER BY booking_date, booking_time
        ''', (user_id, user_id))
        
        bookings = cursor.fetchall()
        conn.close()
        return bookings
    
    def get_all_bookings(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT client_name, service_type, booking_date, booking_time, client_phone, created_at
            FROM bookings 
            ORDER BY booking_date, booking_time
        ''')
        
        bookings = cursor.fetchall()
        conn.close()
        return bookings
    
    def get_service_name(self, service_key: str) -> str:
        return self.services.get(service_key, service_key)