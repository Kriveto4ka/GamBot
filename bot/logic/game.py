"""Game mechanics: XP, Leveling, Damage (SPEC 2)."""
from database.models import User, TaskDifficulty


def get_xp_for_next_level(level: int) -> int:
    """SPEC 2.2: XP for level N = 100 * N."""
    return 100 * level


def get_xp_reward(difficulty: str) -> int:
    """SPEC 2.3."""
    rewards = {
        TaskDifficulty.EASY: 10,
        TaskDifficulty.MEDIUM: 25,
        TaskDifficulty.HARD: 50,
        TaskDifficulty.EPIC: 100,
    }
    return rewards.get(difficulty, 10)


def get_damage_penalty(difficulty: str) -> int:
    """SPEC 2.3."""
    penalties = {
        TaskDifficulty.EASY: 5,
        TaskDifficulty.MEDIUM: 15,
        TaskDifficulty.HARD: 30,
        TaskDifficulty.EPIC: 50,
    }
    return penalties.get(difficulty, 5)


def add_xp(user: User, amount: int) -> bool:
    """
    Add XP to user. Handle level up.
    Returns True if level up occurred.
    SPEC 2.2, 5.4.
    """
    user.xp += amount
    level_up = False
    
    # Loop to handle multiple level ups (E12)
    while True:
        needed = get_xp_for_next_level(user.level)
        if user.xp >= needed:
            # Level up!
            user.xp -= needed
            user.level += 1
            user.max_hp += 10
            user.hp = user.max_hp  # Restore full HP
            user.max_level_reached = max(user.max_level_reached, user.level)
            level_up = True
        else:
            break
            
    return level_up


def apply_damage(user: User, amount: int) -> bool:
    """
    Apply damage to user. Handle death.
    Returns True if user died.
    SPEC 2.4, 2.5, 5.3.
    """
    user.hp -= amount
    if user.hp <= 0:
        reset_character(user)
        return True
    return False


def reset_character(user: User) -> None:
    """
    Reset character on death.
    SPEC 2.5.
    """
    user.level = 1
    user.xp = 0
    user.hp = 100
    user.max_hp = 100
    # Note: Tasks deletion should be handled by the caller or a separate repo function
