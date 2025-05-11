from botcfg import bot, DOWNLOADS_FOLDER
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from chats import active_chats
import os
import re
from utils import ensure_downloads_folder_exists
from utils import sanitize_filename
from pytubefix import YouTube
import uuid
from threading import Thread
import random
import string


callback_store = {}
filename_store = {}
error_store = {}
search_cache = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("convert_mp3_youtube"))
def convert_to_mp3_youtube(call):
    parts = call.data.split("|")  # ✅ Розділяємо callback_data
    unique_id = parts[1]

    url = callback_store.get(unique_id)
    bot.send_message(call.message.chat.id, "⏳ Конвертую у MP3...")

    # Завантажуємо аудіо з відео
    filename, title, error = download_mp3(url)

    if error:
        bot.send_message(call.message.chat.id, error)
        return

    try:
        with open(filename, "rb") as audio:
            bot.send_audio(call.message.chat.id, audio, caption=f"🔗 Завантажуй аудіо тут 👉 @MeryLoadBot")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Помилка: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

@bot.message_handler(func=lambda message: message.from_user.id not in active_chats and re.match(r"(https?://)?(www\.)?(youtube\.com/shorts/)([a-zA-Z0-9_-]+)", message.text))
def videos(message: Message):
    youtube_shorts_url_pattern = r"(https?://)?(www\.)?(youtube\.com/shorts/)([a-zA-Z0-9_-]+)"
    if re.match(youtube_shorts_url_pattern, message.text):
        url = message.text.strip()
        unique_id = str(uuid.uuid4())
        callback_store[unique_id] = url  # 💾 Зберігаємо URL
        
        bot.send_message(message.chat.id, "⏳ Завантажую YouTube Shorts...")
        video_path, error = download_video_youtube(url, "video")  # Використовуємо фіксовану назву

        if error:
            bot.send_message(message.chat.id, error)
            return
        
        if video_path is None:
            bot.send_message(message.chat.id, "❌ Помилка: не вдалося завантажити відео.")
            return
        
        try:
            button = InlineKeyboardButton("🎵 Завантажити у MP3", callback_data=f"convert_mp3_youtube|{unique_id}")
            keyboard = InlineKeyboardMarkup()
            keyboard.add(button)

            with open(video_path, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file, caption="🔗 Завантажуй відео тут 👉 @MeryLoadBot", reply_markup=keyboard, timeout=240)
        except Exception as e:
            error_message = f"❌ Помилка: {e}"
            bot.send_message(message.chat.id, error_message)
            
            # Додаємо кнопку "Вирішення проблеми" тільки якщо помилка пов'язана з файлом
            if "No such file or directory" in str(e):
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("🔄 Вирішення проблеми", callback_data=f"retry_download_{unique_id}"))
                bot.send_message(message.chat.id, "Спробуйте вирішити проблему:", reply_markup=markup)
            return
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def download_video_youtube(url, custom_label="youtube_video"):
    try:
        ensure_downloads_folder_exists(DOWNLOADS_FOLDER)

        yt = YouTube(url)
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        if not video_stream:
            return None, "❌ Не знайдено відповідного відео для завантаження."

        filename_prefix = f"{generate_random_string()}_{custom_label}"
        filename = sanitize_filename(filename_prefix) + ".mp4"
        output_path = os.path.join(DOWNLOADS_FOLDER, filename)

        video_stream.download(output_path=DOWNLOADS_FOLDER, filename=filename)
        return output_path, None

    except Exception as e:
        return None, f"❌ Помилка завантаження відео: {e}"

