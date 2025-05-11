from botcfg import bot
from dp import conn_bot


@bot.message_handler(commands=['delhistory'])
def delhistory(message):
    cur_bot = conn_bot.cursor()
    cur_bot.execute("DELETE FROM messages WHERE user_id=?", (message.from_user.id,))
    conn_bot.commit()
    bot.send_message(message.chat.id, "Історія успішно очищена!")
