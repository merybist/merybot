from botcfg import bot
from dp import conn_bot, cur_bot
import base64
import time


@bot.message_handler(commands=['encode_base64'])
def encode_message(message):  
    text_parts = message.text.split(' ', maxsplit=1) 
    
    if len(text_parts) < 2:  
        bot.send_message(message.chat.id, "❌ Напиши текст після /encode_base64!")
        return
        
    original_text = text_parts[1]  
    encoded_text = base64.b64encode(original_text.encode()).decode()

    timestamp = int(time.time()) 

    cur_bot.execute("INSERT INTO messages (user_id, message_encoded, message_decoded, timestamp) VALUES (?, ?, ?, ?)", 
                    (message.from_user.id, encoded_text, original_text, timestamp))
    conn_bot.commit()

    bot.send_message(message.chat.id, f"🔐 Зашифровано:\n`{encoded_text}`", parse_mode="Markdown")
