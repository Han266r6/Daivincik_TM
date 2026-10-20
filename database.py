"""
SQLite asinxron maglumat bazasy (aiosqlite)
Ulanyjylaryň anketalaryny, halamalaryny, admin hasabatlaryny we ban sanawyny saklaýar.
"""

import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "bot_database.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                name TEXT,
                age INTEGER,
                gender TEXT,
                target_gender TEXT,
                city TEXT,
                bio TEXT,
                photo_file_id TEXT,
                is_active INTEGER DEFAULT 1,
                is_banned INTEGER DEFAULT 0,
                is_vip INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

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
            INSERT INTO users (telegram_id, username, name, age, gender, target_gender, city, bio, photo_file_id, is_active, is_banned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
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

async def ban_user(telegram_id: int, is_banned: bool = True):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_banned = ? WHERE telegram_id = ?", (1 if is_banned else 0, telegram_id))
        await db.commit()

async def set_user_vip(telegram_id: int, is_vip: bool = True):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_vip = ? WHERE telegram_id = ?", (1 if is_vip else 0, telegram_id))
        await db.commit()

async def get_all_active_users():
    """Rassylka (hemmelere hat ugratmak) üçin ulanyjylar"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT telegram_id FROM users WHERE is_banned = 0") as cursor:
            rows = await cursor.fetchall()
            return [r['telegram_id'] for r in rows]

async def get_stats():
    """Admin paneli üçin statistika"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        async with db.execute("SELECT COUNT(*) as count FROM users") as c:
            total_users = (await c.fetchone())['count']
        
        async with db.execute("SELECT COUNT(*) as count FROM users WHERE gender = 'male'") as c:
            male_users = (await c.fetchone())['count']

        async with db.execute("SELECT COUNT(*) as count FROM users WHERE gender = 'female'") as c:
            female_users = (await c.fetchone())['count']

        async with db.execute("SELECT COUNT(*) as count FROM users WHERE is_active = 1 AND is_banned = 0") as c:
            active_users = (await c.fetchone())['count']

        async with db.execute("SELECT COUNT(*) as count FROM users WHERE is_banned = 1") as c:
            banned_users = (await c.fetchone())['count']

        async with db.execute("SELECT COUNT(*) as count FROM likes") as c:
            total_likes = (await c.fetchone())['count']

        async with db.execute('''
            SELECT COUNT(*) / 2 as count FROM likes l1 
            JOIN likes l2 ON l1.from_user_id = l2.to_user_id AND l1.to_user_id = l2.from_user_id
        ''') as c:
            total_matches = (await c.fetchone())['count'] or 0

        return {
            "total_users": total_users,
            "male_users": male_users,
            "female_users": female_users,
            "active_users": active_users,
            "banned_users": banned_users,
            "total_likes": total_likes,
            "total_matches": total_matches
        }

async def get_recent_users(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT ?", (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_next_candidate(current_user: dict):
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
              AND is_banned = 0
              AND telegram_id != ? 
              AND telegram_id NOT IN (
                  SELECT to_user_id FROM likes WHERE from_user_id = ?
              )
              {target_gender_clause}
            ORDER BY is_vip DESC, RANDOM()
            LIMIT 1
        '''
        async with db.execute(sql, params) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def add_like(from_id: int, to_id: int, comment: str = None) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR IGNORE INTO likes (from_user_id, to_user_id, comment)
            VALUES (?, ?, ?)
        ''', (from_id, to_id, comment))
        await db.commit()

        async with db.execute('''
            SELECT id FROM likes WHERE from_user_id = ? AND to_user_id = ?
        ''', (to_id, from_id)) as cursor:
            match = await cursor.fetchone()
            return match is not None
