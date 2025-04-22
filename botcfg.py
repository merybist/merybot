import telebot
import os

bot = telebot.TeleBot('7559990146:AAExlrGO2l-ghrgesXNV0iV3j01hA40A1TA')
telebot.apihelper.API_URL = 'http://localhost:9090/bot{0}/{1}'

ADMIN_USER_ID = 673146683
DOWNLOADS_FOLDER = os.path.abspath("downloads")