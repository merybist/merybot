from botcfg import bot
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from chats import active_chats
import os
import re
import uuid
import string
import random
import re
from pathlib import Path
from moviepy.editor import VideoFileClip
import requests

callback_store = {}

RAPIDAPI_KEY = ""
RAPIDAPI_HOST = ""

@bot.callback_query_handler(func=lambda call: call.data.startswith("convert_mp3|"))
def convert_to_mp3_instagram(call):
    parts = call.data.split("|")
    unique_id = parts[1]

    url = callback_store.get(unique_id)
    if not url:
        bot.send_message(call.message.chat.id, "❌ Посилання більше не активне.")
        return

    bot.send_message(call.message.chat.id, "⏳ Конвертую у MP3...")

    try:
        video_path = download_reel(url)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Помилка завантаження відео: {e}")
        return

    mp3_path, error = convert_video_to_mp3(video_path)

    if error:
        bot.send_message(call.message.chat.id, f"❌ Помилка при конвертації: {error}")
        return

    try:
        with open(mp3_path, "rb") as audio:
            bot.send_audio(call.message.chat.id, audio, caption="🔗 Завантажуй аудіо тут 👉 @MeryLoadBot")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Помилка надсилання: {e}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(mp3_path):
            os.remove(mp3_path)

@bot.message_handler(func=lambda message: message.from_user.id not in active_chats and re.match(r"(https?://)?(www\.)?(instagram\.com/reel/)([a-zA-Z0-9_-]+)", message.text))
def videos(message: Message):
    instagram_reals_url_pattern = r"(https?://)?(www\.)?(instagram\.com/reel/)([a-zA-Z0-9_-]+)"

    if re.match(instagram_reals_url_pattern, message.text):
        url = message.text.strip()
        bot.send_message(message.chat.id, "⏳ Завантажую Instagram...")
   
        video_path= download_reel(url)
        error = None

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
                bot.send_video(message.chat.id, video_file, caption="🔗 Завантажуй відео тут 👉 @MeryLoadBot", reply_markup=keyboard ,timeout=240) #reply_markup=keyboard,
                
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Помилка: {e}")
            return
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def convert_video_to_mp3(video_path):
    try:
        output_path = video_path.replace(".mp4", ".mp3")
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(output_path)
        clip.close()
        return output_path, None
    except Exception as e:
        return None, str(e)

def download_reel(reel_url):
    """
    Завантажує Instagram Reel через RapidAPI і повертає шлях до локального файлу.
    """
    url = "https://instagram-reels-downloader-api.p.rapidapi.com/download"
    querystring = {"url": reel_url}

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        raise Exception(f"RapidAPI error: {response.status_code} - {response.text}")

    data = response.json()
    # Припустимо, в відповіді є поле 'video_url' або схоже, де лежить пряме посилання на відео
    video_url = data.get('video_url')
    if not video_url:
        raise Exception("Не знайдено відео в відповіді RapidAPI")

    # Завантажуємо відео локально
    local_filename = "downloads/" + reel_url.rstrip('/').split('/')[-1] + ".mp4"
    os.makedirs(os.path.dirname(local_filename), exist_ok=True)

    with requests.get(video_url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return local_filename