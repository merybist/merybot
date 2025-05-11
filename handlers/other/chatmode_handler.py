from botcfg import bot
from dp import cur_bot, conn_bot
from chats import active_chats


@bot.message_handler(commands=['chatmode'])
def start_chat_mode(message):
    user_id = message.from_user.id

    try:
        partner_id = int(message.text.split(' ')[1])
    except (IndexError, ValueError):  # Обробляємо помилку, якщо аргумент відсутній або некоректний
        bot.reply_to(message, "❌ Неправильний формат команди. Використовуйте /chatmode <ID_співрозмовника>.")
        return  # Зупиняємо виконання функції


    # Перевірка, чи існує user_id у базі даних
    cur_bot.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if not cur_bot.fetchone():
        bot.reply_to(message, "❌ Ви не зареєстровані в системі. Використовуйте /start для реєстрації.")
        return

    # Перевірка, чи user_id і partner_id не однакові
    if user_id == partner_id:
        bot.reply_to(message, "❌ Ви не можете почати чат із самим собою.")
        return

    # Перевірка, чи існує partner_id у базі даних
    cur_bot.execute("SELECT * FROM users WHERE user_id = ?", (partner_id,))
    if not cur_bot.fetchone():
        bot.reply_to(message, f"❌ Користувача з ID {partner_id} не знайдено.")
        return

    if user_id in active_chats:
        bot.reply_to(message, "❌ Ви вже в чат-режимі!")
        return

    if partner_id in active_chats:
        bot.reply_to(message, "❌ Ваш співрозмовник вже в чат-режимі!")
        return

    active_chats[user_id] = partner_id
    active_chats[partner_id] = user_id

    bot.send_message(user_id, f"✅ Чат-режим з користувачем {partner_id} активований!")
    bot.send_message(partner_id, f"✅ {user_id} активував чат-режим з вами!")