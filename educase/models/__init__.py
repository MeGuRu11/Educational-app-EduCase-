# models/__init__.py
"""
Импорт всех моделей для удобства и чтобы Alembic видел Base.metadata со всеми таблицами.
"""
from models.base import Base
from models.user import Role, Group, User
from models.content import Discipline, Topic, Module, CaseGroup, Case
from models.task import Task
from models.scenario import ScenarioNode
from models.media import Media
from models.system import SystemSetting, SystemLog
from models.attempt import Attempt, TaskAnswer

__all__ = [
    "Base",
    "Role", "Group", "User",
    "Discipline", "Topic", "Module", "CaseGroup", "Case",
    "Task",
    "ScenarioNode",
    "Media",
    "SystemSetting", "SystemLog",
    "Attempt", "TaskAnswer"
]
