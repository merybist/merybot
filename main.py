from botcfg import bot
from dp import conn_bot, cur_bot



import handlers.id_handler
import handlers.sendto_handler
import handlers.sendall_handler
import handlers.list_handler
import handlers.delhistory_handler
import handlers.encodeaes_handler
import handlers.decodefernet_handler
import handlers.encodefernet_handler
import handlers.decodeaes_handler
import handlers.encodebase64_handler
import handlers.decodebase64_handler
import handlers.encodebinary_handler
import handlers.decodebinary_handler
import handlers.encodebase91_handler
import handlers.decodebase91_handler
import handlers.chatmode_handler
import handlers.chatexit_handler
import handlers.chathelp_handler
import handlers.chatstop_handler
import handlers.generate_password_handler
import handlers.help_handler
import media


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