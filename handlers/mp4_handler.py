from botcfg import bot
import os
import yt_dlp
from yt_dlp.utils import DownloadError
from telebot.types import Message


@bot.message_handler(commands=['mp4'])
def download_video(message: Message):
    url = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    
    
    if not url:
        bot.send_message(message.chat.id, "❌ Вкажи посилання на відео!")
        return
    
    bot.send_message(message.chat.id, "⏳ Завантажую відео...")
    
    output_path = "downloads/%(title)s.%(ext)s"
    
    try:
        # Створюємо об'єкт yt-dlp з параметрами
        ydl_opts = {
            "outtmpl": output_path,
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",  # Формат відео - mp4
            "socket_timeout": 30,  # Збільшення таймауту
        }

        # Перевірка чи файл вже існує
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)  # Не завантажуємо файл
            filename = ydl.prepare_filename(info).replace(".webm", ".mp4").replace(".m4a", ".mp4")
            title = info.get("title", "Unknown")
        
        # Якщо файл існує, відправимо його
        if os.path.exists(filename):
            bot.send_message(message.chat.id, "✅ Відео вже завантажене, відправляю файл...")
            with open(filename, "rb") as video:
                bot.send_video(message.chat.id, video, caption="🔗 Завантажуй відео тут 👉 https://t.me/MeryLoadBot",timeout=240)
        else:
            # Якщо файл ще не завантажений, завантажуємо
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Відправлення відео після завантаження
            with open(filename, "rb") as video:
                bot.send_video(message.chat.id, video, caption="🔗 Завантажуй відео тут 👉 https://t.me/MeryLoadBot",timeout=240)

        # Видалення файлу після відправки
        
    
    except DownloadError as e:
        bot.send_message(message.chat.id, f"❌ Помилка завантаження: {e}")
    
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Помилка: {e}")