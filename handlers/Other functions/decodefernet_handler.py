from botcfg import bot
from dp import conn_bot
from cryptography.fernet import Fernet
import time
import base64

@bot.message_handler(commands=['decode_fernet'])
def decode_fernet_message(message):
    cur_bot = conn_bot.cursor()
    text_parts = message.text.split(' ', maxsplit=2)

    if len(text_parts) < 3:
        bot.send_message(message.chat.id, "❌ Напиши текст після /decode_fernet")
        return
    
    try:
        fernet_key = text_parts[2].encode() # Не потрібно декодувати з base64. Усі функції Fernet потребують на вхід base64-encoded bytes або str
        if len(base64.urlsafe_b64decode(text_parts[2])) != 32: # Тут я декодую з base64, аби перевірити кількість байтів. Хоча ця кількість завжди однакова - 44 символи base64 кодують 32 байта, бо в base64 3 байти кодуються в 4 символи
            bot.send_message(message.chat.id, "❌ Ключ повинен бути 32 байти після декодування Base64.")
            return

        original_text = text_parts[1] # Також не потрібно декодувати
        fernet = Fernet(fernet_key)
        decoded_text = fernet.decrypt(original_text).decode()

        # Зберігаємо результат у базу даних
        timestamp = int(time.time())
        cur_bot.execute("INSERT INTO messages (user_id, message_encoded, message_decoded, timestamp) VALUES (?, ?, ?, ?)",
                        (message.from_user.id, original_text, decoded_text, timestamp))
        conn_bot.commit()

        # Відправляємо результат
        bot.send_message(message.chat.id, f"🔓 Розшифровано:\n`{decoded_text}`", parse_mode="Markdown")

    except ValueError as e:
        bot.send_message(message.chat.id, f"❌ Помилка: {e}")
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, f"❌ Сталася помилка: {e}")