"""Keyboards for GameTODO Bot."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import Task, TaskStatus


# 8.1 Welcome keyboard
def welcome_keyboard() -> InlineKeyboardMarkup:
    """Welcome screen keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➕ Создать первую задачу", callback_data="task:new"))
    return builder.as_markup()


# 8.2 Main menu keyboard
def main_menu_keyboard(active_tasks_count: int = 0) -> InlineKeyboardMarkup:
    """Main menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➕ Новая задача", callback_data="task:new"))
    tasks_text = f"📋 Мои задачи ({active_tasks_count})" if active_tasks_count > 0 else "📋 Мои задачи"
    builder.add(InlineKeyboardButton(text=tasks_text, callback_data="task:list"))
    builder.add(InlineKeyboardButton(text="👤 Персонаж", callback_data="screen:character"))
    builder.add(InlineKeyboardButton(text="📊 Статистика", callback_data="screen:stats"))
    builder.adjust(2, 2)
    return builder.as_markup()


# Back to menu button
def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with back to menu button."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 Меню", callback_data="menu"))
    return builder.as_markup()


# Cancel button
def cancel_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with cancel button."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="task:create_cancel"))
    return builder.as_markup()


# 8.8 Difficulty selection keyboard
def difficulty_keyboard() -> InlineKeyboardMarkup:
    """Difficulty selection keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🟢 Лёгкая (+10 XP)", callback_data="task:diff:easy"))
    builder.add(InlineKeyboardButton(text="🟡 Средняя (+25 XP)", callback_data="task:diff:medium"))
    builder.add(InlineKeyboardButton(text="🔴 Сложная (+50 XP)", callback_data="task:diff:hard"))
    builder.add(InlineKeyboardButton(text="🟣 Эпическая (+100 XP)", callback_data="task:diff:epic"))
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="task:create_cancel"))
    builder.adjust(2, 2, 1)
    return builder.as_markup()


# 8.9 Quick deadline selection keyboard
def deadline_quick_keyboard() -> InlineKeyboardMarkup:
    """Quick deadline selection keyboard."""
    from datetime import datetime, timedelta
    from bot.time_utils import get_quick_deadline_times
    
    times = get_quick_deadline_times()
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Через 1ч", callback_data="task:dl:1h"))
    builder.add(InlineKeyboardButton(text="Через 3ч", callback_data="task:dl:3h"))
    builder.add(InlineKeyboardButton(text=times["today"], callback_data="task:dl:today"))
    builder.add(InlineKeyboardButton(text=times["tomorrow_morning"], callback_data="task:dl:tom_morning"))
    builder.add(InlineKeyboardButton(text=times["tomorrow_evening"], callback_data="task:dl:tom_evening"))
    builder.add(InlineKeyboardButton(text="✏️ Ввести", callback_data="task:dl:custom"))
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="task:create_cancel"))
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()


# Task created keyboard
def task_created_keyboard() -> InlineKeyboardMarkup:
    """Keyboard after task creation."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➕ Ещё задачу", callback_data="task:new"))
    builder.add(InlineKeyboardButton(text="🏠 Меню", callback_data="menu"))
    builder.adjust(2)
    return builder.as_markup()


# 8.5 Task list keyboard
def task_list_keyboard(tasks: list[Task]) -> InlineKeyboardMarkup:
    """Task list keyboard."""
    from bot.time_utils import format_remaining_short
    
    builder = InlineKeyboardBuilder()
    
    for task in tasks:
        remaining = format_remaining_short(task.deadline)
        text = f"📌 {task.title} — {remaining}"
        builder.add(InlineKeyboardButton(text=text, callback_data=f"task:detail:{task.id}"))
    
    builder.add(InlineKeyboardButton(text="⛔ Просроченные", callback_data="task:failed"))
    builder.add(InlineKeyboardButton(text="🏠 Меню", callback_data="menu"))
    
    if tasks:
        builder.adjust(1, 1, 1)  # One task per row, then buttons
    else:
        builder.adjust(1)
    
    return builder.as_markup()


# 8.6 Task detail keyboard
def task_detail_keyboard(task: Task) -> InlineKeyboardMarkup:
    """Task detail keyboard."""
    builder = InlineKeyboardBuilder()
    
    # Show "Done" button only for active tasks
    if task.status == TaskStatus.ACTIVE:
        builder.add(InlineKeyboardButton(text="✅ Выполнено", callback_data=f"task:done:{task.id}"))
    
    builder.add(InlineKeyboardButton(text="🗑 Удалить", callback_data=f"task:del:{task.id}"))
    builder.add(InlineKeyboardButton(text="◀️ К задачам", callback_data="task:list"))
    
    if task.status == TaskStatus.ACTIVE:
        builder.adjust(2, 1)
    else:
        builder.adjust(1, 1)
    
    return builder.as_markup()


# Back to tasks keyboard
def back_to_tasks_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with back to tasks button."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="◀️ К задачам", callback_data="task:list"))
    return builder.as_markup()


# Failed tasks list keyboard
def failed_tasks_keyboard(tasks: list[Task]) -> InlineKeyboardMarkup:
    """Failed tasks list keyboard."""
    builder = InlineKeyboardBuilder()
    
    for task in tasks:
        builder.add(InlineKeyboardButton(text=f"❌ {task.title}", callback_data=f"task:detail:{task.id}"))
    
    builder.add(InlineKeyboardButton(text="◀️ К задачам", callback_data="task:list"))
    
    if tasks:
        builder.adjust(1)
    
    return builder.as_markup()


# Reminder notification keyboard
def reminder_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """Reminder notification keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Выполнено", callback_data=f"task:done:{task_id}"))
    builder.add(InlineKeyboardButton(text="📋 Открыть", callback_data=f"task:detail:{task_id}"))
    builder.adjust(2)
    return builder.as_markup()


# Death notification keyboard
def death_notification_keyboard() -> InlineKeyboardMarkup:
    """Death notification keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 Меню", callback_data="menu"))
    return builder.as_markup()


# Overdue notification keyboard
def overdue_notification_keyboard() -> InlineKeyboardMarkup:
    """Overdue notification keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 Меню", callback_data="menu"))
    return builder.as_markup()


# Task completed keyboard
def task_completed_keyboard() -> InlineKeyboardMarkup:
    """Task completed keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📋 К задачам", callback_data="task:list"))
    builder.add(InlineKeyboardButton(text="🏠 Меню", callback_data="menu"))
    builder.adjust(2)
    return builder.as_markup()


# Level up keyboard
def level_up_keyboard() -> InlineKeyboardMarkup:
    """Level up notification keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 Меню", callback_data="menu"))
    return builder.as_markup()
