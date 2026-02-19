"""Game logic for GameTODO Bot."""
from database.models import User
from config import xp_required_for_level


def add_xp(user: User, xp_amount: int) -> tuple[int, int, list[int]]:
    """
    Add XP to user and handle level ups.
    
    Args:
        user: User model instance
        xp_amount: XP to add
    
    Returns:
        tuple: (new_xp, new_max_hp, list_of_new_levels)
    """
    new_xp = user.xp + xp_amount
    new_level = user.level
    new_max_hp = user.max_hp
    level_ups = []
    
    while True:
        xp_needed = xp_required_for_level(new_level)
        if new_xp >= xp_needed:
            # Level up!
            new_xp -= xp_needed
            new_level += 1
            new_max_hp += 10
            level_ups.append(new_level)
        else:
            break
    
    return new_xp, new_max_hp, level_ups


def apply_damage(user: User, damage: int) -> tuple[int, bool]:
    """
    Apply damage to user and check for death.
    
    Args:
        user: User model instance
        damage: Damage amount
    
    Returns:
        tuple: (new_hp, is_dead)
    """
    new_hp = user.hp - damage
    is_dead = new_hp <= 0
    
    return new_hp, is_dead


def reset_character(user: User) -> None:
    """
    Reset character after death (SPEC 2.5).
    
    Sets:
    - Level to 1
    - XP to 0
    - HP to 100
    - Max HP to 100
    """
    user.level = 1
    user.xp = 0
    user.hp = 100
    user.max_hp = 100
