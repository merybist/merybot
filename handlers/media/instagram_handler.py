from botcfg import bot
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from chats import active_chats
import os
import re
import uuid
import string
import random
import instaloader
import re
from pathlib import Path
from moviepy.editor import VideoFileClip


callback_store = {}

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
    Download Instagram reel from URL and return path to the downloaded file.
    
    Args:
        reel_url (str): Full URL to the Instagram reel
        
    Returns:
        str: Path to the downloaded .mp4 file
    """
    # Extract shortcode from URL (handles both /p/ and /reel/ formats)
    shortcode = re.search(r'/(?:p|reel)/([^/?]+)', reel_url)
    if not shortcode:
        raise ValueError("Invalid Instagram reel URL")
    
    # Initialize Instaloader
    L = instaloader.Instaloader(
        download_videos=True,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        filename_pattern="{shortcode}"  # This will use the shortcode as filename
    )
    
    # Download the post
    post = instaloader.Post.from_shortcode(L.context, shortcode.group(1))
    L.download_post(post, target="downloads")
    
    # Find the downloaded .mp4 file
    download_dir = Path("downloads")
    mp4_file = download_dir / f"{shortcode.group(1)}.mp4"
    
    if not mp4_file.exists():
        raise FileNotFoundError("No .mp4 file found after download")
    
    return str(mp4_file)

if __name__ == "__main__":
    # Example usage
    reel_url = "https://www.instagram.com/reel/DJOwSzAtD72/?igsh=ZDgxaWR3cHhnZjFi"
    try:
        video_path = download_reel(reel_url)
        print(f"Reel downloaded to: {video_path}")
    except Exception as e:
        print(f"Error downloading reel: {e}")