from database.connection import DatabaseConnection
from database.models import Booking

class BookingRepository:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def save_booking(self, booking: Booking) -> int:
        """Сохранение записи - ЭТОТ КОД УЖЕ РАБОТАЕТ"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bookings 
            (user_id, username, service_type, booking_date, booking_time, client_name, client_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            booking.user_id,
            booking.username,
            booking.service_type,
            booking.booking_date,
            booking.booking_time,
            booking.client_name,
            booking.client_phone
        ))
        
        booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return booking_id
    
    def get_user_bookings(self, user_id: int):
        """Получение записей пользователя - ЭТОТ КОД УЖЕ РАБОТАЕТ"""
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
        """Получение всех записей - ЭТОТ КОД УЖЕ РАБОТАЕТ"""
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
    
    def get_booked_times(self, date: str):
        """Получение занятого времени на дату - ЭТОТ КОД УЖЕ РАБОТАЕТ"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT booking_time FROM bookings WHERE booking_date = ?",
            (date,)
        )
        booked_times = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return booked_times