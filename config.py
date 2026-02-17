"""Configuration from environment."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

BOT_TOKEN = os.environ.get("BOT_TOKEN")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://gametodo:gametodo@localhost:5432/gametodo",
)

# Character defaults (SPEC 2.1)
DEFAULT_LEVEL = 1
DEFAULT_XP = 0
DEFAULT_HP = 100
DEFAULT_MAX_HP = 100

# XP for next level: 100 * N (SPEC 2.2)
def xp_required_for_level(level: int) -> int:
    """XP required to reach next level from current level."""
    return 100 * level
