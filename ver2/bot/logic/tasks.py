"""Task processing logic for GameTODO Bot."""
import logging
from datetime import datetime
from aiogram import Bot

from database.engine import async_session
from database.task_repo import (
    get_overdue_tasks, mark_task_failed, delete_all_active_tasks
)
from database.user_repo import update_user_stats
from bot.logic.game import apply_damage, reset_character
from bot.texts import notification_task_overdue, notification_death
from bot.keyboards import death_notification_keyboard, overdue_notification_keyboard
from config import DIFFICULTY_DAMAGE

logger = logging.getLogger(__name__)


async def check_deadlines(bot: Bot) -> None:
    """
    Check for overdue tasks and apply damage.
    
    This function is called by the scheduler every 5 minutes.
    """
    logger.info("Checking deadlines...")
    
    now = datetime.utcnow()
    notifications = []  # List of (telegram_id, text, keyboard) tuples
    dead_users = set()  # Track users who died to skip their remaining tasks
    
    async with async_session() as session:
        # Get all overdue tasks
        overdue_tasks = await get_overdue_tasks(session, now)
        
        if not overdue_tasks:
            logger.info("No overdue tasks found")
            return
        
        logger.info(f"Found {len(overdue_tasks)} overdue tasks")
        
        for task in overdue_tasks:
            user = task.user
            
            # Skip if user already died in this cycle
            if user.telegram_id in dead_users:
                continue
            
            # Calculate damage
            diff = task.difficulty.value if hasattr(task.difficulty, 'value') else task.difficulty
            damage = DIFFICULTY_DAMAGE.get(diff, 5)
            
            # Apply damage
            new_hp, is_dead = apply_damage(user, damage)
            
            # Update user stats
            new_total_failed = user.total_failed + 1
            
            if is_dead:
                # Handle death
                reset_character(user)
                user.total_failed = new_total_failed
                
                # Delete all active tasks
                deleted_count = await delete_all_active_tasks(session, user.id)
                logger.info(f"User {user.telegram_id} died. Deleted {deleted_count} active tasks.")
                
                # Mark this user as dead to skip remaining tasks
                dead_users.add(user.telegram_id)
                
                # Update in database
                await update_user_stats(
                    session, user,
                    level=1,
                    xp=0,
                    hp=100,
                    max_hp=100,
                    total_failed=new_total_failed
                )
                
                # Queue death notification
                notifications.append((user.telegram_id, notification_death(), death_notification_keyboard()))
            else:
                # Just apply damage
                await update_user_stats(
                    session, user,
                    hp=new_hp,
                    total_failed=new_total_failed
                )
                
                # Queue overdue notification
                notifications.append((
                    user.telegram_id,
                    notification_task_overdue(task.title, damage, user),
                    overdue_notification_keyboard()
                ))
            
            # Mark task as failed
            await mark_task_failed(session, task.id)
        
        await session.commit()
    
    # Send notifications after transaction is committed
    for telegram_id, text, keyboard in notifications:
        try:
            await bot.send_message(telegram_id, text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Failed to send notification to {telegram_id}: {e}")
    
    logger.info(f"Processed {len(overdue_tasks)} overdue tasks, {len(dead_users)} deaths")
