import os
from telegram import Update
from telegram.ext import CallbackContext
from services.excel_service import ExcelExportService
from config.settings import BOT_CONFIG
from utils.keyboards import Keyboards

excel_service = ExcelExportService()
keyboards = Keyboards()

async def handle_export_buttons(update: Update, context: CallbackContext):
    """Обработчик кнопок экспорта"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    is_admin = user.id in BOT_CONFIG.ADMIN_IDS
    
    if query.data == "export_my_excel":
        await export_my_bookings(update, context)
    elif query.data == "export_all_excel":
        await export_all_bookings(update, context)
    elif query.data == "main_menu":
        from handlers.start import main_menu
        await main_menu(update, context)
    elif query.data == "exit_chat":
        from handlers.start import exit_chat
        await exit_chat(update, context)

async def export_my_bookings(update: Update, context: CallbackContext):
    """Экспорт записей текущего пользователя"""
    query = update.callback_query
    user = query.from_user
    is_admin = user.id in BOT_CONFIG.ADMIN_IDS
    
    try:
        await query.edit_message_text("🔄 Создаю файл Excel с вашими записями...")
        
        filepath = excel_service.export_user_bookings_to_excel(user.id)
        
        with open(filepath, 'rb') as file:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=file,
                filename=os.path.basename(filepath),
                caption="✅ Ваши записи экспортированы в Excel"
            )
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Выберите действие:",
            reply_markup=keyboards.get_main_menu(is_admin=is_admin)
        )
        
    except Exception as e:
        await query.edit_message_text(
            "❌ Произошла ошибка при экспорте записей. Попробуйте позже.",
            reply_markup=keyboards.get_main_menu(is_admin=is_admin)
        )

async def export_all_bookings(update: Update, context: CallbackContext):
    """Экспорт всех записей (только для администраторов)"""
    query = update.callback_query
    user = query.from_user
    
    # Проверяем права администратора
    if user.id not in BOT_CONFIG.ADMIN_IDS:
        await query.edit_message_text(
            "❌ У вас нет прав для экспорта всех записей.",
            reply_markup=keyboards.get_main_menu()
        )
        return
    
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
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Выберите действие:",
            reply_markup=keyboards.get_main_menu(is_admin=True)
        )
        
    except Exception as e:
        await query.edit_message_text(
            "❌ Произошла ошибка при экспорте записей. Попробуйте позже.",
            reply_markup=keyboards.get_main_menu(is_admin=True)
        )