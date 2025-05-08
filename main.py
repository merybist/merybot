
from dotenv import load_dotenv
import os
import re
from botcfg import bot, DOWNLOADS_FOLDER
from dp import conn_bot, cur_bot
from telebot.types import InlineKeyboardMarkup


import handlers.id_handler
import handlers.sendto_handler
import handlers.sendall_handler
import handlers.list_handler
import handlers.delhistory_handler
import handlers.media.tiktok_handler
import handlers.media.youtube_handler
import handlers.media.youtube_music_handler
import handlers.media.soundcloud_handler
import handlers.media.instagram_handler
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
import handlers.media.youtube_shorts_handler
import handlers.media.inline_mode_handler

load_dotenv('/home/ostapchuk/Документи/VC projects/PASS.env') # Додав повний шлях, через тещо не хотів працювати .env

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def split_text(text, max_length=4096):
    """
    Розділяє текст на частини, кожна з яких не перевищує max_length символів.
    """
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


def ensure_downloads_folder_exists():
    if not os.path.exists(DOWNLOADS_FOLDER):
        os.makedirs(DOWNLOADS_FOLDER)

def sanitize_filename(filename):
    """
    Видаляє недопустимі символи з назви файлу.
    """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

cur_bot.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, message_encoded TEXT, message_decoded TEXT, timestamp TEXT)''')
cur_bot.execute('''CREATE TABLE IF NOT EXISTS messages_aes(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, message_encoded TEXT, message_decoded TEXT, pass_aes TEXT ,timestamp TEXT)''')
conn_bot.commit()

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

    markup = InlineKeyboardMarkup()



bot.polling(none_stop=True, timeout=120, long_polling_timeout=120)
