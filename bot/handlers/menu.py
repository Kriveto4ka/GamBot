"""Callbacks: main menu, character screen; stub for stats."""
from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards import back_to_menu_keyboard, main_menu_keyboard
from bot.safe_edit import safe_edit_text
from bot.texts import character_screen_message, main_menu_message
from bot.time_utils import format_deadline_date
from database import async_session
from database.models import User
from database.task_repo import count_active, get_nearest_deadline
from database.user_repo import get_or_create_user

router = Router(name="menu")


async def _get_user_and_tasks(telegram_id: int) -> tuple[User, int, str]:
    """Return (user, active_count, next_deadline_text)."""
    async with async_session() as session:
        user, _ = await get_or_create_user(session, telegram_id=telegram_id)
        cnt = await count_active(session, user.id)
        nearest = await get_nearest_deadline(session, user.id)
    deadline_text = format_deadline_date(nearest) if nearest else "—"
    return user, cnt, deadline_text


@router.callback_query(F.data == "menu")
async def callback_menu(callback: CallbackQuery) -> None:
    """Show main menu (from any screen)."""
    await callback.answer()
    user, active_count, _ = await _get_user_and_tasks(callback.from_user.id)
    text = main_menu_message(user, active_tasks_count=active_count)
    await safe_edit_text(callback.message, text=text, reply_markup=main_menu_keyboard(active_count))


@router.callback_query(F.data == "screen:character")
async def callback_character(callback: CallbackQuery) -> None:
    """Show character screen (R17)."""
    await callback.answer()
    user, active_count, deadline_text = await _get_user_and_tasks(callback.from_user.id)
    text = character_screen_message(user, active_tasks_count=active_count, next_deadline_text=deadline_text)
    await safe_edit_text(callback.message, text=text, reply_markup=back_to_menu_keyboard())
