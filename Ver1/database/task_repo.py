"""Task repository: CRUD for tasks (SPEC 7.2)."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Task, TaskStatus, User


async def create_task(
    session: AsyncSession,
    user_id: int,
    title: str,
    difficulty: str,
    deadline: datetime,
) -> Task:
    """Create task with status active."""
    task = Task(
        user_id=user_id,
        title=title[:200],
        difficulty=difficulty,
        deadline=deadline,
        status=TaskStatus.ACTIVE.value,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_active_tasks(session: AsyncSession, user_id: int) -> list[Task]:
    """List active tasks for user, ordered by deadline."""
    result = await session.execute(
        select(Task)
        .where(Task.user_id == user_id, Task.status == TaskStatus.ACTIVE.value)
        .order_by(Task.deadline)
    )
    return list(result.scalars().all())


async def get_failed_tasks(session: AsyncSession, user_id: int) -> list[Task]:
    """List failed (overdue) tasks for user."""
    result = await session.execute(
        select(Task)
        .where(Task.user_id == user_id, Task.status == TaskStatus.FAILED.value)
        .order_by(Task.deadline.desc())
    )
    return list(result.scalars().all())


async def count_active(session: AsyncSession, user_id: int) -> int:
    """Count active tasks."""
    from sqlalchemy import func
    result = await session.execute(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.status == TaskStatus.ACTIVE.value,
        )
    )
    return result.scalar() or 0


async def get_task_by_id(session: AsyncSession, task_id: int, user_id: int) -> Task | None:
    """Get task by id if it belongs to user. Excludes deleted."""
    result = await session.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
            Task.status != TaskStatus.DELETED.value,
        )
    )
    return result.scalar_one_or_none()


async def get_nearest_deadline(session: AsyncSession, user_id: int) -> datetime | None:
    """Nearest deadline among active tasks (for character screen)."""
    result = await session.execute(
        select(Task.deadline)
        .where(Task.user_id == user_id, Task.status == TaskStatus.ACTIVE.value)
        .order_by(Task.deadline)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def complete_task(session: AsyncSession, task_id: int, user_id: int) -> Task | None:
    """Mark task completed. XP/Level-up is handled in the handler. Returns task or None."""
    task = await get_task_by_id(session, task_id, user_id)
    if not task or task.status != TaskStatus.ACTIVE.value:
        return None
    task.status = TaskStatus.COMPLETED.value
    task.completed_at = datetime.now(timezone.utc)
    user = await session.get(User, user_id)
    if user:
        user.total_completed += 1
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task_id: int, user_id: int) -> bool:
    """Mark task deleted (R4). No XP, no damage."""
    task = await get_task_by_id(session, task_id, user_id)
    if not task:
        return False
    task.status = TaskStatus.DELETED.value
    await session.commit()
    return True


async def get_overdue_active_tasks(session: AsyncSession) -> list[Task]:
    """Get all active tasks where deadline < now. (Phase 3 scheduler)."""
    now = datetime.now(timezone.utc)
    # But for now let's just fetch tasks, and we can fetch user lazily or joined.
    # Given model definition `user = relationship(...)` is lazy='selectin', so it should be fine.
    # update: Model definition is default lazy, so we need selectinload.
    result = await session.execute(
        select(Task)
        .options(selectinload(Task.user))
        .where(
            Task.status == TaskStatus.ACTIVE.value,
            Task.deadline < now
        )
    )
    return list(result.scalars().all())


async def delete_all_active_tasks(session: AsyncSession, user_id: int) -> None:
    """Delete all active tasks for user (e.g. on death)."""
    from sqlalchemy import update
    stmt = (
        update(Task)
        .where(Task.user_id == user_id, Task.status == TaskStatus.ACTIVE.value)
        .values(status=TaskStatus.DELETED.value)
    )
    await session.execute(stmt)
