import telebot
import os

bot = telebot.TeleBot('')
telebot.apihelper.API_URL = 'http://localhost:3241/bot{0}/{1}'

ADMIN_USER_ID = ""
DOWNLOADS_FOLDER = os.path.abspath("downloads")

