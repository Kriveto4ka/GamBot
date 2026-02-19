"""Format deadline and remaining time for display."""
from datetime import datetime, timezone, timedelta


def format_remaining(dt: datetime, now: datetime | None = None) -> str:
    """Human-readable remaining time, e.g. '5ч 23мин', '1д 2ч', '2д'."""
    if now is None:
        now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = dt - now
    if delta.total_seconds() <= 0:
        return "просрочено"
    total_sec = int(delta.total_seconds())
    days = total_sec // 86400
    hours = (total_sec % 86400) // 3600
    minutes = (total_sec % 3600) // 60
    parts = []
    if days:
        parts.append(f"{days}д")
    if hours:
        parts.append(f"{hours}ч")
    if minutes or not parts:
        parts.append(f"{minutes}мин")
    return " ".join(parts)


from bot.deadline_parser import INPUT_TIMEZONE

def format_deadline_date(dt: datetime, now: datetime | None = None) -> str:
    """e.g. '25.01, 18:00' or 'завтра, 18:00'."""
    if now is None:
        now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
        
    # Convert both to local time for display and relative check
    dt_local = dt.astimezone(INPUT_TIMEZONE)
    now_local = now.astimezone(INPUT_TIMEZONE)
    
    today = now_local.date()
    d = dt_local.date()
    
    if d == today:
        return f"сегодня, {dt_local.strftime('%H:%M')}"
    if d == today + timedelta(days=1):
        return f"завтра, {dt_local.strftime('%H:%M')}"
    return dt_local.strftime("%d.%m, %H:%M")
