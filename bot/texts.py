"""Message texts (SPEC 8)."""
from config import xp_required_for_level
from database.models import Task, User

from bot.constants import format_difficulty_short
from bot.time_utils import format_deadline_date, format_remaining


def welcome_message(user: User) -> str:
    """8.1 — First /start welcome."""
    return (
        "🎮 Добро пожаловать в GameTODO!\n\n"
        "Управляй задачами — прокачивай персонажа.\n\n"
        "⚔️ Выполнил вовремя — получил опыт\n"
        "💔 Просрочил — получил урон\n"
        "💀 Ноль здоровья — начинаешь сначала\n\n"
        "Твой персонаж создан:\n"
        f"🎖 Уровень: {user.level}\n"
        f"✨ Опыт: {user.xp}/{xp_required_for_level(user.level)}\n"
        f"❤️ Здоровье: {user.hp}/{user.max_hp}\n\n"
    )


def main_menu_message(user: User, active_tasks_count: int = 0) -> str:
    """8.2 — Main menu."""
    lines = [
        "🎮 GameTODO\n",
        f"🎖 Уровень {user.level} | ❤️ {user.hp}/{user.max_hp}\n",
    ]
    return "".join(lines)


def character_screen_message(user: User, active_tasks_count: int = 0, next_deadline_text: str = "—") -> str:
    """8.3 — Character screen."""
    xp_needed = xp_required_for_level(user.level)
    xp_pct = (user.xp / xp_needed * 100) if xp_needed else 0
    hp_pct = (user.hp / user.max_hp * 100) if user.max_hp else 0

    def bar(pct: float) -> str:
        filled = int(pct / 10)
        return "█" * filled + "░" * (10 - filled)

    return (
        "👤 Твой персонаж\n\n"
        f"🎖 Уровень: {user.level}\n"
        f"✨ Опыт: {user.xp}/{xp_needed}\n"
        f"[{bar(xp_pct)}] {int(xp_pct)}%\n\n"
        f"❤️ Здоровье: {user.hp}/{user.max_hp}\n"
        f"[{bar(hp_pct)}] {int(hp_pct)}%\n\n"
        f"📋 Активных задач: {active_tasks_count}\n"
        f"⏰ Ближайший дедлайн: {next_deadline_text}\n\n"
    )


def soon_stub() -> str:
    """Placeholder for not-yet-implemented screens."""
    return "⏳ Скоро будет доступно. Возвращайтесь в меню."


def statistics_screen_message(user: User) -> str:
    """8.4 — Statistics screen."""
    total_tasks = user.total_completed + user.total_failed
    success_rate = int((user.total_completed / total_tasks * 100)) if total_tasks > 0 else 0
    
    # Format registration date
    reg_date = user.created_at.strftime("%d.%m.%Y")
    
    return (
        "📊 Статистика\n\n"
        f"✅ Выполнено: {user.total_completed}\n"
        f"❌ Просрочено: {user.total_failed}\n"
        f"📈 Успешность: {success_rate}%\n\n"
        f"🏆 Макс. уровень: {user.max_level_reached}\n"
        f"📅 С нами с: {reg_date}\n\n"
    )


# --- Phase 2: tasks (8.5–8.10) ---

def task_list_header(active_count: int) -> str:
    """8.5 — List tasks header."""
    return f"📋 Твои задачи ({active_count})\n\n"


def task_list_empty() -> str:
    """E7 — No active tasks."""
    return "📋 У тебя пока нет активных задач.\n\nСоздай первую кнопкой «Новая задача»."


