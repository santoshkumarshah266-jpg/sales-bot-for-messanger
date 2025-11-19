import aiosqlite
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).parent / "urban_fashion.db"

async def init_db():
    """Initialize SQLite database with tables"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Products table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                regular_price REAL,
                description TEXT,
                colors TEXT,
                sizes TEXT,
                stock INTEGER DEFAULT 0,
                images TEXT,
                active INTEGER DEFAULT 1,
                created_at TEXT
            )
        """)
        
        # Conversations table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                messages TEXT,
                stage TEXT DEFAULT 'greeting',
                context TEXT,
                last_updated TEXT,
                has_media_pending INTEGER DEFAULT 0
            )
        """)
        
        # Orders table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT,
                customer_name TEXT,
                phone_primary TEXT,
                phone_alternative TEXT,
                district TEXT,
                municipality TEXT,
                ward_number TEXT,
                tole_area TEXT,
                items TEXT,
                subtotal REAL,
                delivery_charge REAL,
                total_amount REAL,
                payment_method TEXT,
                payment_screenshot TEXT,
                status TEXT DEFAULT 'pending',
                has_media_pending INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)
        
        # Payment QR table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payment_qr (
                qr_id TEXT PRIMARY KEY,
                payment_method TEXT,
                qr_image_url TEXT,
                account_name TEXT,
                active INTEGER DEFAULT 1
            )
        """)
        
        # Media notifications table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS media_notifications (
                notification_id TEXT PRIMARY KEY,
                customer_id TEXT,
                media_type TEXT,
                media_url TEXT,
                status TEXT DEFAULT 'pending',
                admin_response TEXT,
                created_at TEXT
            )
        """)
        
        await db.commit()

# Helper functions
def serialize_list(data: List) -> str:
    return json.dumps(data)

def deserialize_list(data: str) -> List:
    return json.loads(data) if data else []

def serialize_dict(data: Dict) -> str:
    return json.dumps(data)

def deserialize_dict(data: str) -> Dict:
    return json.loads(data) if data else {}

async def insert_one(table: str, data: Dict[str, Any]):
    """Insert a document into a table"""
    async with aiosqlite.connect(DB_PATH) as db:
        columns = list(data.keys())
        placeholders = ','.join(['?' for _ in columns])
        values = [data[col] for col in columns]
        
        query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
        await db.execute(query, values)
        await db.commit()

async def find_one(table: str, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find one document"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        where_clause = ' AND '.join([f"{k}=?" for k in filter_dict.keys()])
        values = list(filter_dict.values())
        
        query = f"SELECT * FROM {table} WHERE {where_clause} LIMIT 1"
        async with db.execute(query, values) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def find_many(table: str, filter_dict: Dict[str, Any] = None, limit: int = 1000) -> List[Dict[str, Any]]:
    """Find multiple documents"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        if filter_dict:
            where_clause = ' AND '.join([f"{k}=?" for k in filter_dict.keys()])
            values = list(filter_dict.values())
            query = f"SELECT * FROM {table} WHERE {where_clause} LIMIT {limit}"
            async with db.execute(query, values) as cursor:
                rows = await cursor.fetchall()
        else:
            query = f"SELECT * FROM {table} LIMIT {limit}"
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
        
        return [dict(row) for row in rows]

async def update_one(table: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]):
    """Update one document"""
    async with aiosqlite.connect(DB_PATH) as db:
        set_clause = ','.join([f"{k}=?" for k in update_dict.keys()])
        where_clause = ' AND '.join([f"{k}=?" for k in filter_dict.keys()])
        values = list(update_dict.values()) + list(filter_dict.values())
        
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        await db.execute(query, values)
        await db.commit()

async def delete_one(table: str, filter_dict: Dict[str, Any]) -> int:
    """Delete one document, returns number of deleted rows"""
    async with aiosqlite.connect(DB_PATH) as db:
        where_clause = ' AND '.join([f"{k}=?" for k in filter_dict.keys()])
        values = list(filter_dict.values())
        
        query = f"DELETE FROM {table} WHERE {where_clause}"
        cursor = await db.execute(query, values)
        await db.commit()
        return cursor.rowcount

async def count_documents(table: str, filter_dict: Dict[str, Any] = None) -> int:
    """Count documents"""
    async with aiosqlite.connect(DB_PATH) as db:
        if filter_dict:
            where_clause = ' AND '.join([f"{k}=?" for k in filter_dict.keys()])
            values = list(filter_dict.values())
            query = f"SELECT COUNT(*) FROM {table} WHERE {where_clause}"
            async with db.execute(query, values) as cursor:
                result = await cursor.fetchone()
        else:
            query = f"SELECT COUNT(*) FROM {table}"
            async with db.execute(query) as cursor:
                result = await cursor.fetchone()
        
        return result[0] if result else 0
