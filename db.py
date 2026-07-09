import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Читаем параметры подключения из окружения (или используем дефолтные для локальной разработки)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")

@contextmanager
def get_db_connection():
    # Используем RealDictCursor, чтобы код в tg.py мог обращаться к полям как к словарю: user['default_city']
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        cursor_factory=RealDictCursor
    )
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # В PostgreSQL используем SERIAL для автоинкремента
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        telegram_id BIGINT UNIQUE NOT NULL,
                        username TEXT,
                        default_city TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            logger.info("База данных PostgreSQL успешно инициализирована.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации PostgreSQL: {e}")
        # Если база обязательна для запуска, можно сделать raise e, чтобы бот не стартовал впустую
        raise e

def get_user(telegram_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
            return cursor.fetchone()

def add_user(telegram_id, username):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # В PostgreSQL синтаксис избегания дубликатов - ON CONFLICT DO NOTHING
                cursor.execute(
                    'INSERT INTO users (telegram_id, username) VALUES (%s, %s) ON CONFLICT (telegram_id) DO NOTHING',
                    (telegram_id, username)
                )
            except Exception as e:
                logger.error(f"Ошибка при добавлении пользователя: {e}")

def update_default_city(telegram_id, city):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE users SET default_city = %s WHERE telegram_id = %s',
                (city, telegram_id)
            )

def get_users_count():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM users')
            # Так как мы используем RealDictCursor, результат будет {'count': X}
            # Но для COUNT(*) безопаснее забрать по индексу или ключу
            res = cursor.fetchone()
            return res['count'] if res else 0
