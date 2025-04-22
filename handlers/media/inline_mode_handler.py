from telebot.types import InlineQuery, InlineQueryResultCachedVideo
from botcfg import bot
from utils import download_video_youtube, ensure_downloads_folder_exists
import os
import uuid

# Канал для кешування
CACHE_CHANNEL = "@hashvideo"

# Зберігаємо file_id кешованих відео
cached_file_ids = {}

@bot.inline_handler(func=lambda query: True)
def inline_youtube_handler(inline_query: InlineQuery):
    query_text = inline_query.query.strip()
    if not query_text:
        return

    # Перевірка на YouTube-посилання
    if "youtu" not in query_text:
        return

    # Якщо вже кешовано
    if query_text in cached_file_ids:
        file_id = cached_file_ids[query_text]
        result = InlineQueryResultCachedVideo(
            id=str(uuid.uuid4()),
            video_file_id=file_id,
            title="Завантажене відео",
            caption="🎬 Готове відео",
        )
        bot.answer_inline_query(inline_query.id, [result], cache_time=1)
        return

    # Скачуємо відео
    bot.answer_inline_query(inline_query.id, [], switch_pm_text="⏳ Завантажую відео...", switch_pm_parameter="start")
    ensure_downloads_folder_exists()
    video_path, error = download_video_youtube(query_text, "inline")

    if error or not os.path.exists(video_path):
        return

    # Відправляємо в канал для кешування
    with open(video_path, 'rb') as video:
        msg = bot.send_video(
            chat_id=CACHE_CHANNEL,
            video=video,
            caption="📥 Кешоване відео"
        )

    file_id = msg.video.file_id
    cached_file_ids[query_text] = file_id

    # Видаємо результат у інлайн
    result = InlineQueryResultCachedVideo(
        id=str(uuid.uuid4()),
        video_file_id=file_id,
        title="Готове відео",
        caption="🎬 Завантажено через бота"
    )
    bot.answer_inline_query(inline_query.id, [result], cache_time=1)

    # Очищення
    os.remove(video_path)