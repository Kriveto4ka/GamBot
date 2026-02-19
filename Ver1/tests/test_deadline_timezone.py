import unittest
from datetime import datetime, timedelta, timezone
from bot.deadline_parser import parse_deadline

class TestDeadlineTimezone(unittest.TestCase):
    def test_absolute_time_parsing(self):
        # Emulate "now" as 2026-02-17 00:34:00 UTC+3 (Moscow)
        # In UTC, this is 2026-02-16 21:34:00
        moscow_tz = timezone(timedelta(hours=3))
        now_local = datetime(2026, 2, 17, 0, 34, 0, tzinfo=moscow_tz)
        now_utc = now_local.astimezone(timezone.utc)
        
        # User input: "17.02 00:34" (intending local time)
        input_text = "17.02 00:34"
        
        # Parse
        deadline = parse_deadline(input_text, now_utc)
        
        # Expectation: Deadline should be equal to now_utc (21:34 UTC previous day)
        # Actual (Bug): It parses as 00:34 UTC (equal to 03:34 MSK), which is 3 hours later.
        
        print(f"\nUser Input: {input_text}")
        print(f"Now (Local): {now_local}")
        print(f"Now (UTC):   {now_utc}")
        print(f"Parsed (UTC): {deadline}")
        
        if deadline:
             print(f"Parsed (Local): {deadline.astimezone(moscow_tz)}")
        
        # Assert that parsed deadline matches the intended local time converted to UTC
        # If bug exists, deadline will be 00:34 UTC, which is != 21:34 UTC
        self.assertEqual(deadline, now_utc, "Deadline should match 'now' if input string matches 'now' local time")

if __name__ == '__main__':
    unittest.main()
