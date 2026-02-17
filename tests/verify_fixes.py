import asyncio
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from database import init_db, async_session
from database.models import User, Task, TaskStatus, TaskDifficulty
from database.user_repo import get_or_create_user
from database.task_repo import create_task, get_task_by_id
from bot.logic.tasks import check_deadlines

# Setup logging
logging.basicConfig(level=logging.INFO)

class MockBot:
    def __init__(self):
        self.messages = []
        
    async def send_message(self, chat_id, text):
        print(f"MockBot: Sent to {chat_id}: {text[:50]}...")
        self.messages.append((chat_id, text))

async def verify_fixes():
    await init_db()
    print("--- Starting Verification of Fixes ---")
    
    async with async_session() as session:
        # Setup User with Low HP
        telegram_id = 999999
        user, _ = await get_or_create_user(session, telegram_id, "test_victim")
        user.hp = 5
        user.max_hp = 100
        user.level = 10
        await session.commit()
        
        # Create 2 overdue tasks (Easy damage = 5)
        # Task 1: Will kill the user (5 HP - 5 Damage = 0 -> Death -> Reset to 100 HP)
        # Task 2: Should be skipped or deleted, causing NO damage to fresh 100 HP.
        
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        task1 = await create_task(session, user.id, "Fatal Task 1", TaskDifficulty.EASY.value, past)
        task2 = await create_task(session, user.id, "Ignored Task 2", TaskDifficulty.EASY.value, past) # Same time
        
        print(f"Created tasks: {task1.id}, {task2.id} for user {user.id} (HP {user.hp})")
        
    # Run check_deadlines
    bot = MockBot()
    await check_deadlines(bot)
    
    async with async_session() as session:
        user = await session.get(User, user.id)
        # Check user state
        print(f"User state after check: HP={user.hp}, Level={user.level}")
        
        # Expectation:
        # User died -> Level 1, HP 100.
        # If loop continued: Task 2 damage (5) applied to 100 -> 95 HP.
        # If fix works: Task 2 skipped -> 100 HP.
        
        if user.level == 1 and user.hp == 100:
            print("SUCCESS: User died and reset correctly, no extra damage applied.")
        elif user.level == 1 and user.hp == 95:
            print("FAILURE: Death Loop detected! Extra damage applied after resurrection.")
        else:
            print(f"FAILURE: Unexpected state. Level {user.level}, HP {user.hp}")

        # Check tasks
        # Task 1 should be FAILED (caused death)
        # Task 2 should be DELETED (because user died)
        
        t1 = await session.get(Task, task1.id)
        t2 = await session.get(Task, task2.id)
        
        print(f"Task 1 status: {t1.status}")
        print(f"Task 2 status: {t2.status}")
        
        if t1.status == TaskStatus.FAILED.value:
            print("SUCCESS: Task 1 marked FAILED.")
        else:
             print(f"FAILURE: Task 1 status is {t1.status}")

        if t2.status == TaskStatus.DELETED.value:
            print("SUCCESS: Task 2 marked DELETED (Cascade fix).")
        elif t2.status == TaskStatus.FAILED.value:
             print(f"FAILURE: Task 2 marked FAILED (Should be DELETED).")
        else:
             print(f"FAILURE: Task 2 status is {t2.status}")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(verify_fixes())
