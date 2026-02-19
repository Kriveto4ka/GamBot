"""Notification logic for reminders (Phase 4)."""
import logging
from datetime import datetime, timedelta, timezone
from aiogram import Bot
from database import async_session
from database.models import TaskStatus
from database.task_repo import get_active_tasks
from bot.logic.game import get_damage_penalty
from bot.texts import notification_reminder
from bot.keyboards import reminder_keyboard

logger = logging.getLogger(__name__)


async def check_upcoming_deadlines(bot: Bot) -> None:
    """Check for tasks with deadline < 1 hour and send reminders."""
    logger.info("Checking upcoming deadlines for reminders...")
    notifications = []
    
    async with async_session() as session:
        from sqlalchemy import select
        from database.models import User, Task
        from sqlalchemy.orm import selectinload
        
        # Find tasks that:
        # 1. Are active
        # 2. Have deadline within next hour
        # 3. Haven't been reminded yet
        now = datetime.now(timezone.utc)
        one_hour_later = now + timedelta(hours=1)
        
        result = await session.execute(
            select(Task)
            .options(selectinload(Task.user))
            .where(
                Task.status == TaskStatus.ACTIVE.value,
                Task.reminder_sent == 0,
                Task.deadline > now,
                Task.deadline <= one_hour_later
            )
        )
        tasks = list(result.scalars().all())
        
        for task in tasks:
            damage = get_damage_penalty(task.difficulty)
            notifications.append((
                task.user.telegram_id,
                notification_reminder(task.title, task.id, damage),
                reminder_keyboard(task.id)
            ))
            task.reminder_sent = True
        
        if tasks:
            await session.commit()
            logger.info(f"Sent {len(tasks)} reminder notifications.")
    
    # Send notifications outside transaction
    for chat_id, text, reply_markup in notifications:
        try:
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Failed to send reminder to {chat_id}: {e}")
