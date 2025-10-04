# handlers/booking.py
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, filters
from services.booking_service import BookingService
from utils.keyboards import Keyboards
from handlers.common import cancel
from config.settings import BOT_CONFIG

SELECT_SERVICE, SELECT_DATE, SELECT_TIME, CLIENT_NAME, CLIENT_PHONE, CONFIRMATION = range(6)

booking_service = BookingService()
keyboards = Keyboards()

async def select_service(update: Update, context: CallbackContext) -> int:
    """Выбор услуги"""
    query = update.callback_query
    await query.answer()
    
    print(f"DEBUG: select_service called with data: {query.data}")
    
    if query.data == "cancel":
        return await cancel(update, context)
    
    service_data = query.data.replace("service_", "")
    print(f"DEBUG: service_data: {service_data}")
    
    if service_data not in booking_service.services:
        await query.edit_message_text("❌ Ошибка выбора услуги")
        return SELECT_SERVICE
    
    service_name = booking_service.get_service_name(service_data)
    context.user_data['service'] = service_data
    context.user_data['service_name'] = service_name
    
    print(f"DEBUG: Moving to SELECT_DATE state")
    
    await query.edit_message_text(
        f"📅 Вы выбрали: {service_name}\n\nТеперь выберите дату:",
        reply_markup=keyboards.get_dates()
    )
    return SELECT_DATE

async def select_date(update: Update, context: CallbackContext) -> int:
    """Выбор даты"""
    query = update.callback_query
    await query.answer()
    
    print(f"DEBUG: select_date called with data: {query.data}")
    
    if query.data == "cancel":
        return await cancel(update, context)
    
    selected_date = query.data.replace("date_", "")
    context.user_data['date'] = selected_date
    
    print(f"DEBUG: Getting available times for {selected_date}")
    available_times = booking_service.get_available_times(selected_date)
    print(f"DEBUG: Available times: {available_times}")
    
    if not available_times:
        await back_to_dates(update, context)
        return SELECT_DATE
    
    await query.edit_message_text(
        f"🕐 Выберите время для {selected_date}:",
        reply_markup=keyboards.get_times(available_times)
    )
    return SELECT_TIME

async def back_to_dates(update: Update, context: CallbackContext) -> int:
    """Возврат к выбору дат"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "❌ На выбранную дату все время занято. Пожалуйста, выберите другую дату:",
        reply_markup=keyboards.get_dates()
    )
    return SELECT_DATE

async def select_time(update: Update, context: CallbackContext) -> int:
    """Выбор времени"""
    query = update.callback_query
    await query.answer()
    
    print(f"DEBUG: select_time called with data: {query.data}")
    
    if query.data == "cancel":
        return await cancel(update, context)
    
    if query.data == "back_to_dates":
        await back_to_dates(update, context)
        return SELECT_DATE
    
    selected_time = query.data.replace("time_", "")
    context.user_data['time'] = selected_time
    
    print(f"DEBUG: Moving to CLIENT_NAME state")
    
    await query.edit_message_text("👤 Пожалуйста, введите ваше ФИО:")
    return CLIENT_NAME

async def get_client_name(update: Update, context: CallbackContext) -> int:
    """Ввод ФИО клиента"""
    client_name = update.message.text
    print(f"DEBUG: get_client_name called with: {client_name}")
    
    if len(client_name) < 2:
        await update.message.reply_text("❌ Пожалуйста, введите корректное ФИО")
        return CLIENT_NAME
    
    context.user_data['client_name'] = client_name
    
    print(f"DEBUG: Moving to CLIENT_PHONE state")
    
    await update.message.reply_text("📞 Пожалуйста, введите ваш номер телефона:")
    return CLIENT_PHONE

async def get_client_phone(update: Update, context: CallbackContext) -> int:
    """Ввод телефона клиента"""
    client_phone = update.message.text
    print(f"DEBUG: get_client_phone called with: {client_phone}")
    
    if len(client_phone) < 5:
        await update.message.reply_text("❌ Пожалуйста, введите корректный номер телефона")
        return CLIENT_PHONE
    
    context.user_data['client_phone'] = client_phone
    
    service_name = context.user_data['service_name']
    date = context.user_data['date']
    time = context.user_data['time']
    name = context.user_data['client_name']
    phone = context.user_data['client_phone']
    
    confirmation_text = f"""
✅ Пожалуйста, подтвердите запись:

📋 Услуга: {service_name}
📅 Дата: {date}
🕐 Время: {time}
👤 Клиент: {name}
📞 Телефон: {phone}

Всё верно?
"""
    
    print(f"DEBUG: Moving to CONFIRMATION state")
    
    await update.message.reply_text(confirmation_text, reply_markup=keyboards.get_confirmation())
    return CONFIRMATION

async def confirm_booking(update: Update, context: CallbackContext) -> int:
    """Подтверждение записи"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    
    try:
        user_data = {
            'user_id': user.id,
            'username': user.first_name,
            'service': context.user_data['service'],
            'date': context.user_data['date'],
            'time': context.user_data['time'],
            'client_name': context.user_data['client_name'],
            'client_phone': context.user_data['client_phone']
        }
        
        booking_id = booking_service.save_booking(user_data)
        
        final_text = f"""
🎉 Запись успешно создана!

📋 Услуга: {context.user_data['service_name']}
📅 Дата: {context.user_data['date']}
🕐 Время: {context.user_data['time']}
👤 Клиент: {context.user_data['client_name']}
📞 Телефон: {context.user_data['client_phone']}

⏰ Пожалуйста, приходите вовремя.
📞 Мы свяжемся с вами для подтверждения.
"""
        
        await query.edit_message_text(final_text)
        
    except Exception as e:
        await query.edit_message_text("❌ Произошла ошибка при сохранении записи.")
    
    context.user_data.clear()
    
    from handlers.start import main_menu
    await main_menu(update, context)
    return ConversationHandler.END

async def cancel_booking(update: Update, context: CallbackContext) -> int:
    """Отмена записи"""
    query = update.callback_query
    await query.answer("Запись отменена")
    
    await query.edit_message_text("❌ Запись отменена.")
    context.user_data.clear()
    
    from handlers.start import main_menu
    await main_menu(update, context)
    return ConversationHandler.END

async def view_my_bookings(update: Update, context: CallbackContext):
    """Просмотр записей пользователя"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    bookings = booking_service.get_user_bookings(user.id)
    
    if not bookings:
        from handlers.start import main_menu
        await query.edit_message_text(
            "📭 У вас пока нет записей.\n\nХотите записаться?",
            reply_markup=keyboards.get_main_menu(is_admin=user.id in BOT_CONFIG.ADMIN_IDS)
        )
        return
    
    response = "📋 Ваши записи:\n\n"
    
    for booking in bookings:
        service_type, booking_date, booking_time, client_name, client_phone, created_at = booking
        service_name = booking_service.get_service_name(service_type)
        
        response += f"""
📋 Услуга: {service_name}
📅 Дата: {booking_date}
🕐 Время: {booking_time}
👤 Клиент: {client_name}
📞 Телефон: {client_phone}
⏰ Создано: {created_at}
────────────────────
"""
    
    from handlers.start import main_menu
    await query.edit_message_text(
        response, 
        reply_markup=keyboards.get_main_menu(is_admin=user.id in BOT_CONFIG.ADMIN_IDS)
    )