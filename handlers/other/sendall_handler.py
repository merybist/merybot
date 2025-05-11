from botcfg import bot
from dp import cur_bot, conn_bot


@bot.message_handler(commands=['sendall'])
def sendall(message):
    text_parts = message.text.split(' ', maxsplit=2)
    if len(text_parts) <3:
        bot.send_message(message.chat.id, "Використовуй команду правильно, КПТ!")
        return

    password = text_parts[1]
    text_to_send = text_parts[2]

    # Перевірка, чи це виключений користувач
    if message.from_user.id == 673146683:
        # Якщо це той самий користувач, то пароль не потрібен
        pass
    else:
        # Якщо це не той самий користувач, перевіряємо пароль
        admin_password = ("MeryBist_PassWord")
        if not admin_password:
            bot.send_message(message.chat.id, "Не знайдено пароль в змінних середовища!")
            return

        print(f"Пароль з .env: {admin_password}")  # Перевірка значення пароля

        if password != admin_password:
            bot.send_message(message.chat.id, "Неправильний пароль авторизації :/.")
            return

    cur_bot.execute('SELECT chat_id FROM users')
    users = cur_bot.fetchall()

    if not users:
        bot.send_message(message.chat.id, "Немає користувачів для розсилки.")
        return

    for user in users:
        chat_id = user[0]
        bot.send_message(chat_id, text_to_send)