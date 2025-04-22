from botcfg import bot, DOWNLOADS_FOLDER
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from chats import active_chats
import os
import re
from utils import ensure_downloads_folder_exists
from utils import sanitize_filename
import yt_dlp
import uuid


callback_store = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("convert_mp3_instagram"))
def convert_to_mp3_instagram(call):
    parts = call.data.split("|")
    unique_id = parts[1]

    url = callback_store.get(unique_id)
    bot.send_message(call.message.chat.id, "⏳ Конвертую у MP3...")

    # Завантажуємо аудіо з відео
    filename, title, error = download_mp3(url, "video")

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

@bot.message_handler(func=lambda message: message.from_user.id not in active_chats and re.match(r"(https?://)?(www\.)?(instagram\.com/reel/)([a-zA-Z0-9_-]+)", message.text))
def videos(message: Message):
    instagram_reals_url_pattern = r"(https?://)?(www\.)?(instagram\.com/reel/)([a-zA-Z0-9_-]+)"

    if re.match(instagram_reals_url_pattern, message.text):
        url = message.text.strip()
        bot.send_message(message.chat.id, "⏳ Завантажую Instagram...")
   
        video_path, error = download_videos(url)
        
        if error:
            print(error)
            bot.send_message(message.chat.id, error)
            return

        if video_path is None:
            bot.send_message(message.chat.id, "❌ Помилка: не вдалося завантажити відео.")
            return
        
        try:
            unique_id = str(uuid.uuid4())
            callback_store[unique_id] = url
            button = InlineKeyboardButton("🎵 Завантажити у MP3", callback_data=f"convert_mp3|{unique_id}")
            keyboard = InlineKeyboardMarkup()
            keyboard.add(button) 
            
            with open(video_path, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file, caption="🔗 Завантажуй відео тут 👉 @MeryLoadBot",reply_markup=keyboard ,timeout=240) #reply_markup=keyboard,
                
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Помилка: {e}")
            return
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)

def download_videos(url):
    try:
        ensure_downloads_folder_exists(DOWNLOADS_FOLDER)
        output_path = os.path.join(DOWNLOADS_FOLDER, "%(title)s.%(ext)s")
        ydl_opts = {
            "outtmpl": output_path,
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = sanitize_filename(info.get("title", "Unknown"))
            filename = os.path.join(DOWNLOADS_FOLDER, f"{title}.mp4")
        return filename, None
    except Exception as e:
        return None, f"❌ Помилка завантаження відео: {e}"


def download_mp3(url, type):
    """Завантаження аудіо з відео Instagram через yt-dlp"""
    try:
        if not url:
            return None, None, "⚠️ Посилання на Instagram не може бути порожнім."

        ensure_downloads_folder_exists(DOWNLOADS_FOLDER)

        # Завантажуємо відео через yt-dlp
        output_path = os.path.join(DOWNLOADS_FOLDER, "%(title)s.%(ext)s")
        ydl_opts = {
            "outtmpl": output_path,
            "format": "bestaudio/best",
            "postprocessors": [{
                'key': 'FFmpegAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = sanitize_filename(info.get("title", "Unknown"))
            filename = os.path.join(DOWNLOADS_FOLDER, f"{title}.mp3")
        return filename, title, None
    except Exception as e:
        return None, None, f"❌ Помилка при завантаженні MP3: {e}"