import telebot
import os

bot = telebot.TeleBot('7510853360:AAGsv-D3hRB1MoVOedrP8guN5CG9vuadTlA')
telebot.apihelper.API_URL = 'http://localhost:9090/bot{0}/{1}'

ADMIN_USER_ID = 673146683
DOWNLOADS_FOLDER = os.path.abspath("downloads")