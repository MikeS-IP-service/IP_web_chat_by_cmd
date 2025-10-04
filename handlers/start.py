# handlers/start.py
from telegram import Update
from telegram.ext import CallbackContext
from utils.keyboards import Keyboards
from config.settings import BOT_CONFIG

keyboards = Keyboards()

async def start(update: Update, context: CallbackContext):
    """Команда /start - главное меню (ВСЕГДА сбрасывает состояние)"""
    # ВАЖНО: Полностью очищаем все данные и состояния
    context.user_data.clear()
    
    user = update.message.from_user
    is_admin = user.id in BOT_CONFIG.ADMIN_IDS
    
    welcome_text = """
🏢 Добро пожаловать в IP Services!

Мы оказываем следующие услуги:
• 📄 Патентование
• 🏢 Товарные знаки  
• 💬 Консультации по вопросам интеллектуальной собственности

Доступные команды:
/reset - сбросить состояние (если бот завис)

Выберите действие:
"""
    
    await update.message.reply_text(
        welcome_text, 
        reply_markup=keyboards.get_main_menu(is_admin=is_admin)
    )

async def handle_start_buttons(update: Update, context: CallbackContext):
    """Обработчик кнопок главного меню"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    is_admin = user.id in BOT_CONFIG.ADMIN_IDS
    
    if query.data == "start_booking":
        await query.edit_message_text(
            "📋 Выберите услугу:",
            reply_markup=keyboards.get_services()
        )
    
    elif query.data == "view_my_bookings":
        from handlers.booking import view_my_bookings
        await view_my_bookings(update, context)
    
    elif query.data == "export_excel":
        await query.edit_message_text(
            "📊 Выберите тип экспорта:",
            reply_markup=keyboards.get_export_menu(is_admin=is_admin)
        )
    
    elif query.data == "admin_panel" and is_admin:
        from handlers.admin import show_admin_panel
        await show_admin_panel(update, context)
    
    elif query.data == "main_menu":
        await main_menu(update, context)
    
    elif query.data == "exit_chat":
        await exit_chat(update, context)

async def main_menu(update: Update, context: CallbackContext):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    is_admin = user.id in BOT_CONFIG.ADMIN_IDS
    
    welcome_text = """
🏢 Добро пожаловать в IP Services!

Мы оказываем следующие услуги:
• 📄 Патентование
• 🏢 Товарные знаки  
• 💬 Консультации по вопросам интеллектуальной собственности

Доступные команды:
/reset - сбросить состояние (если бот завис)

Выберите действие:
"""
    
    await query.edit_message_text(
        welcome_text, 
        reply_markup=keyboards.get_main_menu(is_admin=is_admin)
    )

async def exit_chat(update: Update, context: CallbackContext):
    """Полный выход из чата"""
    query = update.callback_query
    if query:
        await query.answer("До свидания! 👋")
        await query.edit_message_text(
            "🚪 Вы вышли из чата. Чтобы начать заново, нажмите /start"
        )
    else:
        await update.message.reply_text(
            "🚪 Вы вышли из чата. Чтобы начать заново, нажмите /start"
        )
    
    context.user_data.clear()

async def get_my_id(update: Update, context: CallbackContext):
    """Показать ID пользователя"""
    user = update.message.from_user
    await update.message.reply_text(f"🆔 Ваш ID: {user.id}")

async def force_reset(update: Update, context: CallbackContext):
    """Принудительный сброс состояния (на случай зависания)"""
    context.user_data.clear()
    await update.message.reply_text(
        "🔄 Состояние сброшено! Нажмите /start для начала.",
        reply_markup=keyboards.get_main_menu(is_admin=update.message.from_user.id in BOT_CONFIG.ADMIN_IDS)
    )