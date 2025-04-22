from botcfg import bot, ADMIN_USER_ID
from chats import active_chats
from telebot.types import Message


@bot.message_handler(commands=['chatstop'])
def stop_chat_help(message: Message):
    user_id = message.from_user.id
    
    if user_id not in active_chats:
        bot.reply_to(message, "❌ Ви не в чат-режимі.")
        return
    
    partner_id = active_chats[user_id]
    
    # Видаляємо користувача та партнера з активних чатів
    del active_chats[user_id]
    del active_chats[partner_id]
    
    bot.send_message(user_id, "🚪 Ви вийшли з чат-режиму.")
    bot.send_message(partner_id, "🚪 Ваш співрозмовник вийшов з чат-режиму.")


@bot.message_handler(func=lambda message: message.from_user.id in active_chats)
def chat_with_operator(message: Message):
    user_id = message.from_user.id
    
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        # Перенаправляємо повідомлення адміністратору
        bot.send_message(partner_id, f"📩 @{message.from_user.username}: {message.text}")
        bot.send_message(user_id, "✅ Ваше повідомлення надіслано оператору.")


@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_USER_ID and message.reply_to_message and message.chat.type == "private")
def reply_to_user(message: Message):
    

    if not active_chats:
        bot.send_message(ADMIN_USER_ID, "❌ Немає активних чатів.")
        return
    
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        bot.send_message(ADMIN_USER_ID, "❌ Вкажіть повідомлення для користувача.")
        return
    
    reply_text = parts[1]
    
    # Відправка повідомлення користувачеві
    for user_id in active_chats.keys():
        if user_id != ADMIN_USER_ID:
            bot.send_message(user_id, f"📩 Оператор зворотного зв'язку: {reply_text}")
    
        bot.send_message(ADMIN_USER_ID, "✅ Відповідь надіслана.")
