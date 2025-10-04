from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from utils.keyboards import Keyboards
from services.booking_service import BookingService
from services.excel_service import ExcelExportService
from config.settings import BOT_CONFIG
import os

keyboards = Keyboards()
booking_service = BookingService()
excel_service = ExcelExportService()

# Состояния для админских диалогов
ADMIN_SEARCH_PHONE = 0

async def show_admin_panel(update: Update, context: CallbackContext):
    """Показать админ-панель"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    
    # Проверка прав администратора
    if user.id not in BOT_CONFIG.ADMIN_IDS:
        await query.edit_message_text(
            "❌ У вас нет прав доступа к админ-панели.",
            reply_markup=keyboards.get_main_menu()
        )
        return
    
    # Получаем статистику
    all_bookings = booking_service.get_all_bookings()
    total_bookings = len(all_bookings)
    
    admin_text = f"""
👑 АДМИНИСТРАТОР

📊 Статистика системы:
• Всего записей: {total_bookings}
• Услуг оказано: {total_bookings}
• Активных записей: {total_bookings}

Доступные действия:
• 📊 Экспорт всех записей в Excel
• 👥 Просмотр всех записей в чате  
• 📈 Подробная статистика записей
• 🔍 Поиск записей по номеру телефона
• 🗑️ Очистка старых файлов экспорта
"""
    
    await query.edit_message_text(
        admin_text,
        reply_markup=keyboards.get_admin_menu()
    )

async def handle_admin_buttons(update: Update, context: CallbackContext):
    """Обработчик кнопок админ-панели"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    
    # Проверка прав администратора
    if user.id not in BOT_CONFIG.ADMIN_IDS:
        await query.edit_message_text(
            "❌ У вас нет прав для выполнения этой операции.",
            reply_markup=keyboards.get_main_menu()
        )
        return
    
    if query.data == "admin_export_all":
        await admin_export_all_bookings(update, context)
    
    elif query.data == "admin_view_all":
        await admin_view_all_bookings(update, context)
    
    elif query.data == "admin_stats":
        await admin_show_stats(update, context)
    
    elif query.data == "admin_search_phone":
        await admin_start_search_phone(update, context)
    
    elif query.data == "admin_cleanup":
        await admin_cleanup_exports(update, context)
    
    elif query.data == "admin_panel":
        await show_admin_panel(update, context)
    
    elif query.data == "main_menu":
        from handlers.start import main_menu
        await main_menu(update, context)

async def admin_export_all_bookings(update: Update, context: CallbackContext):
    """Экспорт всех записей для админа"""
    query = update.callback_query
    
    try:
        await query.edit_message_text("🔄 Создаю файл Excel со всеми записями...")
        
        filepath = excel_service.export_bookings_to_excel()
        
        with open(filepath, 'rb') as file:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=file,
                filename=os.path.basename(filepath),
                caption="✅ Все записи экспортированы в Excel"
            )
        
        await query.message.reply_text(
            "📊 Экспорт завершен!",
            reply_markup=keyboards.get_admin_back_menu()
        )
        
    except Exception as e:
        await query.edit_message_text(
            f"❌ Ошибка при экспорте: {str(e)}",
            reply_markup=keyboards.get_admin_back_menu()
        )

async def admin_view_all_bookings(update: Update, context: CallbackContext):
    """Просмотр всех записей в чате"""
    query = update.callback_query
    
    try:
        all_bookings = booking_service.get_all_bookings()
        
        if not all_bookings:
            await query.edit_message_text(
                "📭 В системе пока нет записей.",
                reply_markup=keyboards.get_admin_back_menu()
            )
            return
        
        response = "👥 ВСЕ ЗАПИСИ В СИСТЕМЕ:\n\n"
        
        for i, booking in enumerate(all_bookings, 1):
            client_name, service_type, booking_date, booking_time, client_phone, created_at = booking
            service_name = booking_service.get_service_name(service_type)
            
            response += f"""
📋 Запись #{i}
Услуга: {service_name}
Дата: {booking_date}
Время: {booking_time}
Клиент: {client_name}
Телефон: {client_phone}
Создана: {created_at}
────────────────────
"""
            
            # Разбиваем на сообщения если слишком длинное
            if len(response) > 3000:
                await query.edit_message_text(response)
                response = ""
        
        response += f"\n📊 Всего записей: {len(all_bookings)}"
        
        await query.edit_message_text(
            response,
            reply_markup=keyboards.get_admin_back_menu()
        )
        
    except Exception as e:
        await query.edit_message_text(
            f"❌ Ошибка при получении записей: {str(e)}",
            reply_markup=keyboards.get_admin_back_menu()
        )

