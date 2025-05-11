from botcfg import bot
from dp import conn_bot, cur_bot
from datetime import datetime


@bot.message_handler(commands=['encode_binary'])
def encrypt_cmd(message):
    text = message.text.replace("/encode_binary", "").strip()
    if not text:
        bot.reply_to(message, "Введи текст в рядку з командою, для шифрування.", parse_mode="Markdown")
        return
    binarry = ' '.join(format(ord(char), '08b') for char in text)

    binary_encoded_text = ' '.join(format(ord(char), '08b') for char in text)  # Перетворення тексту в бінарний код
    original_text = text  # Зберігаємо вихідний текст

        # Збереження в базу даних
    cur_bot.execute(
        "INSERT INTO messages (user_id, message_encoded, message_decoded, timestamp) VALUES (?, ?, ?, ?)",
        (message.from_user.id, binary_encoded_text, original_text, int(datetime.now().timestamp()))
    )
    conn_bot.commit()

    bot.reply_to(message, f"Зашифровано:\n`{binarry}`", parse_mode="Markdown")  
