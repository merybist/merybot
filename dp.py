from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('host')
DB_PORT = os.getenv('port')
DB_NAME = os.getenv('dbname')
DB_USER = os.getenv('user')
DB_PASSWORD = os.getenv('password') 

# Створення пулу з'єднань
connection_pool = pool.SimpleConnectionPool(
    1,  # мінімальна кількість з'єднань
    10, # максимальна кількість з'єднань
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)

# Отримання з'єднання
conn_bot = get_connection()
cur_bot = conn_bot.cursor()

# Створення таблиць
cur_bot.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        user_id BIGINT UNIQUE,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        chat_id BIGINT
    )
''')

cur_bot.execute('''
    CREATE TABLE IF NOT EXISTS search_cache (
        query VARCHAR(255) PRIMARY KEY,
        results TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

cur_bot.execute('''
    CREATE TABLE IF NOT EXISTS chat_logs (
        id SERIAL PRIMARY KEY,
        sender_id BIGINT NOT NULL,
        receiver_id BIGINT NOT NULL,
        msg_type VARCHAR(50) NOT NULL,
        content TEXT NOT NULL,
        timestamp BIGINT NOT NULL
    )
''')

cur_bot.execute('''
    CREATE TABLE IF NOT EXISTS user_passwords (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
''')

cur_bot.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        message_encoded TEXT,
        message_decoded TEXT,
        timestamp TIMESTAMP
    )
''')

cur_bot.execute('''
    CREATE TABLE IF NOT EXISTS messages_aes (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        message_encoded TEXT,
        message_decoded TEXT,
        pass_aes VARCHAR(255),
        timestamp TIMESTAMP
    )
''')

conn_bot.commit()