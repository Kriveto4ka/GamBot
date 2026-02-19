"""Task creation handlers for GameTODO Bot."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from database.engine import async_session
from database.user_repo import get_user_by_telegram_id
from database.task_repo import create_task, TITLE_MAX_LEN
from database.models import TaskDifficulty
from bot.texts import (
    task_create_step1, task_create_step2, task_create_step3,
    task_created_message, error_empty_title, error_title_truncated,
    error_deadline_past, error_deadline_invalid
)
from bot.keyboards import (
    cancel_keyboard, difficulty_keyboard, deadline_quick_keyboard,
    task_created_keyboard
)
from bot.safe_edit import safe_edit_text
from bot.deadline_parser import parse_deadline, is_future, get_now_local
from bot.time_utils import get_now_utc

# Timezone for calculations
INPUT_TIMEZONE = ZoneInfo("Europe/Moscow")

task_create_router = Router()


class NewTaskStates(StatesGroup):
    """States for task creation FSM."""
    title = State()
    difficulty = State()
    deadline = State()


@task_create_router.callback_query(F.data == "task:new")
async def task_new(callback: CallbackQuery, state: FSMContext):
    """Start task creation process."""
    await state.set_state(NewTaskStates.title)
    await safe_edit_text(
        callback.message,
        task_create_step1(),
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


@task_create_router.callback_query(F.data == "task:create_cancel")
async def task_create_cancel(callback: CallbackQuery, state: FSMContext):
    """Cancel task creation."""
    await state.clear()
    
    # Show main menu
    from bot.handlers.menu import callback_menu
    await callback_menu(callback)


@task_create_router.message(NewTaskStates.title)
async def task_create_title(message: Message, state: FSMContext):
    """Handle title input."""
    title = message.text.strip()
    
    # E2: Empty title
    if not title:
        await message.answer(error_empty_title())
        return
    
    # E3: Title too long
    truncated = False
    if len(title) > TITLE_MAX_LEN:
        title = title[:TITLE_MAX_LEN]
        truncated = True
    
    # Store title in state
    await state.update_data(title=title, truncated=truncated)
    await state.set_state(NewTaskStates.difficulty)
    
    # Show difficulty selection
    text = task_create_step2(title)
    if truncated:
        text = error_title_truncated() + "\n\n" + text
    
    await message.answer(text, reply_markup=difficulty_keyboard())


@task_create_router.callback_query(F.data.startswith("task:diff:"), NewTaskStates.difficulty)
async def task_create_difficulty(callback: CallbackQuery, state: FSMContext):
    """Handle difficulty selection."""
    diff = callback.data.split(":")[-1]
    
    if diff not in ["easy", "medium", "hard", "epic"]:
        await callback.answer("Выбери сложность из кнопок ниже.", show_alert=True)
        return
    
    # Store difficulty in state
    await state.update_data(difficulty=diff)
    await state.set_state(NewTaskStates.deadline)
    
    # Get stored title
    data = await state.get_data()
    title = data.get("title", "")
    
    # Show deadline selection
    await safe_edit_text(
        callback.message,
        task_create_step3(title, diff),
        reply_markup=deadline_quick_keyboard()
    )
    await callback.answer()


@task_create_router.callback_query(F.data.startswith("task:dl:"), NewTaskStates.deadline)
async def task_create_deadline_quick(callback: CallbackQuery, state: FSMContext):
    """Handle quick deadline selection."""
    dl_code = callback.data.split(":")[-1]
    
    now_local = get_now_local()
    
    if dl_code == "1h":
        deadline = now_local + timedelta(hours=1)
    elif dl_code == "3h":
        deadline = now_local + timedelta(hours=3)
    elif dl_code == "today":
        # Today at 21:00
        deadline = now_local.replace(hour=21, minute=0, second=0, microsecond=0)
        if deadline <= now_local:
            deadline += timedelta(days=1)
    elif dl_code == "tom_morning":
        # Tomorrow at 10:00
        deadline = (now_local + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    elif dl_code == "tom_evening":
        # Tomorrow at 18:00
        deadline = (now_local + timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
    elif dl_code == "custom":
        # Request custom input
        await callback.message.edit_text(
            "Введи дату и время дедлайна:\n\n" + 
            "• завтра 18:00\n" +
            "• 25.01 15:30\n" +
            "• через 2 часа",
            reply_markup=cancel_keyboard()
        )
        await callback.answer()
        return
    else:
        await callback.answer("Ошибка выбора дедлайна", show_alert=True)
        return
    
    # Convert to UTC for storage
    deadline_utc = deadline.astimezone(ZoneInfo("UTC"))
    
    # Create the task
    await _finish_create(callback, state, deadline_utc)


@task_create_router.message(NewTaskStates.deadline)
async def task_create_deadline_text(message: Message, state: FSMContext):
    """Handle custom deadline input."""
    text = message.text.strip()
    
    # Parse deadline
    deadline = parse_deadline(text)
    
    if not deadline:
        await message.answer(error_deadline_invalid())
        return
    
    # E1: Check if deadline is in the future
    if not is_future(deadline):
        await message.answer(error_deadline_past())
        return
    
    # Create the task
    await _finish_create_text(message, state, deadline)


async def _finish_create(callback: CallbackQuery, state: FSMContext, deadline: datetime):
    """Finish task creation from callback."""
    data = await state.get_data()
    title = data.get("title", "")
    difficulty = data.get("difficulty", "easy")
    
    telegram_id = callback.from_user.id
    
    async with async_session() as session:
        user = await get_user_by_telegram_id(session, telegram_id)
        if not user:
            await callback.answer("Пользователь не найден. Отправь /start")
            return
        
        # Create task
        diff_enum = TaskDifficulty(difficulty)
        task = await create_task(session, user.id, title, diff_enum, deadline)
    
    # Clear state
    await state.clear()
    
    # Show confirmation
    await safe_edit_text(
        callback.message,
        task_created_message(task),
        reply_markup=task_created_keyboard()
    )
    await callback.answer()


async def _finish_create_text(message: Message, state: FSMContext, deadline: datetime):
    """Finish task creation from text message."""
    data = await state.get_data()
    title = data.get("title", "")
    difficulty = data.get("difficulty", "easy")
    
    telegram_id = message.from_user.id
    
    async with async_session() as session:
        user = await get_user_by_telegram_id(session, telegram_id)
        if not user:
            await message.answer("Пользователь не найден. Отправь /start")
            return
        
        # Create task
        diff_enum = TaskDifficulty(difficulty)
        task = await create_task(session, user.id, title, diff_enum, deadline)
    
    # Clear state
    await state.clear()
    
    # Show confirmation
    await message.answer(
        task_created_message(task),
        reply_markup=task_created_keyboard()
    )
