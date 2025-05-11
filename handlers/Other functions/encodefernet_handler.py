from botcfg import bot
from dp import conn_bot
from cryptography.fernet import Fernet
import time


@bot.message_handler(commands=['encode_fernet'])
def encode_fernet_message(message):
    cur_bot = conn_bot.cursor()
    text_parts = message.text.split(' ', maxsplit=1) 
    
    if len(text_parts) < 2:  
        bot.send_message(message.chat.id, "❌ Напиши текст після /encode_fernet")
        return

    original_text = text_parts[1]
    fernet_key = Fernet.generate_key()

    fernet = Fernet(fernet_key)
    encoded_text = fernet.encrypt(original_text.encode())

    timestamp = int(time.time())

    cur_bot.execute("INSERT INTO messages (user_id, message_encoded, message_decoded, timestamp) VALUES (?, ?, ?, ?)",
                    (message.from_user.id, encoded_text, original_text, timestamp))
    conn_bot.commit()
   
    bot.send_message(message.chat.id, "🔐 Fernet-зашифрований текст:")
    bot.send_message(message.chat.id, encoded_text.decode()) # Тут перевів байти в текст

    bot.send_message(message.chat.id, "🗝 Fernet-ключ (збережи його!):")
    bot.send_message(message.chat.id, fernet_key.decode()) # Тут не потрібно переводити в base64, бо ключ вже віддається в форматі base64 в рядку 130.
