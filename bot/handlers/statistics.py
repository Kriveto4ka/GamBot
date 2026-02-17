"""Statistics screen handler (R7, R18, 8.4)."""
from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards import back_to_menu_keyboard
from bot.texts import statistics_screen_message
from bot.safe_edit import safe_edit_text
from database import async_session
from database.user_repo import get_or_create_user

router = Router(name="statistics")


@router.callback_query(F.data == "screen:stats")
async def show_statistics(callback: CallbackQuery) -> None:
    """Display user statistics screen."""
    await callback.answer()
    telegram_id = callback.from_user.id
    
    async with async_session() as session:
        user, _ = await get_or_create_user(session, telegram_id=telegram_id)
    
    text = statistics_screen_message(user)
    await safe_edit_text(callback.message, text=text, reply_markup=back_to_menu_keyboard())
