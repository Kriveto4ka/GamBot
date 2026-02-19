"""User repository: get or create by telegram_id."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import DEFAULT_HP, DEFAULT_LEVEL, DEFAULT_MAX_HP, DEFAULT_XP
from database.models import User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None = None,
) -> tuple[User, bool]:
    """Return (user, is_new). is_new=True if user was just created (SPEC 2.1 defaults)."""
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user:
        if username is not None:
            user.username = username
            await session.commit()
        return user, False
    user = User(
        telegram_id=telegram_id,
        username=username,
        level=DEFAULT_LEVEL,
        xp=DEFAULT_XP,
        hp=DEFAULT_HP,
        max_hp=DEFAULT_MAX_HP,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user, True