async def admin_show_stats(update: Update, context: CallbackContext):
    """Подробная статистика записей"""
    query = update.callback_query
    
    try:
        all_bookings = booking_service.get_all_bookings()
        
        # Собираем статистику
        services_count = {}
        dates_count = {}
        
        for booking in all_bookings:
            client_name, service_type, booking_date, booking_time, client_phone, created_at = booking
            
            # Статистика по услугам
            services_count[service_type] = services_count.get(service_type, 0) + 1
            
            # Статистика по датам
            dates_count[booking_date] = dates_count.get(booking_date, 0) + 1
        
        # Формируем отчет
        stats_text = "📈 ПОДРОБНАЯ СТАТИСТИКА\n\n"
        stats_text += f"📊 Всего записей: {len(all_bookings)}\n\n"
        
        stats_text += "📋 По услугам:\n"
        for service, count in services_count.items():
            service_name = booking_service.get_service_name(service)
            stats_text += f"• {service_name}: {count} записей\n"
        
        stats_text += "\n📅 По датам:\n"
        for date, count in list(dates_count.items())[:10]:  # Показываем первые 10 дат
            stats_text += f"• {date}: {count} записей\n"
        
        if len(dates_count) > 10:
            stats_text += f"• ... и еще {len(dates_count) - 10} дат\n"
        
        await query.edit_message_text(
            stats_text,
            reply_markup=keyboards.get_admin_back_menu()
        )
        
    except Exception as e:
        await query.edit_message_text(
            f"❌ Ошибка при получении статистики: {str(e)}",
            reply_markup=keyboards.get_admin_back_menu()
        )

async def admin_start_search_phone(update: Update, context: CallbackContext):
    """Начало поиска по номеру телефона"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🔍 Введите номер телефона для поиска (можно часть номера):",
        reply_markup=keyboards.get_admin_back_menu()
    )
    
    return ADMIN_SEARCH_PHONE

async def admin_search_phone(update: Update, context: CallbackContext):
    """Поиск записей по номеру телефона"""
    phone_query = update.message.text.strip()
    
    try:
        all_bookings = booking_service.get_all_bookings()
        found_bookings = []
        
        for booking in all_bookings:
            client_name, service_type, booking_date, booking_time, client_phone, created_at = booking
            if phone_query in client_phone:
                found_bookings.append(booking)
        
        if not found_bookings:
            await update.message.reply_text(
                f"❌ Записей с номером содержащим '{phone_query}' не найдено.",
                reply_markup=keyboards.get_admin_back_menu()
            )
            return ConversationHandler.END
        
        response = f"🔍 РЕЗУЛЬТАТЫ ПОИСКА по '{phone_query}':\n\n"
        
        for i, booking in enumerate(found_bookings, 1):
            client_name, service_type, booking_date, booking_time, client_phone, created_at = booking
            service_name = booking_service.get_service_name(service_type)
            
            response += f"""
📋 Запись #{i}
Услуга: {service_name}
Дата: {booking_date}
Время: {booking_time}
Клиент: {client_name}
Телефон: {client_phone}
Создана: {created_at}
────────────────────
"""
        
        response += f"\n📊 Найдено записей: {len(found_bookings)}"
        
        await update.message.reply_text(
            response,
            reply_markup=keyboards.get_admin_back_menu()
        )
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка при поиске: {str(e)}",
            reply_markup=keyboards.get_admin_back_menu()
        )
    
    return ConversationHandler.END

async def admin_cleanup_exports(update: Update, context: CallbackContext):
    """Очистка старых файлов экспорта"""
    query = update.callback_query
    
    try:
        excel_service.cleanup_old_exports(days_old=1)  # Очищаем файлы старше 1 дня
        
        await query.edit_message_text(
            "🗑️ Старые файлы экспорта успешно удалены!",
            reply_markup=keyboards.get_admin_back_menu()
        )
        
    except Exception as e:
        await query.edit_message_text(
            f"❌ Ошибка при очистке: {str(e)}",
            reply_markup=keyboards.get_admin_back_menu()
        )

# ConversationHandler для поиска по телефону
admin_search_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(admin_start_search_phone, pattern="^admin_search_phone$")],
    states={
        ADMIN_SEARCH_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_search_phone)]
    },
    fallbacks=[
        CallbackQueryHandler(show_admin_panel, pattern="^admin_panel$")
    ],
    map_to_parent={
        ConversationHandler.END: ConversationHandler.END
    }
)