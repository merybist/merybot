from botcfg import bot
from dp import conn_bot
import time
import base64
from utils import decrypt_aes

@bot.message_handler(commands=['decode_aes'])
def decode_aes_message(message):
    cur_bot = conn_bot.cursor()
    text_parts = message.text.split(' ', maxsplit=2)

    if len(text_parts) < 3:
        bot.send_message(message.chat.id, "❌ Напиши текст після /decode_aes")
        return
    
    original_text = base64.b64decode(text_parts[1])
    aes_key = base64.b64decode(text_parts[2])
    decoded_text = decrypt_aes(original_text, aes_key)

    timestamp = int(time.time())

    cur_bot.execute("INSERT INTO messages_aes (user_id, message_encoded, message_decoded, pass_aes, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (message.from_user.id, original_text, decoded_text, aes_key, timestamp))
    conn_bot.commit()

    bot.send_message(message.chat.id, f"🔓 Розшифровано:\n`{decoded_text}`", parse_mode="Markdown")