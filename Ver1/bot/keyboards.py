"""Inline keyboards (SPEC R12, R13, R19)."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import Task, TaskDifficulty, TaskStatus


def welcome_keyboard(is_new: bool) -> InlineKeyboardMarkup:
    """After first /start: single button to create first task or go to menu."""
    builder = InlineKeyboardBuilder()
    if is_new:
        builder.row(
            InlineKeyboardButton(text="➕ Создать первую задачу", callback_data="menu"),
        )
    else:
        builder.row(
            InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
        )
    return builder.as_markup()


def main_menu_keyboard(active_tasks_count: int = 0) -> InlineKeyboardMarkup:
    """8.2 — Main menu buttons (R13)."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Новая задача", callback_data="task:new"),
    )
    builder.row(
        InlineKeyboardButton(text=f"📋 Мои задачи ({active_tasks_count})", callback_data="task:list"),
    )
    builder.row(
        InlineKeyboardButton(text="👤 Персонаж", callback_data="screen:character"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="screen:stats"),
    )
    return builder.as_markup()


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """R19 — Back/Menu button."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
    )
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    """8.7 — Cancel during create."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="task:create_cancel"),
    )
    return builder.as_markup()


def difficulty_keyboard() -> InlineKeyboardMarkup:
    """8.8 — Choose difficulty (R14)."""
    builder = InlineKeyboardBuilder()
    from bot.constants import DIFFICULTY_LABELS
    for diff in [TaskDifficulty.EASY, TaskDifficulty.MEDIUM, TaskDifficulty.HARD, TaskDifficulty.EPIC]:
        builder.row(
            InlineKeyboardButton(
                text=DIFFICULTY_LABELS[diff.value],
                callback_data=f"task:diff:{diff.value}",
            ),
        )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="task:create_cancel"),
    )
    return builder.as_markup()


def deadline_quick_keyboard() -> InlineKeyboardMarkup:
    """8.9, R15 — Quick deadline (decisions: explicit times)."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Через 1ч", callback_data="task:dl:1h"),
        InlineKeyboardButton(text="Через 3ч", callback_data="task:dl:3h"),
    )
    builder.row(
        InlineKeyboardButton(text="Сегодня 21:00", callback_data="task:dl:today21"),
        InlineKeyboardButton(text="Завтра 10:00", callback_data="task:dl:tm10"),
    )
    builder.row(
        InlineKeyboardButton(text="Завтра 18:00", callback_data="task:dl:tm18"),
        InlineKeyboardButton(text="✏️ Ввести", callback_data="task:dl:manual"),
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="task:create_cancel"),
    )
    return builder.as_markup()


def task_created_keyboard() -> InlineKeyboardMarkup:
    """8.10 — After create."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Ещё задачу", callback_data="task:new"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
    )
    return builder.as_markup()


def task_list_keyboard(has_failed: bool) -> InlineKeyboardMarkup:
    """8.5 — After list: Pросроченные + Меню."""
    builder = InlineKeyboardBuilder()
    if has_failed:
        builder.row(
            InlineKeyboardButton(text="⛔ Просроченные", callback_data="task:failed"),
        )
    builder.row(
        InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
    )
    return builder.as_markup()


def task_detail_keyboard(task: Task) -> InlineKeyboardMarkup:
    """8.6 — Detail: Выполнено (только для active), Удалить, К задачам."""
    builder = InlineKeyboardBuilder()
    if task.status == TaskStatus.ACTIVE.value:
        builder.row(
            InlineKeyboardButton(text="✅ Выполнено", callback_data=f"task:done:{task.id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"task:del:{task.id}"),
        )
    else:
        builder.row(
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"task:del:{task.id}"),
        )
    builder.row(
        InlineKeyboardButton(text="◀️ К задачам", callback_data="task:list"),
    )
    return builder.as_markup()


def task_list_item_keyboard(task_id: int, short_label: str) -> InlineKeyboardButton:
    """Single button for one task in list (8.5)."""
    return InlineKeyboardButton(
        text=short_label,
        callback_data=f"task:detail:{task_id}",
    )


def back_to_tasks_keyboard() -> InlineKeyboardMarkup:
    """From detail or failed list back to task list."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="◀️ К задачам", callback_data="task:list"),
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
    )
    return builder.as_markup()


def death_notification_keyboard() -> InlineKeyboardMarkup:
    """Buttons for death notification."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Новая задача", callback_data="task:new"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
    )
    return builder.as_markup()


def overdue_notification_keyboard() -> InlineKeyboardMarkup:
    """Buttons for overdue task notification."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📋 К задачам", callback_data="task:list"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
    )
    return builder.as_markup()


def reminder_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """Buttons for 1-hour reminder."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Выполнено", callback_data=f"task:done:{task_id}"),
        InlineKeyboardButton(text="📋 К задачам", callback_data="task:list"),
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
    )
    return builder.as_markup()
