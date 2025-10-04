# main.py
import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from config.settings import BOT_CONFIG
from database.connection import DatabaseConnection
from handlers.start import start, handle_start_buttons, get_my_id, exit_chat, force_reset
from handlers.booking import select_service, select_date, select_time, get_client_name, get_client_phone, confirm_booking, cancel_booking, view_my_bookings
from handlers.admin import handle_admin_buttons, show_admin_panel, admin_search_conv_handler
from handlers.export import handle_export_buttons
from handlers.common import cancel, error_handler

SELECT_SERVICE, SELECT_DATE, SELECT_TIME, CLIENT_NAME, CLIENT_PHONE, CONFIRMATION = range(6)

def main():
    # Инициализация базы данных
    db = DatabaseConnection()
    db.init_database()
    
    # Создание приложения
    application = Application.builder().token(BOT_CONFIG.TOKEN).build()
    
    # ConversationHandler для бронирования (БЕЗ per_message=True)
    booking_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_service, pattern="^service_")],
        states={
            SELECT_SERVICE: [CallbackQueryHandler(select_service, pattern="^service_")],
            SELECT_DATE: [CallbackQueryHandler(select_date, pattern="^date_")],
            SELECT_TIME: [CallbackQueryHandler(select_time, pattern="^time_")],
            CLIENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_client_name)],
            CLIENT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_client_phone)],
            CONFIRMATION: [
                CallbackQueryHandler(confirm_booking, pattern="^confirm_booking$"),
                CallbackQueryHandler(cancel_booking, pattern="^cancel_booking$")
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(cancel, pattern="^cancel$"),
            CallbackQueryHandler(exit_chat, pattern="^exit_chat$"),
            CommandHandler("reset", force_reset)
        ]
        # per_message=True УБРАНО!
    )

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("myid", get_my_id))
    application.add_handler(CommandHandler("reset", force_reset))
    
    # Обработчики кнопок главного меню
    application.add_handler(CallbackQueryHandler(handle_start_buttons, pattern="^start_booking$"))
    application.add_handler(CallbackQueryHandler(handle_start_buttons, pattern="^view_my_bookings$"))
    application.add_handler(CallbackQueryHandler(handle_start_buttons, pattern="^export_excel$"))
    application.add_handler(CallbackQueryHandler(handle_start_buttons, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(handle_start_buttons, pattern="^exit_chat$"))
    application.add_handler(CallbackQueryHandler(handle_start_buttons, pattern="^admin_panel$"))
    
    # Обработчики админ-панели
    application.add_handler(CallbackQueryHandler(handle_admin_buttons, pattern="^admin_export_all$"))
    application.add_handler(CallbackQueryHandler(handle_admin_buttons, pattern="^admin_view_all$"))
    application.add_handler(CallbackQueryHandler(handle_admin_buttons, pattern="^admin_stats$"))
    application.add_handler(CallbackQueryHandler(handle_admin_buttons, pattern="^admin_cleanup$"))
    application.add_handler(CallbackQueryHandler(show_admin_panel, pattern="^admin_panel$"))
    
    # Обработчики экспорта
    application.add_handler(CallbackQueryHandler(handle_export_buttons, pattern="^export_my_excel$"))
    application.add_handler(CallbackQueryHandler(handle_export_buttons, pattern="^export_all_excel$"))
    
    # Обработчик просмотра записей
    application.add_handler(CallbackQueryHandler(view_my_bookings, pattern="^view_my_bookings$"))
    
    # ConversationHandler добавляем ПОСЛЕДНИМ
    application.add_handler(booking_conv_handler)

    application.add_handler(admin_search_conv_handler)
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    print("🤖 Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()