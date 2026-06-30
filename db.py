import sqlite3
import logging
from datetime import datetime
from contextlib import contextmanager

DB_PATH = 'bot_database.db'
logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                default_city TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("База данных инициализирована.")

def get_user(telegram_id):
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        return cursor.fetchone()

def add_user(telegram_id, username):
    with get_db_connection() as conn:
        try:
            conn.execute(
                'INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)',
                (telegram_id, username)
            )
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя: {e}")

def update_default_city(telegram_id, city):
    with get_db_connection() as conn:
        conn.execute(
            'UPDATE users SET default_city = ? WHERE telegram_id = ?',
            (city, telegram_id)
        )

def get_users_count():
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT COUNT(*) FROM users')
        return cursor.fetchone()[0]
