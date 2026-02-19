"""Task repository for database operations."""
from datetime import datetime
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from database.models import Task, TaskDifficulty, TaskStatus, User


# Title max length constant
TITLE_MAX_LEN = 200


async def create_task(
    session: AsyncSession,
    user_id: int,
    title: str,
    difficulty: TaskDifficulty,
    deadline: datetime
) -> Task:
    """Create a new task."""
    # Truncate title if too long (E3)
    if len(title) > TITLE_MAX_LEN:
        title = title[:TITLE_MAX_LEN]
    
    # Remove timezone info for TIMESTAMP WITHOUT TIME ZONE compatibility
    if deadline.tzinfo is not None:
        deadline = deadline.replace(tzinfo=None)
    
    task = Task(
        user_id=user_id,
        title=title,
        difficulty=difficulty,
        deadline=deadline,
        status=TaskStatus.ACTIVE
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_active_tasks(session: AsyncSession, user_id: int) -> list[Task]:
    """Get all active tasks for a user."""
    result = await session.execute(
        select(Task)
        .where(and_(Task.user_id == user_id, Task.status == TaskStatus.ACTIVE))
        .order_by(Task.deadline)
    )
    return list(result.scalars().all())


async def get_failed_tasks(session: AsyncSession, user_id: int) -> list[Task]:
    """Get all failed (overdue) tasks for a user."""
    result = await session.execute(
        select(Task)
        .where(and_(Task.user_id == user_id, Task.status == TaskStatus.FAILED))
        .order_by(Task.deadline.desc())
    )
    return list(result.scalars().all())


async def count_active_tasks(session: AsyncSession, user_id: int) -> int:
    """Count active tasks for a user."""
    result = await session.execute(
        select(Task)
        .where(and_(Task.user_id == user_id, Task.status == TaskStatus.ACTIVE))
    )
    return len(list(result.scalars().all()))


async def get_task_by_id(session: AsyncSession, task_id: int, user_id: int = None) -> Task | None:
    """Get task by ID, optionally filtering by user."""
    query = select(Task).where(Task.id == task_id)
    
    if user_id:
        query = query.where(Task.user_id == user_id)
    
    # Exclude deleted tasks
    query = query.where(Task.status != TaskStatus.DELETED)
    
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_nearest_deadline(session: AsyncSession, user_id: int) -> datetime | None:
    """Get the nearest deadline for a user's active tasks."""
    result = await session.execute(
        select(Task.deadline)
        .where(and_(Task.user_id == user_id, Task.status == TaskStatus.ACTIVE))
        .order_by(Task.deadline)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def complete_task(session: AsyncSession, task_id: int, user_id: int) -> Task | None:
    """
    Mark task as completed.
    
    Returns:
        Task if completed, None if task not found or not active
    """
    task = await get_task_by_id(session, task_id, user_id)
    
    if not task or task.status != TaskStatus.ACTIVE:
        return None
    
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task_id: int, user_id: int) -> bool:
    """
    Delete a task (soft delete by changing status).
    
    Returns:
        True if deleted, False if not found
    """
    task = await get_task_by_id(session, task_id, user_id)
    
    if not task:
        return False
    
    task.status = TaskStatus.DELETED
    await session.commit()
    return True


async def get_overdue_tasks(session: AsyncSession, now: datetime = None) -> list[Task]:
    """
    Get all overdue active tasks (for scheduler).
    
    Args:
        session: Database session
        now: Current time (defaults to UTC now)
    
    Returns:
        List of overdue tasks with user relationship loaded
    """
    if now is None:
        now = datetime.utcnow()
    
    result = await session.execute(
        select(Task)
        .options(selectinload(Task.user))
        .where(and_(
            Task.status == TaskStatus.ACTIVE,
            Task.deadline <= now
        ))
    )
    return list(result.scalars().all())


async def get_tasks_for_reminder(session: AsyncSession, now: datetime = None) -> list[Task]:
    """
    Get tasks that need reminder (deadline within 1 hour, no reminder sent yet).
    
    Args:
        session: Database session
        now: Current time (defaults to UTC now)
    
    Returns:
        List of tasks needing reminder with user relationship loaded
    """
    if now is None:
        now = datetime.utcnow()
    
    one_hour_later = now + __import__('datetime').timedelta(hours=1)
    
    result = await session.execute(
        select(Task)
        .options(selectinload(Task.user))
        .where(and_(
            Task.status == TaskStatus.ACTIVE,
            Task.deadline <= one_hour_later,
            Task.deadline > now,
            Task.reminder_sent == 0
        ))
    )
    return list(result.scalars().all())


async def mark_reminder_sent(session: AsyncSession, task_id: int) -> None:
    """Mark that reminder was sent for a task."""
    result = await session.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if task:
        task.reminder_sent = 1
        await session.commit()


async def mark_task_failed(session: AsyncSession, task_id: int) -> None:
    """Mark task as failed (overdue)."""
    result = await session.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if task:
        task.status = TaskStatus.FAILED
        await session.commit()


async def delete_all_active_tasks(session: AsyncSession, user_id: int) -> int:
    """
    Delete all active tasks for a user (used on death).
    
    Returns:
        Number of tasks deleted
    """
    result = await session.execute(
        select(Task)
        .where(and_(Task.user_id == user_id, Task.status == TaskStatus.ACTIVE))
    )
    tasks = list(result.scalars().all())
    
    count = 0
    for task in tasks:
        task.status = TaskStatus.DELETED
        count += 1
    
    await session.commit()
    return count
