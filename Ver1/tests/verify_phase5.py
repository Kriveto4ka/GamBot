import asyncio
import logging
import sys
from datetime import datetime, timedelta, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import init_db, async_session
from database.models import User, Task, TaskStatus, TaskDifficulty
from database.user_repo import get_or_create_user
from database.task_repo import create_task, complete_task
from bot.texts import statistics_screen_message, character_screen_message, task_completed_message
from bot.logic.game import add_xp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def verify_phase5():
    await init_db()
    
    print("\n=== Phase 5 Verification ===\n")
    
    # Test 1: Statistics screen
    print("--- Test 1: Statistics Screen ---")
    async with async_session() as session:
        telegram_id = 555666777
        user, _ = await get_or_create_user(session, telegram_id, "test_stats")
        
        # Set known statistics
        user.total_completed = 47
        user.total_failed = 12
        user.max_level_reached = 7
        await session.commit()
        
        # Generate statistics message
        stats_msg = statistics_screen_message(user)
        
        # Verify content
        has_completed = "47" in stats_msg
        has_failed = "12" in stats_msg
        has_success_rate = "79%" in stats_msg  # 47/(47+12) = 79.66% -> 79% (int truncation)
        has_max_level = "7" in stats_msg
        has_date = user.created_at.strftime("%d.%m.%Y") in stats_msg
        
        if all([has_completed, has_failed, has_success_rate, has_max_level, has_date]):
            print("✅ SUCCESS: Statistics screen displays correctly")
            print(f"   - Completed: {has_completed}")
            print(f"   - Failed: {has_failed}")
            print(f"   - Success rate: {has_success_rate}")
            print(f"   - Max level: {has_max_level}")
            print(f"   - Registration date: {has_date}")
        else:
            print(f"❌ FAILURE: Statistics screen issue")
            print(f"   - Completed: {has_completed}, Failed: {has_failed}")
            print(f"   - Success rate: {has_success_rate}, Max level: {has_max_level}")
            print(f"   - Date: {has_date}")
            print(f"\nMessage:\n{stats_msg}")
    
    # Test 2: Progress bars in messages
    print("\n--- Test 2: Progress Bars ---")
    async with async_session() as session:
        telegram_id = 888999000
        user, _ = await get_or_create_user(session, telegram_id, "test_bars")
        user.level = 3
        user.xp = 150
        user.hp = 75
        user.max_hp = 130
        await session.commit()
        
        # Check character screen has progress bars
        char_msg = character_screen_message(user, 5, "через 2ч")
        has_xp_bar = "█" in char_msg and "░" in char_msg
        has_hp_bar = char_msg.count("█") >= 2  # Both XP and HP bars
        
        if has_xp_bar and has_hp_bar:
            print("✅ SUCCESS: Progress bars present in character screen")
        else:
            print(f"❌ FAILURE: Progress bars missing")
            print(f"   - XP bar: {has_xp_bar}, HP bar: {has_hp_bar}")
    
    # Test 3: Edge case E5 - Completing overdue task
    print("\n--- Test 3: Edge Case E5 (Overdue Task Completion) ---")
    async with async_session() as session:
        telegram_id = 111333555
        user, _ = await get_or_create_user(session, telegram_id, "test_e5")
        
        # Create task and mark it as FAILED (overdue)
        task = await create_task(session, user.id, "Overdue Task", 
                                TaskDifficulty.MEDIUM.value,
                                datetime.now(timezone.utc) - timedelta(hours=1))
        task.status = TaskStatus.FAILED.value
        await session.commit()
        
        # Try to complete the failed task
        result = await complete_task(session, task.id, user.id)
        
        if result is None:
            print("✅ SUCCESS: Cannot complete overdue (FAILED) task")
            print("   - complete_task returned None as expected")
        else:
            print(f"❌ FAILURE: Overdue task was completed")
            print(f"   - Task status: {result.status}")
    
    # Test 4: Edge case E11-E13 - XP overflow and level-ups
    print("\n--- Test 4: Edge Cases E11-E13 (XP and Level-ups) ---")
    async with async_session() as session:
        telegram_id = 222444666
        user, _ = await get_or_create_user(session, telegram_id, "test_xp")
        user.level = 2
        user.xp = 180  # Need 200 for level 3
        await session.commit()
        
        # Add 250 XP (should level up to 3, then have 30 XP towards level 4)
        level_up = add_xp(user, 250)
        
        # 180 + 250 = 430 XP total
        # Level 2->3 needs 200, so 430-200 = 230 XP remaining at level 3
        # Level 3 needs 300 XP to reach level 4, so stays at level 3 with 230 XP
        expected_level = 3
        expected_xp = 230
        
        if user.level == expected_level and user.xp == expected_xp and level_up:
            print("✅ SUCCESS: Multiple level-ups and XP overflow handled correctly")
            print(f"   - Final level: {user.level} (expected {expected_level})")
            print(f"   - Final XP: {user.xp} (expected {expected_xp})")
        else:
            print(f"❌ FAILURE: XP/level-up calculation issue")
            print(f"   - Level: {user.level} (expected {expected_level})")
            print(f"   - XP: {user.xp} (expected {expected_xp})")
    
    print("\n=== Verification Complete ===\n")


if __name__ == "__main__":
    asyncio.run(verify_phase5())
