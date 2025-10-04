from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler
from utils.keyboards import Keyboards

keyboards = Keyboards()

async def cancel(update: Update, context: CallbackContext) -> int:
    if hasattr(update, 'callback_query'):
        query = update.callback_query
        await query.answer("Действие отменено")
        await query.edit_message_text("❌ Действие отменено.")
    else:
        await update.message.reply_text("❌ Действие отменено.", reply_markup=ReplyKeyboardRemove())
    
    context.user_data.clear()
    return ConversationHandler.END

async def error_handler(update: Update, context: CallbackContext):
    if update and update.message:
        await update.message.reply_text("❌ Произошла ошибка. Пожалуйста, начните заново с /start")