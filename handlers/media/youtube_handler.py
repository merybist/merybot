from botcfg import bot, DOWNLOADS_FOLDER
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from chats import active_chats
from telebot import types
import os
import re
from utils import ensure_downloads_folder_exists
from utils import sanitize_filename


import uuid
import random
import string
from pytubefix import YouTube
from moviepy.editor import AudioFileClip


callback_store = {}
filename_store = {}
error_store = {}


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

@bot.message_handler(func=lambda message: message.from_user.id not in active_chats and re.match(r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)", message.text))
def videos(message: Message):
    youtube_url_pattern = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)"
    if re.match(youtube_url_pattern, message.text):
        url = message.text.strip()
        unique_id = str(uuid.uuid4())
        callback_store[unique_id] = url  # 💾 Зберігаємо URL
        
        bot.send_message(message.chat.id, "⏳ Завантажую YouTube...")
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
                bot.send_video(message.chat.id, video_file,width=1920,height=1080, caption="🔗 Завантажуй відео тут 👉 @MeryLoadBot", reply_markup=keyboard, timeout=240)
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

def get_video_stream(yt):
    # Першочергово пробуємо отримати 1080p із прогресивним потоком (відео+аудіо)
    return yt.streams.filter(res="1080p", file_extension='mp4', progressive=True).first() or \
           yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()


def download_video_youtube(url, custom_label="youtube_video"):
    try:
        ensure_downloads_folder_exists(DOWNLOADS_FOLDER)

        yt = YouTube(url)
        video_stream = get_video_stream(yt)
        RES = '1080p'

        for idx,i in enumerate(yt.streams):
            if i.resolution ==RES:
                print(idx)
                print(i.resolution)
                break
        print(yt.streams[idx])
        
        filename_prefix = f"{generate_random_string()}_{custom_label}"
        filename = sanitize_filename(filename_prefix) + ".mp4"
        output_path = os.path.join(DOWNLOADS_FOLDER, filename)

        video_stream.download(output_path=DOWNLOADS_FOLDER, filename=filename)
        return output_path, None

    except Exception as e:
        return None, f"❌ Помилка завантаження відео: {e}"

def download_mp3(url):
    try:
        ensure_downloads_folder_exists(DOWNLOADS_FOLDER)

        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

        if not audio_stream:
            return None, None, "❌ Не знайдено аудіо для завантаження."

        title = sanitize_filename(yt.title)
        temp_video_path = os.path.join(DOWNLOADS_FOLDER, f"{generate_random_string()}_temp.mp4")
        final_mp3_path = os.path.join(DOWNLOADS_FOLDER, f"{title}.mp3")

        audio_stream.download(output_path=DOWNLOADS_FOLDER, filename=os.path.basename(temp_video_path))

        audioclip = AudioFileClip(temp_video_path)
        audioclip.write_audiofile(final_mp3_path, bitrate="192k")
        audioclip.close()
        os.remove(temp_video_path)

        return final_mp3_path, yt.title, None

    except Exception as e:
        return None, None, f"❌ Помилка завантаження аудіо: {e}"

def extract_youtube_url(text):
    match = re.search(r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w\-]+", text)
    return match.group(0) if match else None



