# repositories/task_repo.py
from sqlalchemy.orm import Session
from models.task import Task
from repositories.base_repo import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: Session):
        super().__init__(Task, session)
