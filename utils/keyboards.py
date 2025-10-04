from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta

class Keyboards:
    def get_main_menu(self, is_admin: bool = False):
        """Главное меню с учетом прав администратора"""
        keyboard = [
            [InlineKeyboardButton("📋 Записаться на услугу", callback_data="start_booking")],
            [InlineKeyboardButton("📋 Посмотреть мои записи", callback_data="view_my_bookings")],
            [InlineKeyboardButton("📊 Экспорт в Excel", callback_data="export_excel")]
        ]
        
        if is_admin:
            keyboard.append([InlineKeyboardButton("👑 Администратор", callback_data="admin_panel")])
        
        keyboard.append([InlineKeyboardButton("🚪 Выход из чата", callback_data="exit_chat")])
            
        return InlineKeyboardMarkup(keyboard)
    
    def get_services(self):
        """Клавиатура выбора услуг"""
        keyboard = [
            [InlineKeyboardButton("📄 Патентование", callback_data="service_patent")],
            [InlineKeyboardButton("🏢 Товарные знаки", callback_data="service_trademark")],
            [InlineKeyboardButton("💬 Консультации", callback_data="service_consultation")],
            [InlineKeyboardButton("🚪 Выход из чата", callback_data="exit_chat")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_dates(self):
        """Клавиатура выбора дат (30 дней вперед)"""
        keyboard = []
        today = datetime.now().date()
        
        for i in range(1, 31):
            date = today + timedelta(days=i)
            if date.weekday() < 5:  # Только рабочие дни
                date_str = date.strftime("%d.%m.%Y")
                keyboard.append([
                    InlineKeyboardButton(date_str, callback_data=f"date_{date_str}")
                ])
        
        keyboard.append([InlineKeyboardButton("🚪 Выход из чата", callback_data="exit_chat")])
        return InlineKeyboardMarkup(keyboard)
    
    def get_times(self, available_times):
        """Клавиатура выбора времени"""
        keyboard = []
        row = []
        
        for i, time in enumerate(available_times):
            row.append(InlineKeyboardButton(time, callback_data=f"time_{time}"))
            if (i + 1) % 2 == 0 or i == len(available_times) - 1:
                keyboard.append(row)
                row = []
        
        keyboard.append([InlineKeyboardButton("◀️ Назад к датам", callback_data="back_to_dates")])
        keyboard.append([InlineKeyboardButton("🚪 Выход из чата", callback_data="exit_chat")])
        return InlineKeyboardMarkup(keyboard)
    
    def get_confirmation(self):
        """Клавиатура подтверждения записи"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_booking"),
                InlineKeyboardButton("❌ Отменить", callback_data="cancel_booking")
            ],
            [InlineKeyboardButton("🚪 Выход из чата", callback_data="exit_chat")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_export_menu(self, is_admin: bool = False):
        """Меню экспорта с учетом прав администратора"""
        keyboard = [
            [InlineKeyboardButton("📊 Мои записи", callback_data="export_my_excel")]
        ]
        
        if is_admin:
            keyboard.append([InlineKeyboardButton("📊 Все записи", callback_data="export_all_excel")])
            
        keyboard.append([InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")])
        keyboard.append([InlineKeyboardButton("🚪 Выход из чата", callback_data="exit_chat")])
        return InlineKeyboardMarkup(keyboard)
    
    def get_admin_menu(self):
        """Админ-панель с полным управлением"""
        keyboard = [
            [InlineKeyboardButton("📊 Экспорт всех записей", callback_data="admin_export_all")],
            [InlineKeyboardButton("👥 Просмотр всех записей", callback_data="admin_view_all")],
            [InlineKeyboardButton("📈 Статистика записей", callback_data="admin_stats")],
            [InlineKeyboardButton("🔍 Поиск по телефону", callback_data="admin_search_phone")],
            [InlineKeyboardButton("🗑️ Очистка старых экспортов", callback_data="admin_cleanup")],
            [InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")],
            [InlineKeyboardButton("🚪 Выход из чата", callback_data="exit_chat")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_admin_back_menu(self):
        """Клавиатура для возврата в админ-панель"""
        keyboard = [
            [InlineKeyboardButton("◀️ В админ-панель", callback_data="admin_panel")],
            [InlineKeyboardButton("🚪 Выход из чата", callback_data="exit_chat")]
        ]
        return InlineKeyboardMarkup(keyboard)