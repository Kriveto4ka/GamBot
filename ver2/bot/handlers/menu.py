"""Menu handlers for GameTODO Bot."""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.engine import async_session
from database.user_repo import get_user_by_telegram_id
from database.task_repo import count_active_tasks, get_nearest_deadline
from bot.texts import main_menu_message, character_screen_message, statistics_screen_message, coming_soon
from bot.keyboards import main_menu_keyboard, back_to_menu_keyboard
from bot.safe_edit import safe_edit_text
from bot.time_utils import format_deadline_date

menu_router = Router()


async def _get_user_and_stats(session, telegram_id: int):
    """Helper to get user and task stats."""
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        return None, 0, "—"
    
    active_count = await count_active_tasks(session, user.id)
    nearest = await get_nearest_deadline(session, user.id)
    nearest_text = format_deadline_date(nearest) if nearest else "—"
    
    return user, active_count, nearest_text


@menu_router.callback_query(F.data == "menu")
async def callback_menu(callback: CallbackQuery):
    """Handle main menu button."""
    telegram_id = callback.from_user.id
    
    async with async_session() as session:
        user, active_count, _ = await _get_user_and_stats(session, telegram_id)
        
        if not user:
            await callback.answer("Пользователь не найден. Отправь /start")
            return
        
        await safe_edit_text(
            callback.message,
            main_menu_message(user, active_count),
            reply_markup=main_menu_keyboard(active_count)
        )
    
    await callback.answer()


@menu_router.callback_query(F.data == "screen:character")
async def callback_character(callback: CallbackQuery):
    """Handle character screen button."""
    telegram_id = callback.from_user.id
    
    async with async_session() as session:
        user, active_count, nearest_text = await _get_user_and_stats(session, telegram_id)
        
        if not user:
            await callback.answer("Пользователь не найден. Отправь /start")
            return
        
        await safe_edit_text(
            callback.message,
            character_screen_message(user, active_count, nearest_text),
            reply_markup=back_to_menu_keyboard()
        )
    
    await callback.answer()


@menu_router.callback_query(F.data == "screen:stats")
async def callback_stats(callback: CallbackQuery):
    """Handle statistics screen button."""
    telegram_id = callback.from_user.id
    
    async with async_session() as session:
        user = await get_user_by_telegram_id(session, telegram_id)
        
        if not user:
            await callback.answer("Пользователь не найден. Отправь /start")
            return
        
        await safe_edit_text(
            callback.message,
            statistics_screen_message(user),
            reply_markup=back_to_menu_keyboard()
        )
    
    await callback.answer()
