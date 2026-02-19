"""Notification logic for GameTODO Bot."""
import logging
from datetime import datetime
from aiogram import Bot

from database.engine import async_session
from database.task_repo import get_tasks_for_reminder, mark_reminder_sent
from bot.texts import notification_reminder
from bot.keyboards import reminder_keyboard

logger = logging.getLogger(__name__)


async def check_upcoming_deadlines(bot: Bot) -> None:
    """
    Check for tasks with deadlines within 1 hour and send reminders.
    
    This function is called by the scheduler every 5 minutes.
    """
    logger.info("Checking upcoming deadlines for reminders...")
    
    now = datetime.utcnow()
    
    async with async_session() as session:
        # Get tasks that need reminders
        tasks = await get_tasks_for_reminder(session, now)
        
        if not tasks:
            logger.info("No tasks need reminders")
            return
        
        logger.info(f"Found {len(tasks)} tasks needing reminders")
        
        for task in tasks:
            try:
                # Send reminder
                await bot.send_message(
                    task.user.telegram_id,
                    notification_reminder(task),
                    reply_markup=reminder_keyboard(task.id)
                )
                
                # Mark reminder as sent
                await mark_reminder_sent(session, task.id)
                logger.info(f"Sent reminder for task {task.id} to user {task.user.telegram_id}")
                
            except Exception as e:
                logger.error(f"Failed to send reminder for task {task.id}: {e}")
        
        await session.commit()
    
    logger.info(f"Sent {len(tasks)} reminders")
