"""Parse user deadline input (SPEC R20, E1, E4). All times in UTC."""
import re
from datetime import datetime, timedelta, timezone

# Max title length SPEC
TITLE_MAX_LEN = 200

# Quick deadline presets (decisions.md: explicit times)
# "Через 1ч", "Через 3ч", "Сегодня 21:00", "Завтра 10:00", "Завтра 18:00", "Ввести"
# We use UTC; "today" / "tomorrow" are relative to now(UTC).


# Default input timezone (Moscow)
INPUT_TIMEZONE = timezone(timedelta(hours=3))


def parse_deadline(text: str, now: datetime | None = None) -> datetime | None:
    """
    Parse deadline string. Returns datetime in UTC or None if invalid.
    Supports: "завтра 18:00", "25.01 15:30", "25.01.2025 15:30", "через 2 часа", "через 1 день".
    """
    if now is None:
        now = datetime.now(timezone.utc)
    
    # Convert 'now' to local time for relative date calculations (today/tomorrow)
    now_local = now.astimezone(INPUT_TIMEZONE)
    
    text = (text or "").strip().lower()
    if not text:
        return None

    # Relative: "через N час/часа/часов", "через N день/дня/дней"
    m = re.match(r"через\s+(\d+)\s+(час|часа|часов|часов)", text)
    if m:
        h = int(m.group(1))
        return now + timedelta(hours=h)
    m = re.match(r"через\s+(\d+)\s+(день|дня|дней)", text)
    if m:
        d = int(m.group(1))
        return now + timedelta(days=d)
    m = re.match(r"через\s+(\d+)\s+ч", text)
    if m:
        return now + timedelta(hours=int(m.group(1)))
    m = re.match(r"через\s+(\d+)\s+д", text)
    if m:
        return now + timedelta(days=int(m.group(1)))

    # "завтра 18:00" / "завтра 18:00"
    m = re.match(r"завтра\s+(\d{1,2}):(\d{2})", text)
    if m:
        hour, minute = int(m.group(1)), int(m.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            day = (now_local.date() + timedelta(days=1))
            dt_local = datetime(day.year, day.month, day.day, hour, minute, 0, tzinfo=INPUT_TIMEZONE)
            return dt_local.astimezone(timezone.utc)
        return None

    # "сегодня 21:00"
    m = re.match(r"сегодня\s+(\d{1,2}):(\d{2})", text)
    if m:
        hour, minute = int(m.group(1)), int(m.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            d = now_local.date()
            dt_local = datetime(d.year, d.month, d.day, hour, minute, 0, tzinfo=INPUT_TIMEZONE)
            return dt_local.astimezone(timezone.utc)
        return None

    # "25.01 15:30" or "25.01.2025 15:30"
    m = re.match(r"(\d{1,2})\.(\d{1,2})(?:\.(\d{4}))?\s+(\d{1,2}):(\d{2})", text)
    if m:
        day, month = int(m.group(1)), int(m.group(2))
        year = int(m.group(3)) if m.group(3) else now_local.year
        hour, minute = int(m.group(4)), int(m.group(5))
        if 1 <= month <= 12 and 1 <= day <= 31 and 0 <= hour <= 23 and 0 <= minute <= 59:
            try:
                # Interpret as local time
                dt_local = datetime(year, month, day, hour, minute, 0, tzinfo=INPUT_TIMEZONE)
                return dt_local.astimezone(timezone.utc)
            except ValueError:
                return None
        return None

    return None


def is_future(dt: datetime | None, now: datetime | None = None) -> bool:
    """E1: deadline must be in the future."""
    if dt is None:
        return False
    if now is None:
        now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt > now


def format_deadline_examples() -> str:
    """E4: examples for invalid date."""
    return (
        "Примеры: завтра 18:00, 25.01 15:30, 25.01.2025 15:30, через 2 часа, через 1 день."
    )
