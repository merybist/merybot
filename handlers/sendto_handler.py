from botcfg import bot
from dp import cur_bot, conn_bot
from chats import active_chats
from utils import datetime


@bot.message_handler(commands=['sendto'])
def sendto(message):
        text_parts = message.text.split (' ', maxsplit=3)
        if len(text_parts) <4:
            bot.send_message(message.chat.id, "Використовуй команду правильно, АПТ!")
            return
        
        telegram_id = text_parts[1]
        password = text_parts[2]
        text_to_send = text_parts[3]

           # Перевірка, чи це виключений користувач
        if message.from_user.id == 673146683:
            # Якщо це той самий користувач, то пароль не потрібен
           pass
        else:
            # Якщо це не той самий користувач, перевіряємо пароль
            admin_password = ("MeryBist_PassWord")
            print(f"Пароль з .env: {admin_password}")  # Перевірка значення пароля
            if password != admin_password:
                bot.send_message(message.chat.id, "Неправильний пароль авторизації :/.")
                return

        cur_bot.execute('SELECT chat_id FROM users WHERE user_id =?', (telegram_id,))
        result = cur_bot.fetchone()

        if result:
            chat_id = result[0]
            bot.send_message(chat_id, text_to_send)
            bot.send_message(message.chat.id, "Повідомлення успішно надіслано!")
        else:
            bot.send_message(message.chat.id, "Користувача з таким ID не знайдено.")

@bot.message_handler(func=lambda message: message.from_user.id in active_chats and not message.text.startswith('/'))
def chat_mode_handler(message):
    sender_id = message.from_user.id
    receiver_id = active_chats[sender_id]
    timestamp = int(datetime.now().timestamp())

    print(f"Sender ID: {sender_id}, Receiver ID: {receiver_id}, Message: {message.text}")

    if message.text:
        msg_type = "text"
        content = message.text
        bot.send_message(receiver_id, f"📩 Нове повідомлення від {sender_id}:\n{content}")

    elif message.photo:
         msg_type = "photo"
         file_id = message.photo[-1].file_id  # Вибір останнього розміру фото
         file_info = bot.get_file(file_id)  # Отримуємо інформацію про файл
         downloaded_file = bot.download_file(file_info.file_path)  # Завантажуємо файл

         # Зберігаємо файл локально
         photo_path = f"photo_{sender_id}_{timestamp}.jpg"
         with open(photo_path, 'wb') as photo_file:
             photo_file.write(downloaded_file)

         # Відправляємо фото
         with open(photo_path, 'rb') as photo_file:
             bot.send_photo(receiver_id, photo_file, caption=f"📷 Фото від {sender_id}")
         content = file_id

    elif message.document:
         msg_type = "document"
         file_id = message.document.file_id
         file_info = bot.get_file(file_id)  # Отримуємо інформацію про файл
         downloaded_file = bot.download_file(file_info.file_path)  # Завантажуємо файл

         # Зберігаємо файл локально
         document_path = f"document_{sender_id}_{timestamp}.pdf"
         with open(document_path, 'wb') as doc_file:
             doc_file.write(downloaded_file)

         # Відправляємо документ
         with open(document_path, 'rb') as doc_file:
             bot.send_document(receiver_id, doc_file, caption=f"📎 Документ від {sender_id}")
         content = file_id

    elif message.voice:
         msg_type = "voice"
         file_id = message.voice.file_id
         file_info = bot.get_file(file_id)  # Отримуємо інформацію про файл
         downloaded_file = bot.download_file(file_info.file_path)  # Завантажуємо файл

         # Зберігаємо файл локально
         voice_path = f"voice_{sender_id}_{timestamp}.ogg"
         with open(voice_path, 'wb') as voice_file:
             voice_file.write(downloaded_file)

         # Відправляємо голосове повідомлення
         with open(voice_path, 'rb') as voice_file:
             bot.send_voice(receiver_id, voice_file, caption=f"🎤 Голосове повідомлення від {sender_id}")
         content = file_id

    else:
         return  # Якщо формат повідомлення не підтримується, просто виходимо

    # Логування в БД
    cur_bot.execute(
        "INSERT INTO chat_logs (sender_id, receiver_id, msg_type, content, timestamp) VALUES (?, ?, ?, ?, ?)",
        (sender_id, receiver_id, msg_type, content, timestamp)
    )
    conn_bot.commit()
