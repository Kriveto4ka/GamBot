"""FSM: create task (R14, R15, R20, E1–E4)."""
from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.deadline_parser import TITLE_MAX_LEN, is_future, parse_deadline
from bot.keyboards import (
    cancel_keyboard,
    deadline_quick_keyboard,
    difficulty_keyboard,
    task_created_keyboard,
)
from bot.texts import (
    create_task_step1_title,
    create_task_step2_difficulty,
    create_task_step3_deadline,
    error_deadline_invalid,
    error_deadline_past,
    error_empty_title,
    error_title_truncated,
    task_created_message,
)
from bot.constants import DIFFICULTY_LABELS, format_difficulty_short
from bot.safe_edit import safe_edit_text
from database import async_session
from database.models import TaskDifficulty
from database.task_repo import create_task
from database.user_repo import get_or_create_user

router = Router(name="task_create")


class NewTaskStates(StatesGroup):
    title = State()
    difficulty = State()
    deadline = State()


def _quick_deadline_to_datetime(preset: str) -> datetime | None:
    """Map callback preset to UTC datetime."""
    now = datetime.now(timezone.utc)
    if preset == "1h":
        return now + timedelta(hours=1)
    if preset == "3h":
        return now + timedelta(hours=3)
    if preset == "today21":
        return parse_deadline("сегодня 21:00", now)
    if preset == "tm10":
        return parse_deadline("завтра 10:00", now)
    if preset == "tm18":
        return parse_deadline("завтра 18:00", now)
    return None


# --- Start create flow ---
@router.callback_query(F.data == "task:new")
async def start_create(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(NewTaskStates.title)
    await state.set_data({})
    text = create_task_step1_title()
    await safe_edit_text(callback.message, text=text, reply_markup=cancel_keyboard())


# --- Cancel ---
@router.callback_query(F.data == "task:create_cancel", StateFilter(NewTaskStates))
async def cancel_create(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    from bot.keyboards import main_menu_keyboard
    from bot.texts import main_menu_message
    from database.task_repo import count_active
    from database.user_repo import get_or_create_user
    async with async_session() as session:
        user, _ = await get_or_create_user(session, telegram_id=callback.from_user.id)
        count = await count_active(session, user.id)
    text = main_menu_message(user, active_tasks_count=count)
    await safe_edit_text(callback.message, text=text, reply_markup=main_menu_keyboard(count))


# --- Step 1: title (message) ---
@router.message(NewTaskStates.title, F.text)
async def step_title(message: Message, state: FSMContext) -> None:
    title = (message.text or "").strip()
    if not title:
        await message.answer(error_empty_title())
        return
    truncated = False
    if len(title) > TITLE_MAX_LEN:
        title = title[:TITLE_MAX_LEN]
        truncated = True
    await state.update_data(title=title)
    await state.set_state(NewTaskStates.difficulty)
    text = create_task_step2_difficulty(title)
    if truncated:
        text = error_title_truncated() + "\n\n" + text
    await message.answer(text=text, reply_markup=difficulty_keyboard())


@router.message(NewTaskStates.title)
async def step_title_invalid(message: Message) -> None:
    await message.answer(error_empty_title())


# --- Step 2: difficulty (callback) ---
@router.callback_query(F.data.startswith("task:diff:"), NewTaskStates.difficulty)
async def step_difficulty(callback: CallbackQuery, state: FSMContext) -> None:
    diff = callback.data.replace("task:diff:", "")
    if diff not in (TaskDifficulty.EASY.value, TaskDifficulty.MEDIUM.value, TaskDifficulty.HARD.value, TaskDifficulty.EPIC.value):
        await callback.answer("Выбери сложность из кнопок ниже.", show_alert=True)
        return
    await callback.answer()
    await state.update_data(difficulty=diff)
    await state.set_state(NewTaskStates.deadline)
    data = await state.get_data()
    title = data["title"]
    label = DIFFICULTY_LABELS.get(diff, format_difficulty_short(diff))
    text = create_task_step3_deadline(title, label)
    await safe_edit_text(callback.message, text=text, reply_markup=deadline_quick_keyboard())


# --- Step 3: deadline (callback preset or message) ---
@router.callback_query(F.data.startswith("task:dl:"), NewTaskStates.deadline)
async def step_deadline_preset(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.data == "task:dl:manual":
        from bot.deadline_parser import format_deadline_examples
        await callback.message.answer(
            "Введи дату и время дедлайна текстом.\n\n" + format_deadline_examples()
        )
        return
    preset = callback.data.replace("task:dl:", "")
    deadline_dt = _quick_deadline_to_datetime(preset)
    if not deadline_dt:
        await callback.message.answer(error_deadline_invalid())
        return
    if not is_future(deadline_dt):
        await safe_edit_text(callback.message, text=error_deadline_past(), reply_markup=deadline_quick_keyboard())
        return
    await _finish_create(callback.message, callback.from_user.id, state, deadline_dt)


@router.message(NewTaskStates.deadline, F.text)
async def step_deadline_text(message: Message, state: FSMContext) -> None:
    text_in = (message.text or "").strip()
    deadline_dt = parse_deadline(text_in)
    if deadline_dt is None:
        await message.answer(error_deadline_invalid())
        return
    if not is_future(deadline_dt):
        await message.answer(error_deadline_past())
        return
    await _finish_create(message, message.from_user.id, state, deadline_dt)


async def _finish_create(message: Message, telegram_id: int, state: FSMContext, deadline_dt: datetime) -> None:
    data = await state.get_data()
    title = data["title"]
    difficulty = data["difficulty"]
    await state.clear()
    async with async_session() as session:
        user, _ = await get_or_create_user(session, telegram_id=telegram_id)
        task = await create_task(session, user.id, title, difficulty, deadline_dt)
    text = task_created_message(task)
    try:
        await message.edit_text(text=text, reply_markup=task_created_keyboard())
    except TelegramBadRequest:
        await message.answer(text=text, reply_markup=task_created_keyboard())
