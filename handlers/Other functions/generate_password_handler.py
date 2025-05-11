from botcfg import bot
from dp import *
import string
import random
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def escape_markdown(text):
    """Екранує спеціальні символи для Markdown"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def generate_password(length=32):
    """Генерує унікальний пароль заданої довжини"""
    characters = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(random.choice(characters) for _ in range(length))
        # Перевіряємо чи пароль унікальний
        cur_bot.execute("SELECT COUNT(*) FROM user_passwords WHERE password = ?", (password,))
        if cur_bot.fetchone()[0] == 0:
            return password

def save_password(user_id, password):
    """Зберігає пароль в базу даних"""
    cur_bot.execute("INSERT INTO user_passwords (user_id, password) VALUES (?, ?)", 
                   (user_id, password))
    conn_bot.commit()

def get_user_passwords(user_id):
    """Отримує всі паролі користувача"""
    cur_bot.execute("SELECT password, created_at FROM user_passwords WHERE user_id = ? ORDER BY created_at DESC", 
                   (user_id,))
    return cur_bot.fetchall()

def create_length_keyboard():
    """Створює клавіатуру з вибором довжини пароля"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("8 символів", callback_data="length_8"),
        InlineKeyboardButton("16 символів", callback_data="length_16"),
        InlineKeyboardButton("24 символи", callback_data="length_24"),
        InlineKeyboardButton("32 символи", callback_data="length_32")
    )
    return keyboard

@bot.message_handler(commands=['generate'])
def generate_password_command(message):
    """Обробник команди /generate"""
    bot.reply_to(message, "Виберіть довжину пароля:", reply_markup=create_length_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('length_'))
def handle_length_selection(call):
    """Обробник вибору довжини пароля"""
    length = int(call.data.split('_')[1])
    password = generate_password(length)
    save_password(call.from_user.id, password)
    
    # Форматуємо пароль для кращої читабельності
    formatted_password = f"🔑 Пароль ({length} символів):\n\n{password}\n\n📝 Збережено в базі даних"
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=formatted_password
    )

@bot.message_handler(commands=['passlist'])
def list_passwords_command(message):
    """Обробник команди /passlist"""
    passwords = get_user_passwords(message.from_user.id)
    if not passwords:
        bot.reply_to(message, "У вас ще немає збережених паролів")
        return
    
    response = "📋 Список ваших паролів:\n\n"
    for i, (password, created_at) in enumerate(passwords, 1):
        # Форматуємо дату для кращої читабельності
        date_str = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M")
        response += f"🔑 Пароль #{i} (створено {date_str}):\n{password}\n\n"
    
    bot.reply_to(message, response)

