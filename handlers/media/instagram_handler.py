from botcfg import bot, DOWNLOADS_FOLDER, RAPIDAPI_KEY
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from chats import active_chats
import os
import re
from utils import ensure_downloads_folder_exists
from utils import sanitize_filename
import uuid
import requests


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
                bot.send_video(message.chat.id, video_file, caption="🔗 Завантажуй відео тут 👉 @MeryLoadBot" ,timeout=240) #reply_markup=keyboard,
                
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Помилка: {e}")
            return
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)

def download_videos(url):
    try:
        api_url = "https://instagram-reels-downloader-api.p.rapidapi.com/download"
        headers = {
            "x-rapidapi-host": "instagram-reels-downloader-api.p.rapidapi.com",
            "x-rapidapi-key": "c9b4776399msh584913a9dce7762p1928fbjsn973d4d80f527"
        }
        payload = {"url": url}
        response = requests.post(api_url, json=payload, headers=headers)
        result = response.json()

        if "media" not in result or not result["media"]:
            return None, "❌ Не вдалося отримати відео через RapidAPI"

        video_url = result["media"]
        filename = os.path.join(DOWNLOADS_FOLDER, "video.mp4")
        r = requests.get(video_url, stream=True)
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        return filename, None
    except Exception as e:
        return None, f"❌ Помилка при завантаженні відео через RapidAPI: {e}"

def download_mp3(url, type):
    try:
        video_path, error = download_videos(url)
        if error:
            return None, None, error

        mp3_path = video_path.replace(".mp4", ".mp3")

        audio = AudioSegment.from_file(video_path)
        audio.export(mp3_path, format="mp3", bitrate="192k")

        return mp3_path, os.path.basename(mp3_path), None
    except Exception as e:
        return None, None, f"❌ Помилка при конвертації в MP3: {e}"
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)