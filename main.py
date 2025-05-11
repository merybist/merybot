from botcfg import bot
from dp import conn_bot, cur_bot



import handlers.other.id_handler
import handlers.other.sendto_handler
import handlers.other.sendall_handler
import handlers.other.list_handler
import handlers.other.delhistory_handler
import handlers.other.encodeaes_handler
import handlers.other.decodefernet_handler
import handlers.other.encodefernet_handler
import handlers.other.decodeaes_handler
import handlers.other.encodebase64_handler
import handlers.other.decodebase64_handler
import handlers.other.encodebinary_handler
import handlers.other.decodebinary_handler
import handlers.other.encodebase91_handler
import handlers.other.decodebase91_handler
import handlers.other.chatmode_handler
import handlers.other.chatexit_handler
import handlers.other.chathelp_handler
import handlers.other.chatstop_handler
import handlers.other.generate_password_handler
import handlers.other.help_handler
import handlers.media.youtube_handler
import handlers.media.instagram_handler
import handlers.media.tiktok_handler


@bot.message_handler(commands=['start'])
def main(message):
    cur_bot = conn_bot.cursor()
    first_name = message.from_user.first_name or "" 
    last_name = message.from_user.last_name or "" 
    full_name = f"{first_name} {last_name}".strip()  
    user_id = message.from_user.id
     
    cur_bot.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    existing_user = cur_bot.fetchone()

    if existing_user:
        bot.send_message(message.chat.id, f'Привіт, {full_name}! Раді знову тебе бачити! 😎')
    else:
        cur_bot.execute("INSERT INTO users (user_id, first_name, last_name, chat_id) VALUES (?, ?, ?, ?)", 
                          (user_id, first_name, last_name, message.chat.id))
        conn_bot.commit()
        bot.send_message(message.chat.id, f'Привіт, {full_name}! Я бот, який вміє завантажувати відео з TikTok, Instagram та YouTube.\n\nНадішли посилання на відео, яке хочеш завантажити😊')


bot.polling(none_stop=True, timeout=120, long_polling_timeout=120)