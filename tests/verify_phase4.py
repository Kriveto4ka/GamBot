"""Verification script for Phase 4: Death mechanics and notifications."""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from database import init_db, async_session
from database.models import User, Task, TaskStatus, TaskDifficulty
from database.user_repo import get_or_create_user
from database.task_repo import create_task, get_active_tasks
from bot.logic.game import apply_damage, add_xp
from bot.logic.tasks import check_deadlines
from bot.logic.notifications import check_upcoming_deadlines
from aiogram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockBot:
    """Mock bot for testing notifications."""
    def __init__(self):
        self.messages = []
    
    async def send_message(self, chat_id, text):
        self.messages.append((chat_id, text[:100]))
        logger.info(f"MockBot: Message to {chat_id}: {text[:50]}...")


async def verify_phase4():
    await init_db()
    bot = MockBot()
    
    print("\n=== Phase 4 Verification ===\n")
    
    # Test 1: Death mechanics with task deletion
    print("--- Test 1: Death Mechanics ---")
    async with async_session() as session:
        telegram_id = 999888777
        user, _ = await get_or_create_user(session, telegram_id, "test_death")
        user.hp = 10  # Low HP
        
        # Create multiple active tasks
        task1 = await create_task(session, user.id, "Task 1", TaskDifficulty.EASY.value, 
                                  datetime.now(timezone.utc) + timedelta(hours=2))
        task2 = await create_task(session, user.id, "Task 2", TaskDifficulty.MEDIUM.value,
                                  datetime.now(timezone.utc) + timedelta(hours=3))
        await session.commit()
        
        tasks_before = await get_active_tasks(session, user.id)
        print(f"Active tasks before death: {len(tasks_before)}")
        
        # Trigger death via overdue task
        overdue_task = await create_task(session, user.id, "Overdue Deadly Task", 
                                         TaskDifficulty.HARD.value,
                                         datetime.now(timezone.utc) - timedelta(hours=1))
        await session.commit()
    
    # Run deadline check (should trigger death)
    await check_deadlines(bot)
    
    async with async_session() as session:
        user = await session.get(User, user.id)
        tasks_after = await get_active_tasks(session, user.id)
        
        if user.level == 1 and user.hp == 100 and len(tasks_after) == 0:
            print("✅ SUCCESS: Death mechanics work correctly")
            print(f"   - Character reset: Level={user.level}, HP={user.hp}")
            print(f"   - All tasks deleted: {len(tasks_after)} active tasks")
        else:
            print(f"❌ FAILURE: Death mechanics issue")
            print(f"   - Level={user.level} (expected 1), HP={user.hp} (expected 100)")
            print(f"   - Active tasks={len(tasks_after)} (expected 0)")
    
    # Test 2: 1-hour reminder notifications
    print("\n--- Test 2: 1-Hour Reminders ---")
    async with async_session() as session:
        telegram_id = 111222333
        user, _ = await get_or_create_user(session, telegram_id, "test_reminder")
        
        # Create task with deadline in 30 minutes
        near_deadline = datetime.now(timezone.utc) + timedelta(minutes=30)
        task = await create_task(session, user.id, "Urgent Task", 
                                TaskDifficulty.MEDIUM.value, near_deadline)
        await session.commit()
        
        print(f"Created task with deadline in 30 minutes")
        print(f"Reminder sent before: {task.reminder_sent}")
    
    # Run reminder check
    bot.messages.clear()
    await check_upcoming_deadlines(bot)
    
    async with async_session() as session:
        task = await session.get(Task, task.id)
        
        if task.reminder_sent and len(bot.messages) > 0:
            print("✅ SUCCESS: 1-hour reminder sent")
            print(f"   - Reminder flag set: {task.reminder_sent}")
            print(f"   - Notification sent: {len(bot.messages)} message(s)")
        else:
            print(f"❌ FAILURE: Reminder not sent")
            print(f"   - Reminder flag: {task.reminder_sent}")
            print(f"   - Messages sent: {len(bot.messages)}")
    
    # Test 3: Level-up notification (manual verification needed)
    print("\n--- Test 3: Level-Up Notifications ---")
    print("ℹ️  Level-up notifications are sent via task completion handler")
    print("   Manual test: Complete a task that triggers level-up in the bot")
    print("   Expected: Receive two messages (completion + level-up)")
    
    print("\n=== Verification Complete ===\n")


if __name__ == "__main__":
    asyncio.run(verify_phase4())
