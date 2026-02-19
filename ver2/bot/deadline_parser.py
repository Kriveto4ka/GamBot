"""Deadline parser for GameTODO Bot (SPEC R20)."""
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Default timezone for user input (Moscow time, UTC+3)
INPUT_TIMEZONE = ZoneInfo("Europe/Moscow")
UTC_TIMEZONE = ZoneInfo("UTC")

# Maximum title length
TITLE_MAX_LEN = 200


def get_now_local() -> datetime:
    """Get current local time (Moscow)."""
    return datetime.now(INPUT_TIMEZONE)


def parse_deadline(text: str, now: datetime = None) -> datetime | None:
    """
    Parse deadline from text input.
    
    Supported formats (SPEC R20):
    - "завтра 18:00"
    - "сегодня 21:00"
    - "25.01 15:30"
    - "25.01.2025 15:30"
    - "через 2 часа"
    - "через 1 день"
    
    Args:
        text: Input text
        now: Current time (defaults to local now)
    
    Returns:
        datetime in UTC or None if parsing failed
    """
    if now is None:
        now = get_now_local()
    
    text = text.strip().lower()
    
    # "через N час(а/ов)"
    match = re.search(r'через\s+(\d+)\s+час', text)
    if match:
        hours = int(match.group(1))
        result = now + timedelta(hours=hours)
        return result.astimezone(UTC_TIMEZONE)
    
    # "через N дн(я/ей/ень)" or "через N день"
    match = re.search(r'через\s+(\d+)\s+(дн|день)', text)
    if match:
        days = int(match.group(1))
        result = now + timedelta(days=days)
        return result.astimezone(UTC_TIMEZONE)
    
    # "завтра HH:MM"
    match = re.search(r'завтра\s+(\d{1,2}):(\d{2})', text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        tomorrow = now + timedelta(days=1)
        result = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return result.astimezone(UTC_TIMEZONE)
    
    # "сегодня HH:MM"
    match = re.search(r'сегодня\s+(\d{1,2}):(\d{2})', text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        result = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return result.astimezone(UTC_TIMEZONE)
    
    # "DD.MM.YYYY HH:MM" or "DD.MM.YYYY HH:MM"
    match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}):(\d{2})', text)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        hour = int(match.group(4))
        minute = int(match.group(5))
        try:
            result = datetime(year, month, day, hour, minute, tzinfo=INPUT_TIMEZONE)
            return result.astimezone(UTC_TIMEZONE)
        except ValueError:
            return None
    
    # "DD.MM HH:MM"
    match = re.search(r'(\d{1,2})\.(\d{1,2})\s+(\d{1,2}):(\d{2})', text)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        hour = int(match.group(3))
        minute = int(match.group(4))
        year = now.year
        try:
            result = datetime(year, month, day, hour, minute, tzinfo=INPUT_TIMEZONE)
            # If date is in the past, assume next year
            if result < now:
                result = datetime(year + 1, month, day, hour, minute, tzinfo=INPUT_TIMEZONE)
            return result.astimezone(UTC_TIMEZONE)
        except ValueError:
            return None
    
    return None


def is_future(dt: datetime, now: datetime = None) -> bool:
    """Check if datetime is in the future."""
    if now is None:
        now = get_now_local()
    
    # Convert to local for comparison if needed
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TIMEZONE)
    local_dt = dt.astimezone(INPUT_TIMEZONE)
    
    return local_dt > now


def format_deadline_examples() -> str:
    """Return examples of valid deadline formats."""
    return """Примеры:
• завтра 18:00
• сегодня 21:00
• 25.01 15:30
• 25.01.2025 15:30
• через 2 часа
• через 1 день"""
