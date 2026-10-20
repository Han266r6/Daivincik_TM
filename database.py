"""
SQLite asinxron maglumat bazasy (aiosqlite)
Ulanyjylaryn anketalaryny, like-laryny we gabat gelmeleri yatda saklayar.
"""

import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "bot_database.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Ulanyjylar tablisasy
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                name TEXT,
                age INTEGER,
                gender TEXT,       -- 'male' ýa-da 'female'
                target_gender TEXT, -- 'male', 'female', ýa-da 'all'
                city TEXT,
                bio TEXT,
                photo_file_id TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Halama (Likes) tablisasy
        await db.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER,
                to_user_id INTEGER,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(from_user_id, to_user_id)
            )
        ''')
        await db.commit()

async def get_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def save_user(telegram_id: int, username: str, name: str, age: int, gender: str, target_gender: str, city: str, bio: str, photo_file_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO users (telegram_id, username, name, age, gender, target_gender, city, bio, photo_file_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(telegram_id) DO UPDATE SET
                username=excluded.username,
                name=excluded.name,
                age=excluded.age,
                gender=excluded.gender,
                target_gender=excluded.target_gender,
                city=excluded.city,
                bio=excluded.bio,
                photo_file_id=excluded.photo_file_id,
                is_active=1
        ''', (telegram_id, username, name, age, gender, target_gender, city, bio, photo_file_id))
        await db.commit()

async def set_user_active(telegram_id: int, is_active: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_active = ? WHERE telegram_id = ?", (1 if is_active else 0, telegram_id))
        await db.commit()

async def get_next_candidate(current_user: dict):
    """
    Indiki anketany gozlemek:
    - Ozi dal
    - On like ya-da dislike bermedik
    - Jynsy we gyzyklanmasy gabat gelyan
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        target_gender_clause = ""
        params = [current_user['telegram_id'], current_user['telegram_id']]

        if current_user['target_gender'] in ['male', 'female']:
            target_gender_clause = " AND gender = ?"
            params.append(current_user['target_gender'])

        sql = f'''
            SELECT * FROM users 
            WHERE is_active = 1 
              AND telegram_id != ? 
              AND telegram_id NOT IN (
                  SELECT to_user_id FROM likes WHERE from_user_id = ?
              )
              {target_gender_clause}
            ORDER BY RANDOM()
            LIMIT 1
        '''
        async with db.execute(sql, params) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def add_like(from_id: int, to_id: int, comment: str = None) -> bool:
    """
    Like goşýar. Eger özara gabat gelme (Match) bolsa True gaýtarýar.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Ilki bilen like-y goşýarys
        await db.execute('''
            INSERT OR IGNORE INTO likes (from_user_id, to_user_id, comment)
            VALUES (?, ?, ?)
        ''', (from_id, to_id, comment))
        await db.commit()

        # O biri tarap hem meni haladymy barlayas
        async with db.execute('''
            SELECT id FROM likes WHERE from_user_id = ? AND to_user_id = ?
        ''', (to_id, from_id)) as cursor:
            match = await cursor.fetchone()
            return match is not None
