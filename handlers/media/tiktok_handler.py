from botcfg import bot, DOWNLOADS_FOLDER
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from chats import active_chats
import os
import re
from utils import ensure_downloads_folder_exists
from utils import sanitize_filename, download_tiktok, download_mp3
# import yt_dlp
import uuid
import requests

callback_store = {}

# handlers/media/tiktok_handler.py
def handle_tiktok(call):
    # Код для обробки завантаження з TikTok
    bot.send_message(call.message.chat.id, "🙃 Надішліть посилання на відео з TikTok.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("convert_mp3_tiktok"))
def convert_to_mp3(call):
    parts = call.data.split("|")
    unique_id = parts[1]

    url = callback_store.get(unique_id)

    bot.send_message(call.message.chat.id, "⏳ Конвертую у MP3...")

    # Завантажуємо аудіо з відео
    filename, title, error = download_tiktok(url)

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

@bot.message_handler(func=lambda message: message.text and message.from_user.id not in active_chats and re.match(r"(https?://)?(www\.)?(tiktok\.com/.+|vm\.tiktok\.com/.+|vt\.tiktok\.com/.+)", message.text))
def videos(message: Message):
    print("tiktok")
    tiktok_url_pattern = r"(https?://)?(www\.)?(tiktok\.com/.+|vm\.tiktok\.com/.+|vt\.tiktok\.com/.+)"
    if re.match(tiktok_url_pattern, message.text):
        url = message.text.strip()
        bot.send_message(message.chat.id, "⏳ Завантажую TikTok...")

        result, content_type_or_error = download_videos(url, "video")

        # Якщо це помилка
        if isinstance(content_type_or_error, str) and content_type_or_error.startswith("❌"):
            bot.send_message(message.chat.id, content_type_or_error)
            return

        if result is None:
            bot.send_message(message.chat.id, "❌ Помилка: не вдалося завантажити відео.\n\nСпробуйте знову надіслати посилання на відео.")
            return

        try:
            if content_type_or_error == "photo":
                from telebot.types import InputMediaPhoto

                media_group = []
                for path in result:
                    with open(path, "rb") as img_file:
                        media_group.append(InputMediaPhoto(img_file.read()))

                bot.send_media_group(message.chat.id, media_group)
                bot.send_message(message.chat.id, "📸 Завантажуй фото тут 👉 @MeryLoadBot")

                # Видаляємо фото
                for path in result:
                    if os.path.exists(path):
                        os.remove(path)
                os.rmdir(os.path.dirname(result[0]))  # видаляємо тимчасову теку
            else:
                # Звичайне відео
                unique_id = str(uuid.uuid4())
                callback_store[unique_id] = url
                button = InlineKeyboardButton("🎵 Завантажити у MP3", callback_data=f"convert_mp3_tiktok|{unique_id}")
                keyboard = InlineKeyboardMarkup()
                keyboard.add(button)

                with open(result, 'rb') as video_file:
                    bot.send_video(message.chat.id, video_file, caption="🔗 Завантажуй відео тут 👉 @MeryLoadBot", reply_markup=keyboard, timeout=240)

                if os.path.exists(result):
                    os.remove(result)

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Помилка: {e}")


def download_videos(url, type):
    try:
        ensure_downloads_folder_exists(DOWNLOADS_FOLDER)
        api_url = f"https://tikwm.com/api/?url={url}"

        response = requests.get(api_url)
        data = response.json()

        if not data.get("data"):
            return None, "⚠️ Не вдалося отримати відео з API."

        post_data = data["data"]

        # Перевіряємо, чи це пост з фото
        if "images" in post_data:
            image_urls = post_data["images"]
            image_folder = os.path.join(DOWNLOADS_FOLDER, str(uuid.uuid4()))
            os.makedirs(image_folder, exist_ok=True)

            image_paths = []
            for idx, img_url in enumerate(image_urls):
                img_data = requests.get(img_url).content
                img_path = os.path.join(image_folder, f"slide_{idx + 1}.jpg")
                with open(img_path, "wb") as f:
                    f.write(img_data)
                image_paths.append(img_path)

            return image_paths, "photo"
        
        # Інакше — це відео
        if not post_data.get("play"):
            return None, "⚠️ Не вдалося отримати відео з API."

        video_url = post_data["play"]
        filename = sanitize_filename("video")
        full_path = os.path.join(DOWNLOADS_FOLDER, f"{filename}.mp4")

        video_content = requests.get(video_url).content
        with open(full_path, "wb") as f:
            f.write(video_content)

        return full_path, "video"

    except Exception as e:
        return None, f"❌ Помилка завантаження відео: {e}"


