"""Start command handler for GameTODO Bot."""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database.engine import async_session
from database.user_repo import get_or_create_user
from database.task_repo import count_active_tasks
from bot.texts import welcome_message, main_menu_message
from bot.keyboards import welcome_keyboard, main_menu_keyboard

start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    telegram_id = message.from_user.id
    username = message.from_user.username
    
    async with async_session() as session:
        user, is_new = await get_or_create_user(session, telegram_id, username)
        
        if is_new:
            # New user - show welcome message
            await message.answer(
                welcome_message(user),
                reply_markup=welcome_keyboard()
            )
        else:
            # Existing user - show main menu
            active_count = await count_active_tasks(session, user.id)
            await message.answer(
                main_menu_message(user, active_count),
                reply_markup=main_menu_keyboard(active_count)
            )
