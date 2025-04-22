from telebot.types import Message
from botcfg import bot
from utils import download_mp3, os


@bot.message_handler(commands=['mp3'])
def handle_mp3(message: Message):
    url = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    
    if not url:
        bot.send_message(message.chat.id, "❌ Вкажи посилання на аудіо!")
        return
    
    bot.send_message(message.chat.id, "⏳ Завантажую аудіо...")
    
    filename, title ,error = download_mp3(url)
    
    if error:
        bot.send_message(message.chat.id, error)
        return
    
    with open(filename, "rb") as audio:
        bot.send_audio(message.chat.id, audio, caption="🔗 Завантажуй аудіо тут 👉 https://t.me/MeryLoadBot", timeout=240)
    
    os.remove(filename)
