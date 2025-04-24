from botcfg import bot, DOWNLOADS_FOLDER
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultVideo
from chats import active_chats
from telebot import types

import os
import re
from utils import ensure_downloads_folder_exists
from utils import sanitize_filename
from utils import download_mp3
import yt_dlp
from yt_dlp import YoutubeDL
import uuid
from threading import Thread
import random
import string
from pytube import YouTube


callback_store = {}
filename_store = {}
error_store = {}
search_cache = {}


@bot.inline_handler(lambda query: extract_youtube_url(query.query) is not None)
def inline_query_handler(inline_query):
    url = extract_youtube_url(inline_query.query)
    video_id = str(uuid.uuid4())

    content = types.InputTextMessageContent(f"🔄 Завантажую відео...")

    result = types.InlineQueryResultArticle(
        id=video_id,
        title="🎬 Завантажити відео",
        description=url,
        input_message_content=content,
    )

    bot.answer_inline_query(inline_query.id, [result], cache_time=1)
    # Продовження далі: обробка в background
    import threading
    threading.Thread(target=send_video_after_inline, args=(inline_query.from_user.id, url)).start()

def send_video_after_inline(user_id, url):
    filepath, error = download_video_youtube(url)
    if error:
        bot.send_message(user_id, f"❌ Помилка: {error}")
        return

    with open(filepath, "rb") as f:
        bot.send_video(user_id, f, caption="🎬 Готово!")

    os.remove(filepath)



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

@bot.message_handler(commands=['search'])
def search_youtube_handler(message: Message):
    if message.chat.type != 'private':  # Перевірка, що це не група
        return

    query = message.text[8:].strip()  # Отримуємо текст після команди /search
    if not query:
        bot.reply_to(message, "❗ Введіть текст для пошуку після команди, наприклад: `/search смішні коти`.")
        return

    # Перевіряємо, чи є кеш для цього запиту
    if query in search_cache:
        bot.send_message(message.chat.id, f"🔎 Показую результат для: *{query}*" , parse_mode="Markdown")
        cached_videos = search_cache[query]
    else:
        bot.send_message(message.chat.id, f"🔎 Шукаю: *{query}*", parse_mode="Markdown")
        cached_videos = search_youtube(query)
        search_cache[query] = cached_videos  # Зберігаємо результат у кеші

    if not cached_videos:
        bot.send_message(message.chat.id, "❌ Нічого не знайдено.")
        return

    markup = InlineKeyboardMarkup()
    for i, video in enumerate(cached_videos):
        title = video.get('title')
        video_url = video.get('webpage_url')
        uid = str(uuid.uuid4())
        callback_store[uid] = video_url
        button = InlineKeyboardButton(f"{i+1}. {title[:50]}", callback_data=f"video_select|{uid}")
        markup.add(button)

    bot.send_message(message.chat.id, "🔽 Обери відео для завантаження:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("video_select|"))
def handle_video_selection(call):
    thread = Thread(target=process_video_selection, args=(call,))
    thread.start()

def process_video_selection(call):
    uid = call.data.split("|")[1]
    url = callback_store.get(uid)
    if not url:
        bot.answer_callback_query(call.id, "❌ Невідоме посилання.")
        return

    bot.send_message(call.message.chat.id, "⏳ Завантажую відео...")

    video_path, error = download_video_youtube(url, "video")

    if error:
        bot.send_message(call.message.chat.id, error)
        return

    if video_path is None:
        bot.send_message(call.message.chat.id, "❌ Не вдалося завантажити відео.")
        return

    try:
        button = InlineKeyboardButton("🎵 Завантажити у MP3", callback_data=f"convert_mp3_youtube|{uid}")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(button)

        with open(video_path, 'rb') as video_file:
            bot.send_video(call.message.chat.id, video_file, caption="🔗 Завантажуй відео тут 👉 @MeryLoadBot", reply_markup=keyboard)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Помилка: {e}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


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

        random_id = generate_random_string()
        filename_prefix = f"{random_id}_{custom_label}"
        output_path = os.path.join(DOWNLOADS_FOLDER, f"{sanitize_filename(filename_prefix)}.mp4")

        ydl_opts = {
            'proxy': 'socks5://dimadehtyarow:m8HccqCJn8@5.22.206.113:59101',
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',  # Вкажіть ваш юзер-агент
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return output_path, None
    except Exception as e:
        return None, f"❌ Помилка завантаження відео: {e}"

def download_mp3(url):
    try:
        ensure_downloads_folder_exists(DOWNLOADS_FOLDER)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOADS_FOLDER, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',  # Рандомний юзер-агент
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', None)
            filename = ydl.prepare_filename(info_dict).replace('.webm', '.mp3')

        return filename, title, None
    except Exception as e:
        return None, None, f"❌ Помилка завантаження аудіо: {e}"

def search_youtube(query):
    try:
        with YoutubeDL({'quiet': True}) as ydl:
            search_query = f"ytsearch5:{query}"
            result = ydl.extract_info(search_query, download=False)
            videos = result.get('entries', [])
        return videos
    except Exception as e:
        return []
    
def extract_youtube_url(text):
    match = re.search(r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w\-]+", text)
    return match.group(0) if match else None



