"""Command /start: create character and show welcome or main menu."""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards import main_menu_keyboard, welcome_keyboard
from bot.texts import main_menu_message, welcome_message
from database import async_session
from database.task_repo import count_active
from database.user_repo import get_or_create_user

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Create or load user, send welcome (new) or main menu (returning)."""
    async with async_session() as session:
        user, is_new_user = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
        )
        active_count = await count_active(session, user.id)

    if is_new_user:
        text = welcome_message(user)
        reply_markup = welcome_keyboard(is_new=True)
    else:
        text = main_menu_message(user, active_tasks_count=active_count)
        reply_markup = main_menu_keyboard(active_tasks_count=active_count)

    await message.answer(text=text, reply_markup=reply_markup)
