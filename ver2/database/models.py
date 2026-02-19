"""Database models for GameTODO Bot."""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class TaskDifficulty(str, PyEnum):
    """Task difficulty levels (SPEC 7.3)."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EPIC = "epic"


class TaskStatus(str, PyEnum):
    """Task status (SPEC 7.2)."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class User(Base):
    """User model (SPEC 7.1)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    level = Column(Integer, nullable=False, default=1)
    xp = Column(Integer, nullable=False, default=0)
    hp = Column(Integer, nullable=False, default=100)
    max_hp = Column(Integer, nullable=False, default=100)
    total_completed = Column(Integer, nullable=False, default=0)
    total_failed = Column(Integer, nullable=False, default=0)
    max_level_reached = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, level={self.level}, xp={self.xp}, hp={self.hp}/{self.max_hp})>"


class Task(Base):
    """Task model (SPEC 7.2)."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    difficulty = Column(Enum(TaskDifficulty), nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    reminder_sent = Column(Integer, nullable=False, default=0)  # 0 = False, 1 = True

    # Relationship for eager loading
    user = relationship("User", backref="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, difficulty={self.difficulty}, status={self.status})>"
