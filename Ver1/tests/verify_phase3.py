import asyncio
import logging
from datetime import datetime, timedelta, timezone

from database import init_db, async_session
from database.models import User, Task, TaskStatus, TaskDifficulty
from database.user_repo import get_or_create_user
from database.task_repo import create_task, get_task_by_id
from bot.logic.game import add_xp, apply_damage, get_xp_reward, get_damage_penalty
from bot.logic.tasks import check_deadlines
from aiogram import Bot

# Mock bot
class MockBot:
    async def send_message(self, chat_id, text):
        print(f"MockBot: Sent to {chat_id}: {text[:50]}...")

async def verify_phase3():
    await init_db()
    
    print("--- Starting Verification Phase 3 ---")
    
    async with async_session() as session:
        # 1. Setup User
        telegram_id = 123456789
        user, is_new = await get_or_create_user(session, telegram_id, "test_user")
        # Reset user for testing
        user.level = 1
        user.xp = 0
        user.hp = 100
        user.max_hp = 100
        await session.commit()
        print(f"User setup: Lvl {user.level}, XP {user.xp}, HP {user.hp}")

        # 2. Test XP and Level Up
        print("\n--- Testing XP and Level Up ---")
        xp_reward = 150 # Enough for Lvl 1 -> 2 (100 XP needed)
        level_up = add_xp(user, xp_reward)
        await session.commit()
        
        if level_up and user.level == 2 and user.xp == 50:
            print(f"SUCCESS: Level up works. Lvl {user.level}, XP {user.xp}")
        else:
            print(f"FAILURE: Level up failed. Lvl {user.level}, XP {user.xp}, Expected Lvl 2, XP 50")
            
        # 3. Test Deadline Check (Damage)
        print("\n--- Testing Deadline Check ---")
        # Create overdue task
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        task = await create_task(session, user.id, "Overdue Task", TaskDifficulty.MEDIUM.value, past)
        print(f"Created overdue task: {task.id}")
        
        # Run check_deadlines
        bot = MockBot()
        # We need to run the logic from tasks.py. 
        # But check_deadlines manages its own session.
        pass
        
    # Run check_deadlines (it opens its own session)
    await check_deadlines(bot)
    
    async with async_session() as session:
        # Check result
        task = await get_task_by_id(session, task.id, user.id)
        # Note: task status might be FAILED now?
        # get_task_by_id excludes DELETED, but FAILED should be visible? 
        # Repo `get_task_by_id` excludes DELETED.
        # But `failed` tasks are FAILED status.
        
        # Reload user
        user = await session.get(User, user.id)
        
        if task.status == TaskStatus.FAILED.value:
             print(f"SUCCESS: Task marked FAILED.")
        else:
             print(f"FAILURE: Task status is {task.status}")
             
        # Damage for Medium is 15. User HP was 100 (restored on level up).
        if user.hp == 100 - 15:
             print(f"SUCCESS: Damage applied. HP {user.hp}")
        else:
             print(f"FAILURE: HP is {user.hp}, expected 85")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(verify_phase3())
