import pandas as pd
from datetime import datetime
import os
from services.booking_service import BookingService

class ExcelExportService:
    def __init__(self):
        self.booking_service = BookingService()
        self.export_folder = "exports"
        self._ensure_export_folder()
    
    def _ensure_export_folder(self):
        """Создает папку для экспорта если ее нет"""
        if not os.path.exists(self.export_folder):
            os.makedirs(self.export_folder)
    
    def export_bookings_to_excel(self) -> str:
        """Экспортирует все записи в Excel файл и возвращает путь к файлу"""
        # Получаем все записи
        bookings = self.booking_service.get_all_bookings()
        
        # Преобразуем в DataFrame
        data = []
        for booking in bookings:
            client_name, service_type, booking_date, booking_time, client_phone, created_at = booking
            service_name = self.booking_service.get_service_name(service_type)
            
            data.append({
                'ФИО клиента': client_name,
                'Услуга': service_name,
                'Дата': booking_date,
                'Время': booking_time,
                'Телефон': client_phone,
                'Дата создания': created_at
            })
        
        # Создаем DataFrame
        df = pd.DataFrame(data)
        
        # Форматируем дату для имени файла
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"bookings_export_{current_date}.xlsx"
        filepath = os.path.join(self.export_folder, filename)
        
        # Сохраняем в Excel с форматированием
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Записи', index=False)
            
            # Получаем workbook и worksheet для форматирования
            workbook = writer.book
            worksheet = writer.sheets['Записи']
            
            # Автоматически подгоняем ширину колонок
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Добавляем фильтры к заголовкам
            worksheet.auto_filter.ref = worksheet.dimensions
        
        return filepath
    
    def export_user_bookings_to_excel(self, user_id: int) -> str:
        """Экспортирует записи конкретного пользователя в Excel"""
        bookings = self.booking_service.get_user_bookings(user_id)
        
        # Преобразуем в DataFrame
        data = []
        for booking in bookings:
            service_type, booking_date, booking_time, client_name, client_phone, created_at = booking
            service_name = self.booking_service.get_service_name(service_type)
            
            data.append({
                'Услуга': service_name,
                'Дата': booking_date,
                'Время': booking_time,
                'ФИО клиента': client_name,
                'Телефон': client_phone,
                'Дата создания': created_at
            })
        
        # Создаем DataFrame
        df = pd.DataFrame(data)
        
        # Форматируем дату для имени файла
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"my_bookings_export_{current_date}.xlsx"
        filepath = os.path.join(self.export_folder, filename)
        
        # Сохраняем в Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Мои записи', index=False)
            
            # Форматирование
            workbook = writer.book
            worksheet = writer.sheets['Мои записи']
            
            # Автоподгонка ширины колонок
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            worksheet.auto_filter.ref = worksheet.dimensions
        
        return filepath
    
    def cleanup_old_exports(self, days_old: int = 7):
        """Удаляет старые файлы экспорта"""
        import time
        current_time = time.time()
        
        for filename in os.listdir(self.export_folder):
            filepath = os.path.join(self.export_folder, filename)
            if os.path.isfile(filepath):
                # Проверяем возраст файла
                file_age = current_time - os.path.getctime(filepath)
                if file_age > (days_old * 24 * 60 * 60):  # Конвертируем дни в секунды
                    os.remove(filepath)