import random
import string
import os
import yt_dlp
import re
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import requests
import uuid
from moviepy.editor import VideoFileClip
from functools import wraps
from dp import cur_bot
from botcfg import bot
from functools import wraps
from botcfg import DOWNLOADS_FOLDER

def check_subscription(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        cur_bot.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cur_bot.fetchone()

        if user and user[4] == False:  # Якщо користувач не підписаний
            bot.send_message(message.chat.id, "❌ Ти не підписаний на канал. Підпишись, щоб користуватися всіма функціями.")
        else:
            return func(message, *args, **kwargs)  # Виконати хендлер, якщо підписка є
    return wrapper


def encrypt_aes(text, key):
    cipher = AES.new(key, AES.MODE_CBC, key)
    ciphertext = cipher.encrypt(pad(text.encode(), AES.block_size))
    return base64.b64encode(ciphertext).decode()

def decrypt_aes(encoded_text, key):
    cipher = AES.new(key, AES.MODE_CBC, key)
    decrypted = cipher.decrypt(encoded_text) 
    return unpad(decrypted, AES.block_size).decode()

def split_text(text, max_length=4096):
    """
    Розділяє текст на частини, кожна з яких не перевищує max_length символів.
    """
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


def sanitize_filename(filename):
    """
    Видаляє недопустимі символи з назви файлу.
    """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def ensure_downloads_folder_exists(downloads_folder):
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)


def download_mp3(url, downloads_folder="downloads"):
    """Завантаження аудіо з YouTube або YouTube Music"""
    try:
        ensure_downloads_folder_exists(downloads_folder)
        output_path = os.path.join(downloads_folder, "%(title)s.%(ext)s")
        ydl_opts = {
            "outtmpl": output_path,
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            title = info.get("title", "Unknown")
        return filename, title, None
    except Exception as e:
        return None, None, f"❌ Помилка: {e}"

def download_mp3_tiktok(url, downloads_folder="downloads"):
    """Завантаження аудіо з YouTube або YouTube Music"""
    try:
        ensure_downloads_folder_exists(downloads_folder)
        output_path = os.path.join(downloads_folder, "%(title)s.%(ext)s")
        ydl_opts = {
            "outtmpl": output_path,
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            title = info.get("title", "Unknown")
        return filename, title, None
    except Exception as e:
        return None, None, f"❌ Помилка: {e}"

def download_mp3_instagram(url, downloads_folder="downloads"):
    """Завантаження аудіо з YouTube або YouTube Music"""
    try:
        ensure_downloads_folder_exists(downloads_folder)
        output_path = os.path.join(downloads_folder, "%(title)s.%(ext)s")
        ydl_opts = {
            "outtmpl": output_path,
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            title = info.get("title", "Unknown")
        return filename, title, None
    except Exception as e:
        return None, None, f"❌ Помилка: {e}"
    
def download_tiktok(url, downloads_folder="downloads"):
    """Завантаження аудіо з TikTok через API tikwm та конвертація у MP3"""
    try:
        if not url:
            return None, None, "⚠️ Посилання на TikTok не може бути порожнім."

        ensure_downloads_folder_exists(downloads_folder)

        # 🔗 Запит до tikwm API
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url)

        if response.status_code != 200:
            return None, None, f"❌ API не відповідає. Код: {response.status_code}"

        data = response.json()

        # 📦 Перевірка структури відповіді
        if not data.get("data") or not data["data"].get("play"):
            return None, None, "⚠️ Не вдалося отримати відео з API. Можливо, відео приватне або посилання неправильне."

        # 🎥 Отримуємо відео та шляхи
        video_url = data["data"]["play"]
        title = sanitize_filename(data["data"].get("title") or f"audio_{uuid.uuid4()}")
        video_path = os.path.join(downloads_folder, f"{title}.mp4")
        audio_path = os.path.join(downloads_folder, f"{title}.mp3")

        # 📥 Завантаження відео
        video_response = requests.get(video_url)
        if video_response.status_code != 200:
            return None, None, f"❌ Не вдалося завантажити відео. Код: {video_response.status_code}"

        with open(video_path, "wb") as f:
            f.write(video_response.content)

        # 🎧 Конвертація у MP3
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path, logger=None)
        clip.close()

        # 🧹 Видаляємо відео після обробки
        os.remove(video_path)

        return audio_path, title, None

    except Exception as e:
        return None, None, f"❌ Помилка: {e}"

def escape_markdown(text, version=2):
    """
    Екранує спеціальні символи для Markdown або MarkdownV2.
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    if version == 2:
        escape_chars += r'\\'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def download_video_youtube(url, custom_label="youtube_video"):
    try:
        ensure_downloads_folder_exists(DOWNLOADS_FOLDER)

        random_id = generate_random_string()
        filename_prefix = f"{random_id}_{custom_label}"
        output_path = os.path.join(DOWNLOADS_FOLDER, f"{sanitize_filename(filename_prefix)}.%(ext)s")

        ydl_opts = {
            "outtmpl": output_path,
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "socket_timeout": 120,  # ⏱️ Тут ти можеш поставити навіть 120 або більше секунд
        }


        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = filename.replace(".webm", ".mp4").replace(".m4a", ".mp4")  # Уніфікація

        return filename, None
    except Exception as e:
        return None, f"❌ Помилка завантаження відео: {e}"