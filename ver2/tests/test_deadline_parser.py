"""Tests for deadline parser (Phase 2)."""
import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from bot.deadline_parser import parse_deadline, is_future, get_now_local

INPUT_TIMEZONE = ZoneInfo("Europe/Moscow")


class TestParseDeadline:
    """Tests for deadline parsing (SPEC R20)."""
    
    def test_parse_relative_hours(self):
        """Parse 'через 2 часа'."""
        now = datetime.now(INPUT_TIMEZONE)
        result = parse_deadline("через 2 часа", now)
        assert result is not None
        # Result should be approximately 2 hours from now
        expected = now + timedelta(hours=2)
        # Allow 1 minute tolerance for test execution
        diff = abs((result.astimezone(INPUT_TIMEZONE) - expected).total_seconds())
        assert diff < 60
    
    def test_parse_relative_days(self):
        """Parse 'через 1 день'."""
        now = datetime.now(INPUT_TIMEZONE)
        result = parse_deadline("через 1 день", now)
        assert result is not None
        expected = now + timedelta(days=1)
        diff = abs((result.astimezone(INPUT_TIMEZONE) - expected).total_seconds())
        assert diff < 60
    
    def test_parse_relative_days_variant(self):
        """Parse 'через 2 дня'."""
        now = datetime.now(INPUT_TIMEZONE)
        result = parse_deadline("через 2 дня", now)
        assert result is not None
        expected = now + timedelta(days=2)
        diff = abs((result.astimezone(INPUT_TIMEZONE) - expected).total_seconds())
        assert diff < 60
    
    def test_parse_tomorrow_time(self):
        """Parse 'завтра 18:00'."""
        now = datetime(2025, 1, 15, 10, 0, tzinfo=INPUT_TIMEZONE)
        result = parse_deadline("завтра 18:00", now)
        assert result is not None
        local_result = result.astimezone(INPUT_TIMEZONE)
        assert local_result.hour == 18
        assert local_result.minute == 0
        assert local_result.day == 16
    
    def test_parse_today_time(self):
        """Parse 'сегодня 21:00'."""
        now = datetime(2025, 1, 15, 10, 0, tzinfo=INPUT_TIMEZONE)
        result = parse_deadline("сегодня 21:00", now)
        assert result is not None
        local_result = result.astimezone(INPUT_TIMEZONE)
        assert local_result.hour == 21
        assert local_result.minute == 0
        assert local_result.day == 15
    
    def test_parse_date_time(self):
        """Parse '25.01 15:30'."""
        now = datetime(2025, 1, 15, 10, 0, tzinfo=INPUT_TIMEZONE)
        result = parse_deadline("25.01 15:30", now)
        assert result is not None
        local_result = result.astimezone(INPUT_TIMEZONE)
        assert local_result.day == 25
        assert local_result.month == 1
        assert local_result.hour == 15
        assert local_result.minute == 30
    
    def test_parse_full_date_time(self):
        """Parse '25.01.2025 15:30'."""
        now = datetime(2025, 1, 15, 10, 0, tzinfo=INPUT_TIMEZONE)
        result = parse_deadline("25.01.2025 15:30", now)
        assert result is not None
        local_result = result.astimezone(INPUT_TIMEZONE)
        assert local_result.day == 25
        assert local_result.month == 1
        assert local_result.year == 2025
        assert local_result.hour == 15
        assert local_result.minute == 30
    
    def test_parse_invalid(self):
        """Parse invalid input returns None."""
        result = parse_deadline("абракадабра")
        assert result is None


class TestIsFuture:
    """Tests for future date checking."""
    
    def test_is_future_true(self):
        """Future date returns True."""
        now = get_now_local()
        future = now + timedelta(hours=1)
        assert is_future(future, now) is True
    
    def test_is_future_false(self):
        """Past date returns False."""
        now = get_now_local()
        past = now - timedelta(hours=1)
        assert is_future(past, now) is False
    
    def test_is_future_now(self):
        """Current time returns False."""
        now = get_now_local()
        assert is_future(now, now) is False
