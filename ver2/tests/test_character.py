"""Tests for character mechanics (Phase 1)."""
import pytest
from config import (
    xp_required_for_level,
    DEFAULT_LEVEL,
    DEFAULT_XP,
    DEFAULT_HP,
    DEFAULT_MAX_HP,
    DIFFICULTY_XP,
    DIFFICULTY_DAMAGE
)
from database.models import User


class TestXPFormula:
    """Tests for XP formula (SPEC 2.2)."""
    
    def test_xp_for_level_1(self):
        """Level 1 to 2 requires 100 XP."""
        assert xp_required_for_level(1) == 100
    
    def test_xp_for_level_2(self):
        """Level 2 to 3 requires 200 XP."""
        assert xp_required_for_level(2) == 200
    
    def test_xp_for_level_5(self):
        """Level 5 to 6 requires 500 XP."""
        assert xp_required_for_level(5) == 500
    
    def test_xp_for_level_10(self):
        """Level 10 to 11 requires 1000 XP."""
        assert xp_required_for_level(10) == 1000


class TestInitialCharacterStats:
    """Tests for initial character stats (SPEC 2.1)."""
    
    def test_default_level(self):
        """Default level is 1."""
        assert DEFAULT_LEVEL == 1
    
    def test_default_xp(self):
        """Default XP is 0."""
        assert DEFAULT_XP == 0
    
    def test_default_hp(self):
        """Default HP is 100."""
        assert DEFAULT_HP == 100
    
    def test_default_max_hp(self):
        """Default max HP is 100."""
        assert DEFAULT_MAX_HP == 100
    
    def test_user_model_defaults(self):
        """User model can be created with default stats."""
        user = User(
            telegram_id=123456789,
            username="test_user",
            level=DEFAULT_LEVEL,
            xp=DEFAULT_XP,
            hp=DEFAULT_HP,
            max_hp=DEFAULT_MAX_HP
        )
        assert user.level == 1
        assert user.xp == 0
        assert user.hp == 100
        assert user.max_hp == 100


class TestDifficultyConstants:
    """Tests for difficulty constants (SPEC 7.3)."""
    
    def test_easy_xp(self):
        """Easy difficulty gives 10 XP."""
        assert DIFFICULTY_XP["easy"] == 10
    
    def test_easy_damage(self):
        """Easy difficulty deals 5 damage."""
        assert DIFFICULTY_DAMAGE["easy"] == 5
    
    def test_medium_xp(self):
        """Medium difficulty gives 25 XP."""
        assert DIFFICULTY_XP["medium"] == 25
    
    def test_medium_damage(self):
        """Medium difficulty deals 15 damage."""
        assert DIFFICULTY_DAMAGE["medium"] == 15
    
    def test_hard_xp(self):
        """Hard difficulty gives 50 XP."""
        assert DIFFICULTY_XP["hard"] == 50
    
    def test_hard_damage(self):
        """Hard difficulty deals 30 damage."""
        assert DIFFICULTY_DAMAGE["hard"] == 30
    
    def test_epic_xp(self):
        """Epic difficulty gives 100 XP."""
        assert DIFFICULTY_XP["epic"] == 100
    
    def test_epic_damage(self):
        """Epic difficulty deals 50 damage."""
        assert DIFFICULTY_DAMAGE["epic"] == 50


class TestProgressBar:
    """Tests for progress bar generation."""
    
    def test_progress_bar_full(self):
        """Progress bar at 100%."""
        from bot.texts import make_progress_bar
        bar = make_progress_bar(100, 100)
        assert "100%" in bar
        assert "█" in bar
    
    def test_progress_bar_half(self):
        """Progress bar at 50%."""
        from bot.texts import make_progress_bar
        bar = make_progress_bar(50, 100)
        assert "50%" in bar
    
    def test_progress_bar_zero(self):
        """Progress bar at 0%."""
        from bot.texts import make_progress_bar
        bar = make_progress_bar(0, 100)
        assert "0%" in bar
    
    def test_progress_bar_empty_max(self):
        """Progress bar with max 0."""
        from bot.texts import make_progress_bar
        bar = make_progress_bar(0, 0)
        assert "0%" in bar
