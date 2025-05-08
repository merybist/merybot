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
import instaloader



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

def download_videos(shortcode, custom_label='reels'):
    try:
        filename_prefix = f"{generate_random_string()}_{custom_label}"
        filename = sanitize_filename(filename_prefix) + ".mp4"
        output_path = os.path.join('downloads', filename)
        print(output_path)
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(loader.context,"DJOwSzAtD72")
        loader.download_post(post, output_path)
       
        return output_path, None
    except Exception as e:
        print(e)