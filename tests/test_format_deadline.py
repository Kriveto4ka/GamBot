import unittest
from datetime import datetime, timedelta, timezone
from bot.time_utils import format_deadline_date
from bot.deadline_parser import INPUT_TIMEZONE

class TestFormatDeadline(unittest.TestCase):
    def test_format_deadline_timezone(self):
        # Current time: 12:00 UTC
        now_utc = datetime(2026, 2, 17, 12, 0, 0, tzinfo=timezone.utc)
        
        # User deadline: 15:00 UTC+3 (Moscow) -> 12:00 UTC
        # Let's say deadline is 18:00 UTC+3 -> 15:00 UTC
        deadline_local = datetime(2026, 2, 17, 18, 0, 0, tzinfo=INPUT_TIMEZONE)
        deadline_utc = deadline_local.astimezone(timezone.utc)
        
        # We expect the output to be "сегодня, 18:00" (Local time)
        # Verify what format_deadline_date returns
        result = format_deadline_date(deadline_utc, now_utc)
        
        print(f"Now (UTC): {now_utc}")
        print(f"Deadline (UTC): {deadline_utc}")
        print(f"Deadline (Local): {deadline_local}")
        print(f"Result: {result}")
        
        self.assertIn("18:00", result, f"Expected 18:00 in output, got {result}")

if __name__ == '__main__':
    unittest.main()
