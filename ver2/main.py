"""Main entry point for GameTODO Bot."""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN, DEADLINE_CHECK_INTERVAL_MINUTES
from database.engine import init_db
from bot.handlers.start import start_router
from bot.handlers.menu import menu_router
from bot.handlers.task_create import task_create_router
from bot.handlers.task_list import task_list_router
from bot.logic.tasks import check_deadlines
from bot.logic.notifications import check_upcoming_deadlines

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the bot."""
    # Verify token is set
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set!")
        return
    
    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    
    # Create bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register routers
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(task_create_router)
    dp.include_router(task_list_router)
    
    # Setup scheduler
    scheduler = AsyncIOScheduler()
    
    # Check deadlines every 5 minutes
    scheduler.add_job(
        check_deadlines,
        'interval',
        minutes=DEADLINE_CHECK_INTERVAL_MINUTES,
        args=[bot]
    )
    
    # Check for reminders every 5 minutes
    scheduler.add_job(
        check_upcoming_deadlines,
        'interval',
        minutes=DEADLINE_CHECK_INTERVAL_MINUTES,
        args=[bot]
    )
    
    scheduler.start()
    logger.info(f"Scheduler started, checking deadlines and reminders every {DEADLINE_CHECK_INTERVAL_MINUTES} minutes")
    
    # Start polling
    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
