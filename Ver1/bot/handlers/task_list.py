"""Task list, detail, done, delete, failed (R2–R5, R16, E6, E7)."""
import logging
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

logger = logging.getLogger(__name__)

from bot.keyboards import (
    back_to_tasks_keyboard,
    main_menu_keyboard,
    task_detail_keyboard,
    task_list_keyboard,
    task_list_item_keyboard,
)
from bot.texts import (
    error_task_not_found,
    failed_tasks_empty,
    failed_tasks_header,
    task_already_completed,
    task_detail_message,
    task_list_empty,
    task_list_header,
    task_completed_message,
    notification_level_up,
)
from bot.time_utils import format_remaining
from database import async_session
from database.models import Task, TaskStatus
from database.task_repo import (
    complete_task,
    count_active,
    delete_task,
    get_active_tasks,
    get_failed_tasks,
    get_task_by_id,
)
from bot.safe_edit import safe_edit_text
from database.user_repo import get_or_create_user
from bot.logic.game import add_xp, get_xp_reward, get_xp_for_next_level
from config import BOT_TOKEN
from aiogram import Bot

router = Router(name="task_list")


def _task_short_label(task: Task) -> str:
    """e.g. '📌 Сделать домашку — 5ч'."""
    rem = format_remaining(task.deadline)
    return f"📌 {task.title[:30]}{'…' if len(task.title) > 30 else ''} — {rem}"


# --- List tasks ---
@router.callback_query(F.data == "task:list")
async def list_tasks(callback: CallbackQuery) -> None:
    await callback.answer()
    telegram_id = callback.from_user.id
    async with async_session() as session:
        user, _ = await get_or_create_user(session, telegram_id=telegram_id)
        tasks = await get_active_tasks(session, user.id)
        failed = await get_failed_tasks(session, user.id)
    if not tasks:
        text = task_list_empty()
        await safe_edit_text(callback.message, text=text, reply_markup=task_list_keyboard(has_failed=len(failed) > 0))
        return
    text = task_list_header(len(tasks))
    builder = InlineKeyboardBuilder()
    for t in tasks:
        builder.row(task_list_item_keyboard(t.id, _task_short_label(t)))
    if failed:
        builder.row(InlineKeyboardButton(text="⛔ Просроченные", callback_data="task:failed"))
    builder.row(InlineKeyboardButton(text="🏠 Меню", callback_data="menu"))
    await safe_edit_text(callback.message, text=text, reply_markup=builder.as_markup())


# --- Detail ---
@router.callback_query(F.data.startswith("task:detail:"))
async def task_detail(callback: CallbackQuery) -> None:
    await callback.answer()
    try:
        task_id = int(callback.data.split(":")[-1])
    except ValueError:
        return
    telegram_id = callback.from_user.id
    async with async_session() as session:
        user, _ = await get_or_create_user(session, telegram_id=telegram_id)
        task = await get_task_by_id(session, task_id, user.id)
    if not task:
        await safe_edit_text(callback.message, text=error_task_not_found(), reply_markup=back_to_tasks_keyboard())
        return
    text = task_detail_message(task)
    await safe_edit_text(callback.message, text=text, reply_markup=task_detail_keyboard(task))


# --- Done ---
@router.callback_query(F.data.startswith("task:done:"))
async def task_done(callback: CallbackQuery) -> None:
    await callback.answer()
    try:
        task_id = int(callback.data.split(":")[-1])
    except ValueError:
        return
    telegram_id = callback.from_user.id
    already_completed = False
    async with async_session() as session:
        user, _ = await get_or_create_user(session, telegram_id=telegram_id)
        task = await complete_task(session, task_id, user.id)
        if not task:
            existing = await get_task_by_id(session, task_id, user.id)
            already_completed = existing is not None and existing.status == TaskStatus.COMPLETED.value
        else:
            # Phase 3: Award XP
            xp_reward = get_xp_reward(task.difficulty)
            # Need to re-fetch user or refresh because complete_task committed
            await session.refresh(user)
            level_up = add_xp(user, xp_reward)
            await session.commit()

    if not task:
        text = task_already_completed() if already_completed else error_task_not_found()
        await safe_edit_text(callback.message, text=text, reply_markup=back_to_tasks_keyboard())
        return
    
    text = task_completed_message(task, xp_reward, user, level_up)
    await safe_edit_text(callback.message, text=text, reply_markup=back_to_tasks_keyboard())
    
    # Phase 4: Send level-up notification if leveled up
    if level_up:
        bot = Bot(token=BOT_TOKEN)
        xp_next = get_xp_for_next_level(user.level)
        level_up_text = notification_level_up(user.level, user.hp, user.max_hp, xp_next)
        try:
            await bot.send_message(
                chat_id=telegram_id, 
                text=level_up_text,
                reply_markup=main_menu_keyboard()
            )
        except Exception as e:
            logger.error(f"Failed to send level-up notification: {e}")
        finally:
            await bot.session.close()


# --- Delete ---
@router.callback_query(F.data.startswith("task:del:"))
async def task_delete(callback: CallbackQuery) -> None:
    await callback.answer()
    try:
        task_id = int(callback.data.split(":")[-1])
    except ValueError:
        return
    telegram_id = callback.from_user.id
    async with async_session() as session:
        user, _ = await get_or_create_user(session, telegram_id=telegram_id)
        ok = await delete_task(session, task_id, user.id)
    if not ok:
        await safe_edit_text(callback.message, text=error_task_not_found(), reply_markup=back_to_tasks_keyboard())
        return
    text = "🗑 Задача удалена."
    await safe_edit_text(callback.message, text=text, reply_markup=back_to_tasks_keyboard())


# --- Failed list (R5) ---
@router.callback_query(F.data == "task:failed")
async def list_failed(callback: CallbackQuery) -> None:
    await callback.answer()
    telegram_id = callback.from_user.id
    async with async_session() as session:
        user, _ = await get_or_create_user(session, telegram_id=telegram_id)
        failed = await get_failed_tasks(session, user.id)
    if not failed:
        text = failed_tasks_empty()
    else:
        text = failed_tasks_header(len(failed))
        for t in failed:
            text += f"• {t.title} — {t.deadline.strftime('%d.%m %H:%M')}\n"
    await safe_edit_text(callback.message, text=text, reply_markup=back_to_tasks_keyboard())
