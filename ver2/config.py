"""Configuration module for GameTODO Bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Database URL - PostgreSQL for Docker, SQLite for local
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/gametodo")

# Character initial stats (SPEC 2.1)
DEFAULT_LEVEL = 1
DEFAULT_XP = 0
DEFAULT_HP = 100
DEFAULT_MAX_HP = 100

# XP formula: XP for level N = 100 * N (SPEC 2.2)
def xp_required_for_level(level: int) -> int:
    """Calculate XP required to advance from given level to next level."""
    return 100 * level

# Task difficulty constants (SPEC 7.3)
DIFFICULTY_XP = {
    "easy": 10,
    "medium": 25,
    "hard": 50,
    "epic": 100
}

DIFFICULTY_DAMAGE = {
    "easy": 5,
    "medium": 15,
    "hard": 30,
    "epic": 50
}

# Scheduler settings
DEADLINE_CHECK_INTERVAL_MINUTES = 5
