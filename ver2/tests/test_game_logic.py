"""Tests for game logic (Phase 3)."""
import pytest
from database.models import User
from bot.logic.game import add_xp, apply_damage, reset_character
from config import xp_required_for_level


class TestAddXP:
    """Tests for XP addition and level up logic."""
    
    def test_add_xp_simple(self):
        """Add XP without level up."""
        user = User(telegram_id=1, level=1, xp=0, hp=100, max_hp=100)
        new_xp, new_max_hp, level_ups = add_xp(user, 50)
        assert new_xp == 50
        assert new_max_hp == 100
        assert len(level_ups) == 0
    
    def test_add_xp_level_up(self):
        """Add XP causing level up."""
        user = User(telegram_id=1, level=1, xp=50, hp=100, max_hp=100)
        new_xp, new_max_hp, level_ups = add_xp(user, 60)  # 50 + 60 = 110, need 100 for level 2
        assert new_xp == 10  # 110 - 100 = 10
        assert new_max_hp == 110  # +10 for level up
        assert len(level_ups) == 1
        assert level_ups[0] == 2
    
    def test_add_xp_multiple_level_ups(self):
        """Add XP causing multiple level ups (E12)."""
        user = User(telegram_id=1, level=1, xp=0, hp=100, max_hp=100)
        # 100 for level 2, 200 for level 3 = 300 XP needed
        new_xp, new_max_hp, level_ups = add_xp(user, 350)
        assert new_xp == 50  # 350 - 300 = 50
        assert new_max_hp == 120  # +10 for each level up
        assert len(level_ups) == 2
        assert level_ups == [2, 3]
    
    def test_add_xp_exact_threshold(self):
        """Add XP exactly at threshold (E13)."""
        user = User(telegram_id=1, level=1, xp=0, hp=100, max_hp=100)
        new_xp, new_max_hp, level_ups = add_xp(user, 100)
        assert new_xp == 0  # Exactly at threshold
        assert new_max_hp == 110
        assert len(level_ups) == 1


class TestApplyDamage:
    """Tests for damage application."""
    
    def test_apply_damage_simple(self):
        """Apply simple damage."""
        user = User(telegram_id=1, level=1, xp=0, hp=100, max_hp=100)
        new_hp, is_dead = apply_damage(user, 30)
        assert new_hp == 70
        assert is_dead is False
    
    def test_apply_damage_death(self):
        """Apply damage causing death (E8)."""
        user = User(telegram_id=1, level=1, xp=0, hp=20, max_hp=100)
        new_hp, is_dead = apply_damage(user, 30)
        assert new_hp == -10
        assert is_dead is True
    
    def test_apply_damage_exact_zero(self):
        """Apply damage leaving exactly 0 HP."""
        user = User(telegram_id=1, level=1, xp=0, hp=30, max_hp=100)
        new_hp, is_dead = apply_damage(user, 30)
        assert new_hp == 0
        assert is_dead is True


class TestResetCharacter:
    """Tests for character reset on death."""
    
    def test_reset_character(self):
        """Reset character to initial state."""
        user = User(
            telegram_id=1,
            level=5,
            xp=200,
            hp=50,
            max_hp=140
        )
        reset_character(user)
        assert user.level == 1
        assert user.xp == 0
        assert user.hp == 100
        assert user.max_hp == 100
