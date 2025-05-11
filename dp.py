import sqlite3

conn_bot = sqlite3.connect('bot.db', check_same_thread=False)
cur_bot = conn_bot.cursor()

# Таблиця користувачів
cur_bot.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    user_id INTEGER UNIQUE, 
    first_name TEXT, 
    last_name TEXT,
    chat_id INTEGER
)''')


cur_bot.execute('''CREATE TABLE IF NOT EXISTS search_cache (
    query TEXT PRIMARY KEY,
    results TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

cur_bot.execute('''CREATE TABLE IF NOT EXISTS chat_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    msg_type TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp INTEGER NOT NULL
)''')

cur_bot.execute('''CREATE TABLE IF NOT EXISTS user_passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)''')

cur_bot.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, message_encoded TEXT, message_decoded TEXT, timestamp TEXT)''')
cur_bot.execute('''CREATE TABLE IF NOT EXISTS messages_aes(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, message_encoded TEXT, message_decoded TEXT, pass_aes TEXT ,timestamp TEXT)''')

conn_bot.commit()