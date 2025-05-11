from botcfg import bot
from datetime import datetime
from dp import cur_bot, conn_bot
from utils import split_text


@bot.message_handler(commands=['list'])
def list_queries(message):
    
    text_parts = message.text.split(' ', maxsplit=1)

    if len(text_parts) < 2:
        limit = 10
    else:
        param = text_parts[1].strip().lower()
        if param == "all":
            limit = None  
        else:
            try:
                limit = int(param)  
                if limit <= 0:
                    limit = 10  
            except ValueError:
                limit = 10  
   
    query = "SELECT timestamp, message_encoded, message_decoded FROM messages WHERE user_id = ? ORDER BY id DESC"
    if limit:
        query += " LIMIT ?"
    
    cur_bot.execute(query, (message.from_user.id, limit) if limit else (message.from_user.id,))
    queries = cur_bot.fetchall()


    if not queries:
        bot.send_message(message.chat.id, "❌ Ваша історія порожня!")
        return

    
    current_month_year = datetime.now().strftime("#%m%Y")
    
    response = f"Ваша історія запитів:\n\n"

    for query in queries:
        timestamp = query[0]
        encoded_message = query[1]
        decoded_message = query[2]
        
       
        if timestamp is None:
            timestamp = 0  
        
        if isinstance(timestamp, int):
            date_time = datetime.fromtimestamp(timestamp)
        else:
            try:
                date_time = datetime.strptime(timestamp, "%d.%m.%Y | %H:%M")
            except ValueError:
                date_time = datetime.fromtimestamp(int(timestamp))
        
        formatted_time = date_time.strftime("%d.%m.%Y | %H:%M")

        response += f"{current_month_year}\n{formatted_time} - \nЗашифрований текст: \n {encoded_message} \nРозшифрований текст: \n {decoded_message}\n\n"

        for part in split_text(response):
            bot.send_message(message.chat.id, part)
