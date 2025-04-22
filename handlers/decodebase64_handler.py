from botcfg import bot
import base64
import binascii
import time
from dp import conn_bot, cur_bot



@bot.message_handler(commands=['decode_base64'])
def decode_message(message):  
    text_parts = message.text.split(' ', maxsplit=1)  
        
    if len(text_parts) < 2:  
        bot.send_message(message.chat.id, "❌ Напиши текст після /decode_base64!")
        return
    
    original_text = text_parts[1]  
    try:
        decoded_text = base64.b64decode(original_text).decode()  
    except binascii.Error:  
        bot.send_message(message.chat.id, "❌ Ви ввели текст, який не є зашифрованим у форматі Base64. Будь ласка, введіть коректне зашифроване повідомлення! 😅")
        return
    except UnicodeDecodeError:  
        bot.send_message(message.chat.id, "❌ Розшифровані дані не є текстом у форматі UTF-8. Спробуйте інше повідомлення! 😅")
        return
    except Exception as e: 
        bot.send_message(message.chat.id, f"❌ Помилка: {e}. Спробуйте ще раз! 😅")
        return
    
    timestamp = int(time.time()) 

    cur_bot.execute("INSERT INTO messages (user_id, message_encoded, message_decoded, timestamp) VALUES (?, ?, ?, ?)", 
                (message.from_user.id, original_text, decoded_text, timestamp))
    conn_bot.commit()

    bot.send_message(message.chat.id, f"🔐 Розкодовано:\n`{decoded_text}`", parse_mode="Markdown")