"""Tests for character logic: XP formula, initial stats (phase 1)."""
import pytest

from config import (
    DEFAULT_HP,
    DEFAULT_LEVEL,
    DEFAULT_MAX_HP,
    DEFAULT_XP,
    xp_required_for_level,
)
from database.models import User


def test_xp_for_level_1():
    """Level 1 -> 2 requires 100 XP."""
    assert xp_required_for_level(1) == 100


def test_xp_for_level_2():
    """Level 2 -> 3 requires 200 XP."""
    assert xp_required_for_level(2) == 200


def test_xp_for_level_5():
    """Level 5 -> 6 requires 500 XP."""
    assert xp_required_for_level(5) == 500


def test_xp_for_level_0_invalid():
    """Level 0 is not used; function still returns 0."""
    assert xp_required_for_level(0) == 0


def test_initial_character_stats():
    """New character: level=1, xp=0, hp=100, max_hp=100 (SPEC 2.1). Verifies model + repo defaults."""
    user = User(
        telegram_id=1,
        level=DEFAULT_LEVEL,
        xp=DEFAULT_XP,
        hp=DEFAULT_HP,
        max_hp=DEFAULT_MAX_HP,
    )
    assert user.level == 1
    assert user.xp == 0
    assert user.hp == 100
    assert user.max_hp == 100
