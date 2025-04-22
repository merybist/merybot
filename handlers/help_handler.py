from botcfg import bot

def handle_help(call):
    bot.send_message(call.message.chat.id, '🎬 Завантаження відео\n\n'   
                                    'Просто вставте посилання з TikTok, Instagram або YouTube — бот автоматично завантажить відео для вас.\n\n'
                                    '🆔 Ідентифікатор Telegram\n\n'
                                    '/id — Дізнатися свій Telegram ID'
                                    )
    
@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, '🎬 Завантаження відео\n\n'   
                                    'Просто вставте посилання з TikTok, Instagram або YouTube — бот автоматично завантажить відео для вас.\n\n'
                                    '🆔 Ідентифікатор Telegram\n\n'
                                    '/id — Дізнатися свій Telegram ID'
                                    )