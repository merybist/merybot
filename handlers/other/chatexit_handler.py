from botcfg import bot
from chats import active_chats


@bot.message_handler(commands=['chatexit'])
def chat_mode_exit(message):
    user_id = message.from_user.id

    # Перевірка, чи користувач в активному чаті
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        del active_chats[user_id]
        del active_chats[partner_id]

        bot.send_message(user_id, "🚪 Ви вийшли з чат-режиму.")
        bot.send_message(partner_id, "🚪 Ваш співрозмовник вийшов з чат-режиму.")
    else:
        bot.reply_to(message, "❌ Ви не в чат-режимі.")
