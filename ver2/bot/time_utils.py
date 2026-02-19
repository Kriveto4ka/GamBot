"""Time utilities for GameTODO Bot."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Default timezone for user input (Moscow time, UTC+3)
INPUT_TIMEZONE = ZoneInfo("Europe/Moscow")
UTC_TIMEZONE = ZoneInfo("UTC")


def get_now_utc() -> datetime:
    """Get current UTC time."""
    return datetime.now(UTC_TIMEZONE)


def get_now_local() -> datetime:
    """Get current local time (Moscow)."""
    return datetime.now(INPUT_TIMEZONE)


def format_remaining(deadline: datetime) -> str:
    """Format remaining time until deadline."""
    # Use naive UTC for comparison with DB timestamps
    now = datetime.utcnow()
    
    if deadline <= now:
        return "просрочено"
    
    diff = deadline - now
    
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}д")
    if hours > 0:
        parts.append(f"{hours}ч")
    if minutes > 0 and days == 0:
        parts.append(f"{minutes}мин")
    
    if not parts:
        return "менее минуты"
    
    return " ".join(parts)


def format_remaining_short(deadline: datetime) -> str:
    """Format remaining time in short format for task list."""
    # Use naive UTC for comparison with DB timestamps
    now = datetime.utcnow()
    
    if deadline <= now:
        return "просрочено"
    
    diff = deadline - now
    
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}д {hours}ч"
    elif hours > 0:
        return f"{hours}ч {minutes}мин"
    else:
        return f"{minutes}мин"


def format_deadline_date(deadline: datetime) -> str:
    """Format deadline date for display."""
    # DB stores naive UTC, make it aware before converting
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=UTC_TIMEZONE)
    
    # Convert UTC to local timezone for display
    local_deadline = deadline.astimezone(INPUT_TIMEZONE)
    local_now = get_now_local()
    
    # Format based on relative date
    if local_deadline.date() == local_now.date():
        return f"сегодня, {local_deadline.strftime('%H:%M')}"
    elif local_deadline.date() == local_now.date() + timedelta(days=1):
        return f"завтра, {local_deadline.strftime('%H:%M')}"
    else:
        return local_deadline.strftime('%d.%m, %H:%M')


def get_quick_deadline_times() -> dict:
    """Get quick deadline button texts with actual times."""
    now = get_now_local()
    
    # Today at 21:00
    today_evening = now.replace(hour=21, minute=0, second=0, microsecond=0)
    if today_evening <= now:
        today_evening += timedelta(days=1)
    
    # Tomorrow at 10:00
    tomorrow_morning = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    
    # Tomorrow at 18:00
    tomorrow_evening = (now + timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
    
    return {
        "today": f"Сегодня {today_evening.strftime('%H:%M')}",
        "tomorrow_morning": f"Завтра {tomorrow_morning.strftime('%H:%M')}",
        "tomorrow_evening": f"Завтра {tomorrow_evening.strftime('%H:%M')}"
    }
