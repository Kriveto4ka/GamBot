"""Text templates for GameTODO Bot (SPEC 8)."""
from database.models import User, Task
from config import xp_required_for_level


def make_progress_bar(current: int, maximum: int, width: int = 10) -> str:
    """Create a visual progress bar."""
    if maximum <= 0:
        return "[" + "░" * width + "] 0%"
    
    filled = int((current / maximum) * width)
    empty = width - filled
    percentage = int((current / maximum) * 100)
    
    return "[" + "█" * filled + "░" * empty + f"] {percentage}%"


# 8.1 Welcome message (first /start)
def welcome_message(user: User) -> str:
    """Welcome message for new users."""
    xp_needed = xp_required_for_level(user.level)
    return f"""🎮 Добро пожаловать в GameTODO!

Управляй задачами — прокачивай персонажа.

⚔️ Выполнил вовремя — получил опыт
💔 Просрочил — получил урон
💀 Ноль здоровья — начинаешь сначала

Твой персонаж создан:
🎖 Уровень: {user.level}
✨ Опыт: {user.xp}/{xp_needed}
❤️ Здоровье: {user.hp}/{user.max_hp}"""


# 8.2 Main menu
def main_menu_message(user: User, active_tasks_count: int = 0) -> str:
    """Main menu message."""
    return f"""🎮 GameTODO

🎖 Уровень {user.level} | ❤️ {user.hp}/{user.max_hp}"""


# 8.3 Character screen
def character_screen_message(user: User, active_tasks_count: int = 0, nearest_deadline: str = "—") -> str:
    """Character screen message."""
    xp_needed = xp_required_for_level(user.level)
    xp_bar = make_progress_bar(user.xp, xp_needed)
    hp_bar = make_progress_bar(user.hp, user.max_hp)
    
    return f"""👤 Твой персонаж

🎖 Уровень: {user.level}
✨ Опыт: {user.xp}/{xp_needed}
{xp_bar}

❤️ Здоровье: {user.hp}/{user.max_hp}
{hp_bar}

📋 Активных задач: {active_tasks_count}
⏰ Ближайший дедлайн: {nearest_deadline}"""


# 8.4 Statistics screen
def statistics_screen_message(user: User) -> str:
    """Statistics screen message."""
    total = user.total_completed + user.total_failed
    success_rate = int((user.total_completed / total) * 100) if total > 0 else 0
    created_date = user.created_at.strftime("%d.%m.%Y") if user.created_at else "—"
    
    return f"""📊 Статистика

✅ Выполнено: {user.total_completed}
❌ Просрочено: {user.total_failed}
📈 Успешность: {success_rate}%

🏆 Макс. уровень: {user.max_level_reached}
📅 С нами с: {created_date}"""


# 8.5 Task list
def task_list_header(count: int) -> str:
    """Task list header."""
    return f"📋 Твои задачи ({count})"


def task_list_empty() -> str:
    """Empty task list message."""
    return "📋 У тебя пока нет активных задач.\n\nНажми «Новая задача» чтобы создать первую!"


# 8.6 Task detail
def task_detail_message(task: Task, remaining: str = "—") -> str:
    """Task detail message."""
    diff_labels = {
        "easy": "Лёгкая",
        "medium": "Средняя", 
        "hard": "Сложная",
        "epic": "Эпическая"
    }
    from config import DIFFICULTY_XP, DIFFICULTY_DAMAGE
    
    diff = task.difficulty.value if hasattr(task.difficulty, 'value') else task.difficulty
    label = diff_labels.get(diff, diff)
    xp = DIFFICULTY_XP.get(diff, 0)
    damage = DIFFICULTY_DAMAGE.get(diff, 0)
    
    return f"""📋 {task.title}

⚡ Сложность: {label} (+{xp} XP)
⏰ Дедлайн: {task.deadline.strftime('%d.%m, %H:%M')}
⏳ Осталось: {remaining}"""


# 8.7-8.9 Task creation steps
def task_create_step1() -> str:
    """Task creation step 1 - enter title."""
    return """➕ Новая задача

Введи название задачи:"""


def task_create_step2(title: str) -> str:
    """Task creation step 2 - select difficulty."""
    return f"""➕ Новая задача

📝 {title}

Выбери сложность:"""


