"""Task difficulty labels and rewards (SPEC 7.3, 8.8)."""
from database.models import TaskDifficulty

DIFFICULTY_LABELS = {
    TaskDifficulty.EASY.value: "🟢 Лёгкая (+10 XP)",
    TaskDifficulty.MEDIUM.value: "🟡 Средняя (+25 XP)",
    TaskDifficulty.HARD.value: "🔴 Сложная (+50 XP)",
    TaskDifficulty.EPIC.value: "🟣 Эпическая (+100 XP)",
}

DIFFICULTY_XP_DAMAGE = {
    TaskDifficulty.EASY.value: (10, 5),
    TaskDifficulty.MEDIUM.value: (25, 15),
    TaskDifficulty.HARD.value: (50, 30),
    TaskDifficulty.EPIC.value: (100, 50),
}


def format_difficulty_short(difficulty: str) -> str:
    """e.g. 'Средняя (+25 XP / -15 HP)' for task detail/created."""
    xp, damage = DIFFICULTY_XP_DAMAGE.get(difficulty, (0, 0))
    names = {
        TaskDifficulty.EASY.value: "Лёгкая",
        TaskDifficulty.MEDIUM.value: "Средняя",
        TaskDifficulty.HARD.value: "Сложная",
        TaskDifficulty.EPIC.value: "Эпическая",
    }
    name = names.get(difficulty, difficulty)
    return f"{name} (+{xp} XP / -{damage} HP)"
