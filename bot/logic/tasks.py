"""Background tasks logic (Phase 3)."""
import logging
from aiogram import Bot
from database import async_session
from database.models import TaskStatus
from database.task_repo import get_overdue_active_tasks, delete_all_active_tasks
from bot.logic.game import apply_damage, get_damage_penalty
from bot.keyboards import death_notification_keyboard, overdue_notification_keyboard
from bot.texts import (
    notification_task_overdue,
    notification_death,
)

logger = logging.getLogger(__name__)


async def check_deadlines(bot: Bot) -> None:
    """Check for overdue tasks and apply penalties."""
    logger.info("Checking deadlines...")
    notifications = []
    
    async with async_session() as session:
        overdue_tasks = await get_overdue_active_tasks(session)
        dead_users = set()

        for task in overdue_tasks:
            if task.user_id in dead_users:
                continue

            user = task.user
            difficulty = task.difficulty
            damage = get_damage_penalty(difficulty)
            
            # Apply damage
            died = apply_damage(user, damage)
            
            # Mark as failed
            task.status = TaskStatus.FAILED.value
            
            if died:
                dead_users.add(user.id)
                # Delete all other active tasks to prevent death loop
                await delete_all_active_tasks(session, user.id)
                
                notifications.append((
                    user.telegram_id, 
                    notification_death(task.title, damage),
                    death_notification_keyboard()
                ))
            else:
                notifications.append((
                    user.telegram_id, 
                    notification_task_overdue(task.title, damage, user.hp, user.max_hp),
                    overdue_notification_keyboard()
                ))
                
        if overdue_tasks:
            await session.commit()
            logger.info(f"Processed {len(overdue_tasks)} overdue tasks.")

    # Send notifications outside transaction
    for chat_id, text, reply_markup in notifications:
        try:
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Failed to send notification to {chat_id}: {e}")