def task_create_step3(title: str, difficulty: str) -> str:
    """Task creation step 3 - select deadline."""
    from config import DIFFICULTY_XP, DIFFICULTY_DAMAGE
    
    diff_labels = {
        "easy": "Лёгкая",
        "medium": "Средняя",
        "hard": "Сложная", 
        "epic": "Эпическая"
    }
    
    xp = DIFFICULTY_XP.get(difficulty, 0)
    damage = DIFFICULTY_DAMAGE.get(difficulty, 0)
    label = diff_labels.get(difficulty, difficulty)
    
    return f"""➕ Новая задача

📝 {title}
⚡ {label} (+{xp} XP / -{damage} HP)

Когда дедлайн?"""


# 8.10 Task created
def task_created_message(task: Task) -> str:
    """Task created confirmation."""
    from config import DIFFICULTY_XP, DIFFICULTY_DAMAGE
    
    diff_labels = {
        "easy": "Лёгкая",
        "medium": "Средняя",
        "hard": "Сложная",
        "epic": "Эпическая"
    }
    
    diff = task.difficulty.value if hasattr(task.difficulty, 'value') else task.difficulty
    xp = DIFFICULTY_XP.get(diff, 0)
    damage = DIFFICULTY_DAMAGE.get(diff, 0)
    label = diff_labels.get(diff, diff)
    
    return f"""✅ Задача создана!

📝 {task.title}
⚡ {label} (+{xp} XP / -{damage} HP)
⏰ Дедлайн: {task.deadline.strftime('%d.%m, %H:%M')}

Удачи! 💪"""


# Task completed
def task_completed_message(user: User, xp_gained: int) -> str:
    """Task completed message."""
    xp_needed = xp_required_for_level(user.level)
    xp_bar = make_progress_bar(user.xp, xp_needed)
    
    return f"""✅ Задача выполнена!

✨ +{xp_gained} XP

🎖 Уровень: {user.level}
✨ Опыт: {user.xp}/{xp_needed}
{xp_bar}"""


# Level up notification (8.14)
def notification_level_up(user: User, new_level: int) -> str:
    """Level up notification."""
    xp_needed = xp_required_for_level(new_level)
    return f"""🎉 Поздравляем! Ты достиг уровня {new_level}!

❤️ HP полностью восстановлено!
✨ Опыт: {user.xp}/{xp_needed}"""


# Overdue notification (8.13)
def notification_task_overdue(task_title: str, damage: int, user: User) -> str:
    """Task overdue notification."""
    hp_bar = make_progress_bar(user.hp, user.max_hp)
    return f"""💀 Задача просрочена!

📝 {task_title}
💔 Получен урон: -{damage} HP

❤️ Здоровье: {user.hp}/{user.max_hp}
{hp_bar}"""


# Death notification (8.15)
def notification_death() -> str:
    """Death notification."""
    return """💀 Твой персонаж погиб!

Прогресс сброшен. Начинаем заново!

🎖 Уровень: 1
✨ Опыт: 0/100
❤️ Здоровье: 100/100"""


# Reminder notification (8.12)
def notification_reminder(task: Task) -> str:
    """Reminder notification - 1 hour before deadline."""
    from config import DIFFICULTY_DAMAGE
    
    diff = task.difficulty.value if hasattr(task.difficulty, 'value') else task.difficulty
    damage = DIFFICULTY_DAMAGE.get(diff, 0)
    
    return f"""⏰ Напоминание!

📝 {task.title}
⏳ Осталось меньше часа!

Не забудь выполнить, иначе -{damage} HP"""


# Error messages
def error_empty_title() -> str:
    return "❌ Название не может быть пустым. Попробуй ещё раз:"


def error_title_truncated(max_len: int = 200) -> str:
    return f"⚠️ Название слишком длинное, обрезано до {max_len} символов."


def error_deadline_past() -> str:
    return "❌ Дедлайн должен быть в будущем. Попробуй ещё раз:"


def error_deadline_invalid() -> str:
    return """❌ Не удалось разобрать дату. Попробуй форматы:
• завтра 18:00
• 25.01 15:30
• через 2 часа"""


def error_task_not_found() -> str:
    return "❌ Задача не найдена или уже удалена."


def task_already_completed() -> str:
    return "✅ Эта задача уже выполнена."


def coming_soon() -> str:
    return "🚧 Скоро будет доступно"


# Failed tasks
def failed_tasks_header(count: int) -> str:
    return f"❌ Просроченные задачи ({count})"


def failed_tasks_empty() -> str:
    return "✅ У тебя нет просроченных задач!"
