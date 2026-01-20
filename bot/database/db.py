import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict


class Database:
    def __init__(self, db_path: str = "stars_bot.db"):
        self.db_path = db_path
    
    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_purchases INTEGER DEFAULT 0,
                    total_spent INTEGER DEFAULT 0
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    package_id INTEGER,
                    stars_amount INTEGER,
                    bonus_amount INTEGER,
                    price INTEGER,
                    status TEXT DEFAULT 'pending',
                    telegram_payment_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            await db.commit()
    
    async def add_user(self, user_id: int, username: str = None, first_name: str = None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR IGNORE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            """, (user_id, username, first_name))
            await db.commit()
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def create_purchase(
        self, 
        user_id: int, 
        package_id: int, 
        stars_amount: int,
        bonus_amount: int,
        price: int
    ) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO purchases (user_id, package_id, stars_amount, bonus_amount, price)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, package_id, stars_amount, bonus_amount, price))
            await db.commit()
            return cursor.lastrowid
    
    async def complete_purchase(self, purchase_id: int, telegram_payment_id: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE purchases 
                SET status = 'completed', 
                    telegram_payment_id = ?,
                    completed_at = ?
                WHERE id = ?
            """, (telegram_payment_id, datetime.now(), purchase_id))
            
            # Обновляем статистику пользователя
            await db.execute("""
                UPDATE users 
                SET total_purchases = total_purchases + 1,
                    total_spent = total_spent + (
                        SELECT price FROM purchases WHERE id = ?
                    )
                WHERE user_id = (
                    SELECT user_id FROM purchases WHERE id = ?
                )
            """, (purchase_id, purchase_id))
            
            await db.commit()
    
    async def get_user_purchases(self, user_id: int) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM purchases 
                WHERE user_id = ? AND status = 'completed'
                ORDER BY created_at DESC
                LIMIT 10
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]


db = Database()
