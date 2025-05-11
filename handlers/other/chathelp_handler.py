from botcfg import bot, ADMIN_USER_ID
from telebot.types import Message
from chats import active_chats


@bot.message_handler(commands=['chathelp'])
def start_chat_help(message: Message):
    user_id = message.from_user.id
    
    if user_id in active_chats:
        bot.reply_to(message, "❌ Ви вже в чат-режимі!")
        return
    
    # Перевіряємо, чи є адміністратор в активних чатах
    if ADMIN_USER_ID in active_chats:
        bot.send_message(user_id, "❌ Адміністратор зараз недоступний для чату. Спробуйте пізніше.")
        return
    
    # Якщо адміністратор доступний, додаємо користувача в чат
    active_chats[user_id] = ADMIN_USER_ID  # Створюємо чат з адміністратором
    active_chats[ADMIN_USER_ID] = user_id  # Додаємо адміністратора в активні чати

    bot.send_message(user_id, "🆘 Ви підключені до оператора. Напишіть ваше питання.")
    bot.send_message(ADMIN_USER_ID, f"🆘 Новий запит від користувача @{user_id}. Відповідайте тут.")