"""GameTODO Bot — entry point. Phase 2: tasks CRUD + menu."""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import menu_router, start_router, statistics_router
from bot.handlers.task_create import router as task_create_router
from bot.handlers.task_list import router as task_list_router
from config import BOT_TOKEN
from database import init_db
from bot.scheduler_setup import scheduler
from bot.logic.tasks import check_deadlines
from bot.logic.notifications import check_upcoming_deadlines

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main() -> None:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set")
        sys.exit(1)

    await init_db()

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(start_router)
    dp.include_router(task_create_router)
    dp.include_router(task_list_router)
    dp.include_router(statistics_router)
    dp.include_router(menu_router)

    # Scheduler setup
    scheduler.add_job(check_deadlines, 'interval', minutes=5, args=[bot])
    scheduler.add_job(check_upcoming_deadlines, 'interval', minutes=5, args=[bot])
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
