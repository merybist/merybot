from botcfg import bot
from dp import conn_bot
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import time
import base64
from utils import encrypt_aes

@bot.message_handler(commands=['encode_aes'])
def encode_aes_message(message):  
     cur_bot = conn_bot.cursor()
     text_parts = message.text.split(' ', maxsplit=1) 
    
     if len(text_parts) < 2:  
        bot.send_message(message.chat.id, "❌ Напиши текст після /encode_aes")
        return

     original_text = text_parts[1]
     aes_key = get_random_bytes(16)  # Генеруємо випадковий AES-ключ
     encoded_text = encrypt_aes(original_text, aes_key)

     timestamp = int(time.time()) 

     cur_bot.execute("INSERT INTO messages_aes (user_id, message_encoded, message_decoded, pass_aes, timestamp) VALUES (?, ?, ?, ?, ?)", 
                     (message.from_user.id, encoded_text, original_text, aes_key, timestamp))
     conn_bot.commit()
    
     bot.send_message(message.chat.id, "🔐 AES-зашифрований текст:")
     bot.send_message(message.chat.id, encoded_text)

     bot.send_message(message.chat.id, "🗝 AES-ключ (збережи його!):")
     bot.send_message(message.chat.id, base64.b64encode(aes_key).decode())