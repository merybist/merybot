from botcfg import bot
from datetime import datetime
from utils import escape_markdown
from dp import conn_bot, cur_bot


@bot.message_handler(commands=['decode_binary'])
def decrypt_cmd(message):
    binarry = message.text.replace("/decode_binary", "").strip()
    if not binarry:
        bot.reply_to(message, "Введи двійковий код для його дешифрування", parse_mode="Markdown")
        return
    try:
        if not all(char in "01 " for char in binarry):
            raise ValueError("Некоректний двійковий код")
        text = ''.join(chr(int(b, 2)) for b in binarry.split())
        escaped_text = escape_markdown(text, version=2)

        cur_bot.execute(
            "INSERT INTO messages (user_id, message_encoded, message_decoded, timestamp) VALUES (?, ?, ?, ?)",
            (message.from_user.id, binarry, text, int(datetime.now().timestamp()))
        )
        conn_bot.commit()

        bot.reply_to(message, f"Дешифровано:\n`{escaped_text}`", parse_mode="MarkdownV2")
    except ValueError:
        bot.reply_to(message, "Помилка! Введи коректний двійковий код (тільки 0 та 1, розділені пробілами).", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Сталася помилка: {e}", parse_mode="Markdown")