def task_detail_message(task: Task) -> str:
    """8.6 — Task detail."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    return (
        f"📋 {task.title}\n\n"
        f"⚡ Сложность: {format_difficulty_short(task.difficulty)}\n"
        f"⏰ Дедлайн: {format_deadline_date(task.deadline, now)}\n"
        f"⏳ Осталось: {format_remaining(task.deadline, now)}\n\n"
    )


def task_created_message(task: Task) -> str:
    """8.10 — Task created."""
    return (
        "✅ Задача создана!\n\n"
        f"📝 {task.title}\n"
        f"⚡ {format_difficulty_short(task.difficulty)}\n"
        f"⏰ Дедлайн: {format_deadline_date(task.deadline)}\n\n"
        "Удачи! 💪\n\n"
    )


def task_completed_message_phase2(task: Task) -> str:
    """Phase 2: task completed (no XP yet)."""
    return f"✅ Задача «{task.title}» отмечена выполненной.\n\n(Опыт будет начисляться в следующем обновлении.)"


def create_task_step1_title() -> str:
    """8.7 — Step 1."""
    return "➕ Новая задача\n\nВведи название задачи:\n\n"


def create_task_step2_difficulty(title: str) -> str:
    """8.8 — Step 2."""
    return f"➕ Новая задача\n\n📝 {title}\n\nВыбери сложность:\n\n"


def create_task_step3_deadline(title: str, difficulty_label: str) -> str:
    """8.9 — Step 3."""
    return f"➕ Новая задача\n\n📝 {title}\n⚡ {difficulty_label}\n\nКогда дедлайн?\n\n"


def error_empty_title() -> str:
    """E2."""
    return "❌ Название не может быть пустым. Введи текст задачи."


def error_title_truncated() -> str:
    """E3 — notify after truncation."""
    return "⚠️ Название обрезано до 200 символов."


def error_deadline_past() -> str:
    """E1."""
    return "❌ Дедлайн должен быть в будущем. Введи другую дату или время."


def error_deadline_invalid() -> str:
    """E4."""
    from bot.deadline_parser import format_deadline_examples
    return f"❌ Не удалось разобрать дату.\n\n{format_deadline_examples()}"


def error_task_not_found() -> str:
    """E6."""
    return "❌ Задача не найдена или уже удалена."


def task_already_completed() -> str:
    """Задача уже отмечена выполненной."""
    return "✅ Задача уже выполнена."


def failed_tasks_header(count: int) -> str:
    """R5 — List failed tasks."""
    return f"⛔ Просроченные задачи ({count})\n\n"


def failed_tasks_empty() -> str:
    return "⛔ Нет просроченных задач."


def notification_reminder(title: str, task_id: int, damage: int) -> str:
    """8.12 — 1-hour reminder."""
    return (
        "⏰ Напоминание!\n\n"
        f"📝 {title}\n"
        "⏳ Осталось меньше часа!\n\n"
        f"Не забудь выполнить, иначе -{damage} HP\n\n"
    )


def notification_task_overdue(title: str, damage: int, hp: int, max_hp: int) -> str:
    """8.13 — Overdue notification."""
    hp_pct = (hp / max_hp * 100) if max_hp else 0
    filled = int(hp_pct / 10)
    bar = "█" * filled + "░" * (10 - filled)
    
    return (
        "⚠️ Задача просрочена!\n\n"
        f"📝 {title}\n"
        f"💔 -{damage} HP\n\n"
        f"❤️ Здоровье: {hp}/{max_hp} [{bar}] {int(hp_pct)}%\n\n"
    )


def notification_death(title: str, damage: int) -> str:
    """8.15 — Death notification."""
    return (
        "💀 Твой персонаж погиб!\n\n"
        f"Задача «{title}» нанесла {damage} урона.\n"
        "Здоровье упало до нуля.\n"
        "Прогресс сброшен.\n\n"
        "🔄 Заново:\n"
        "🎖 Уровень: 1\n"
        "✨ Опыт: 0/100\n"
        "❤️ Здоровье: 100/100\n\n"
        "Все задачи удалены.\n\n"
    )


def notification_level_up(level: int, hp: int, max_hp: int, xp_next: int) -> str:
    """8.14 — Level up."""
    return (
        "🎉 Уровень повышен!\n\n"
        f"🎖 Новый уровень: {level}\n"
        f"❤️ Здоровье восстановлено: {hp}/{max_hp}\n"
        f"✨ До следующего: 0/{xp_next}\n\n"
        "Так держать! 💪\n\n"
    )


def task_completed_message(task: Task, xp_reward: int, user: User, level_up: bool) -> str:
    """8.11 — Task completed with XP."""
    xp_needed = xp_required_for_level(user.level)
    xp_pct = (user.xp / xp_needed * 100) if xp_needed else 0
    filled = int(xp_pct / 10)
    bar = "█" * filled + "░" * (10 - filled)

    msg = (
        "🎉 Задача выполнена!\n\n"
        f"📝 {task.title}\n"
        f"✨ +{xp_reward} XP\n\n"
        f"🎖 Уровень: {user.level}\n"
        f"✨ Опыт: {user.xp}/{xp_needed} [{bar}] {int(xp_pct)}%\n\n"
    )
    if level_up:
        msg += "🚀 УРОВЕНЬ ПОВЫШЕН! (Проверь статус)\n\n"
        
    return msg
