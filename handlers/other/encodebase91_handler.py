from botcfg import bot
from dp import conn_bot
import base91
import time

@bot.message_handler(commands=['encode_base91'])
def encode_base91_message(message):
    cur_bot = conn_bot.cursor()
    text_parts = message.text.split(' ', maxsplit=1)

    if len(text_parts) < 2:
        bot.send_message(message.chat.id, "❌ Напиши текст після /encode_base91")
        return
    
    original_text = text_parts[1]
    encoded_text = base91.encode(original_text.encode())
    
    timestamp = int(time.time())
    cur_bot.execute("INSERT INTO messages (user_id, message_encoded, message_decoded, timestamp) VALUES (?, ?, ?, ?)",  
                    (message.from_user.id, encoded_text, original_text, timestamp))
    conn_bot.commit()
    bot.send_message(message.chat.id, f"🔐 Base91-зашифрований текст:\n`{encoded_text}`", parse_mode="Markdown")
