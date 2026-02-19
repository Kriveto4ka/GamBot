"""Add reminder_sent field to tasks table (Phase 4)."""
import asyncio
from database import init_db, async_session
from sqlalchemy import text

async def migrate():
    await init_db()
    
    async with async_session() as session:
        # Add reminder_sent column with default False
        await session.execute(text(
            "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_sent INTEGER DEFAULT 0 NOT NULL"
        ))
        await session.commit()
        print("Migration completed: Added reminder_sent field to tasks table")

if __name__ == "__main__":
    asyncio.run(migrate())
