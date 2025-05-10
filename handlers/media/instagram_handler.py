from botcfg import bot, DOWNLOADS_FOLDER, RAPIDAPI_KEY
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from chats import active_chats
import os
import re
from utils import ensure_downloads_folder_exists
from utils import sanitize_filename
import uuid
import string
import random
import requests



callback_store = {}

# @bot.callback_query_handler(func=lambda call: call.data.startswith("convert_mp3_instagram"))
# def convert_to_mp3_instagram(call):
#     parts = call.data.split("|")
#     unique_id = parts[1]

#     url = callback_store.get(unique_id)
#     bot.send_message(call.message.chat.id, "⏳ Конвертую у MP3...")

#     # Завантажуємо аудіо з відео
#     filename, title, error = download_mp3(url, "video")

#     if error:
#         bot.send_message(call.message.chat.id, error)
#         return

#     try:
#         with open(filename, "rb") as audio:
#             bot.send_audio(call.message.chat.id, audio, caption=f"🔗 Завантажуй аудіо тут 👉 @MeryLoadBot")
#     except Exception as e:
#         bot.send_message(call.message.chat.id, f"❌ Помилка: {e}")
#     finally:
#         if os.path.exists(filename):
#             os.remove(filename)

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
                bot.send_video(message.chat.id, video_file, caption="🔗 Завантажуй відео тут 👉 @MeryLoadBot" ,timeout=240) #reply_markup=keyboard,
                
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Помилка: {e}")
            return
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def download_videos(instagram_url, rapidapi_key, rapidapi_host):
    url = "https://instagram-reels-downloader-api.p.rapidapi.com/download"

    querystring = {"url": instagram_url}

    headers = {
        "x-rapidapi-key": "c9b4776399msh584913a9dce7762p1928fbjsn973d4d80f527",
	    "x-rapidapi-host": "instagram-reels-downloader-api.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()

        data = response.json()
        video_url = data.get("media")
        if not video_url:
            return None, "❌ Не знайдено відео за посиланням."

        # Скачуємо файл
        video_data = requests.get(video_url).content
        filename = "instagram_video.mp4"
        with open(filename, "wb") as f:
            f.write(video_data)

        return filename, None

    except requests.RequestException as e:
        return None, f"❌ HTTP помилка: {e}"
    except Exception as e:
        return None, f"❌ Помилка: {e}"   