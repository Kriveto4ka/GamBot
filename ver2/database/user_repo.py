"""User repository for database operations."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from config import DEFAULT_LEVEL, DEFAULT_XP, DEFAULT_HP, DEFAULT_MAX_HP


async def get_or_create_user(session: AsyncSession, telegram_id: int, username: str = None) -> tuple[User, bool]:
    """
    Get existing user or create new one.
    
    Returns:
        tuple: (User, is_new) where is_new is True if user was just created
    """
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Update username if changed
        if username and user.username != username:
            user.username = username
            await session.commit()
        return user, False
    
    # Create new user with default stats (SPEC 2.1)
    user = User(
        telegram_id=telegram_id,
        username=username,
        level=DEFAULT_LEVEL,
        xp=DEFAULT_XP,
        hp=DEFAULT_HP,
        max_hp=DEFAULT_MAX_HP,
        total_completed=0,
        total_failed=0,
        max_level_reached=DEFAULT_LEVEL
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user, True


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    """Get user by telegram ID."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def update_user_stats(
    session: AsyncSession, 
    user: User,
    level: int = None,
    xp: int = None,
    hp: int = None,
    max_hp: int = None,
    total_completed: int = None,
    total_failed: int = None,
    max_level_reached: int = None
) -> User:
    """Update user stats."""
    if level is not None:
        user.level = level
    if xp is not None:
        user.xp = xp
    if hp is not None:
        user.hp = hp
    if max_hp is not None:
        user.max_hp = max_hp
    if total_completed is not None:
        user.total_completed = total_completed
    if total_failed is not None:
        user.total_failed = total_failed
    if max_level_reached is not None:
        user.max_level_reached = max_level_reached
    
    await session.commit()
    await session.refresh(user)
    return user
