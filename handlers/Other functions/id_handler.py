from botcfg import bot


@bot.message_handler(commands=['id'])
def info(message):
    bot.send_message(message.chat.id, f'Ваш ID: {message.from_user.id}')