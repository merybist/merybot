from botcfg import bot, DOWNLOADS_FOLDER
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from chats import active_chats
import os
import re
from utils import ensure_downloads_folder_exists
from utils import sanitize_filename
import yt_dlp

@bot.message_handler(func=lambda message: message.from_user.id not in active_chats and re.match(r"(https?://)?(www\.)?(music\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]+)", message.text))
def videos(message: Message):
    youtube_music_watch_url_pattern = r"(https?://)?(www\.)?(music\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]+)"
    if re.match(youtube_music_watch_url_pattern, message.text):
        url = message.text.strip()
        bot.send_message(message.chat.id, "⏳ Завантажую YouTube Music...")

        video_path, error = download_video_youtube(url)

        if error:
            bot.send_message(message.chat.id, error)
            return
        
        if video_path is None:
            bot.send_message(message.chat.id, "❌ Помилка: не вдалося завантажити відео.")
            return
    
        try:
            with open(video_path, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file, caption="🔗 Завантажуй відео тут 👉 @MeryLoadBot",timeout=240) #reply_markup=keyboard,
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Помилка: {e}")
            return
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)


def download_video_youtube(url):
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