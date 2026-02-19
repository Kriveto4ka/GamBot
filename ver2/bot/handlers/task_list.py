"""Task list handlers for GameTODO Bot."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from database.engine import async_session
from database.user_repo import get_user_by_telegram_id, update_user_stats
from database.task_repo import (
    get_active_tasks, get_failed_tasks, get_task_by_id,
    complete_task, delete_task, count_active_tasks
)
from database.models import TaskStatus
from bot.texts import (
    task_list_header, task_list_empty, task_detail_message,
    error_task_not_found, task_already_completed,
    failed_tasks_header, failed_tasks_empty, task_completed_message,
    notification_level_up
)
from bot.keyboards import (
    task_list_keyboard, task_detail_keyboard, back_to_tasks_keyboard,
    back_to_menu_keyboard, failed_tasks_keyboard, task_completed_keyboard,
    level_up_keyboard
)
from bot.safe_edit import safe_edit_text
from bot.time_utils import format_remaining, get_now_utc
from config import DIFFICULTY_XP, xp_required_for_level

logger = logging.getLogger(__name__)
task_list_router = Router()


@task_list_router.callback_query(F.data == "task:list")
async def task_list(callback: CallbackQuery):
    """Show list of active tasks."""
    telegram_id = callback.from_user.id
    
    async with async_session() as session:
        user = await get_user_by_telegram_id(session, telegram_id)
        if not user:
            await callback.answer("Пользователь не найден. Отправь /start")
            return
        
        tasks = await get_active_tasks(session, user.id)
    
    if not tasks:
        # E7: No active tasks
        await safe_edit_text(
            callback.message,
            task_list_empty(),
            reply_markup=back_to_menu_keyboard()
        )
    else:
        await safe_edit_text(
            callback.message,
            task_list_header(len(tasks)),
            reply_markup=task_list_keyboard(tasks)
        )
    
    await callback.answer()


@task_list_router.callback_query(F.data.startswith("task:detail:"))
async def task_detail(callback: CallbackQuery):
    """Show task details."""
    task_id = int(callback.data.split(":")[-1])
    telegram_id = callback.from_user.id
    
    async with async_session() as session:
        user = await get_user_by_telegram_id(session, telegram_id)
        if not user:
            await callback.answer("Пользователь не найден. Отправь /start")
            return
        
        task = await get_task_by_id(session, task_id, user.id)
    
    # E6: Task not found
    if not task:
        await callback.answer(error_task_not_found(), show_alert=True)
        return
    
    remaining = format_remaining(task.deadline)
    await safe_edit_text(
        callback.message,
        task_detail_message(task, remaining),
        reply_markup=task_detail_keyboard(task)
    )
    await callback.answer()


@task_list_router.callback_query(F.data.startswith("task:done:"))
async def task_done(callback: CallbackQuery):
    """Mark task as completed."""
    task_id = int(callback.data.split(":")[-1])
    telegram_id = callback.from_user.id
    
    async with async_session() as session:
        user = await get_user_by_telegram_id(session, telegram_id)
        if not user:
            await callback.answer("Пользователь не найден. Отправь /start")
            return
        
        task = await get_task_by_id(session, task_id, user.id)
        
        # E6: Task not found
        if not task:
            await callback.answer(error_task_not_found(), show_alert=True)
            return
        
        # E5: Task already completed or failed
        if task.status == TaskStatus.COMPLETED:
            await callback.answer(task_already_completed(), show_alert=True)
            return
        
        if task.status == TaskStatus.FAILED:
            await callback.answer("Эта задача уже просрочена. XP не начисляется.", show_alert=True)
            return
        
        # Complete the task
        completed_task = await complete_task(session, task_id, user.id)
        if not completed_task:
            await callback.answer(error_task_not_found(), show_alert=True)
            return
        
        # Calculate XP
        diff = task.difficulty.value if hasattr(task.difficulty, 'value') else task.difficulty
        xp_gained = DIFFICULTY_XP.get(diff, 10)
        
        # Add XP and handle level up
        new_xp = user.xp + xp_gained
        new_level = user.level
        new_max_hp = user.max_hp
        level_ups = []
        
        while True:
            xp_needed = xp_required_for_level(new_level)
            if new_xp >= xp_needed:
                # Level up!
                new_xp -= xp_needed
                new_level += 1
                new_max_hp += 10
                level_ups.append(new_level)
            else:
                break
        
        # Update user stats
        new_total_completed = user.total_completed + 1
        new_max_level = max(user.max_level_reached, new_level)
        
        await update_user_stats(
            session, user,
            level=new_level,
            xp=new_xp,
            hp=user.hp,  # HP stays the same
            max_hp=new_max_hp,
            total_completed=new_total_completed,
            max_level_reached=new_max_level
        )
    
    # Show completion message
    await safe_edit_text(
        callback.message,
        task_completed_message(user, xp_gained),
        reply_markup=task_completed_keyboard()
    )
    await callback.answer()
    
    # Send level up notification if applicable
    if level_ups:
        try:
            await callback.message.answer(
                notification_level_up(user, level_ups[-1]),
                reply_markup=level_up_keyboard()
            )
        except TelegramBadRequest as e:
            logger.warning(f"Failed to send level up notification: {e}")


@task_list_router.callback_query(F.data.startswith("task:del:"))
async def task_delete(callback: CallbackQuery):
    """Delete a task."""
    task_id = int(callback.data.split(":")[-1])
    telegram_id = callback.from_user.id
    
    async with async_session() as session:
        user = await get_user_by_telegram_id(session, telegram_id)
        if not user:
            await callback.answer("Пользователь не найден. Отправь /start")
            return
        
        # Delete the task
        deleted = await delete_task(session, task_id, user.id)
    
    if not deleted:
        await callback.answer(error_task_not_found(), show_alert=True)
        return
    
    # Show task list
    await task_list(callback)


@task_list_router.callback_query(F.data == "task:failed")
async def task_failed_list(callback: CallbackQuery):
    """Show list of failed (overdue) tasks."""
    telegram_id = callback.from_user.id
    
    async with async_session() as session:
        user = await get_user_by_telegram_id(session, telegram_id)
        if not user:
            await callback.answer("Пользователь не найден. Отправь /start")
            return
        
        tasks = await get_failed_tasks(session, user.id)
    
    if not tasks:
        await safe_edit_text(
            callback.message,
            failed_tasks_empty(),
            reply_markup=back_to_tasks_keyboard()
        )
    else:
        await safe_edit_text(
            callback.message,
            failed_tasks_header(len(tasks)),
            reply_markup=failed_tasks_keyboard(tasks)
        )
    
    await callback.answer()
