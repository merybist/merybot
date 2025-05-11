
import os
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import datetime
from datetime import time

def encrypt_aes(text, key):
    cipher = AES.new(key, AES.MODE_CBC, key)
    ciphertext = cipher.encrypt(pad(text.encode(), AES.block_size))
    return base64.b64encode(ciphertext).decode()

def decrypt_aes(encoded_text, key):
    cipher = AES.new(key, AES.MODE_CBC, key)
    decrypted = cipher.decrypt(encoded_text) 
    return unpad(decrypted, AES.block_size).decode()

def split_text(text, max_length=4096):
    """
    Розділяє текст на частини, кожна з яких не перевищує max_length символів.
    """
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


def sanitize_filename(filename):
    """
    Видаляє недопустимі символи з назви файлу.
    """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def ensure_downloads_folder_exists(downloads_folder):
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)

def escape_markdown(text, version=2):
    """
    Екранує спеціальні символи для Markdown або MarkdownV2.
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    if version == 2:
        escape_chars += r'\\'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)
