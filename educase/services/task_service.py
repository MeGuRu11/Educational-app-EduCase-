# services/task_service.py
from typing import Any, Optional, Dict
from sqlalchemy.orm import Session

from models.task import Task
from repositories.task_repo import TaskRepository


class TaskService:
    def __init__(self, session: Session):
        self.session = session
        self.task_repo = TaskRepository(session)

    def create_task(self, case_id: int, task_type: str, title: str, configuration: Dict[str, Any], max_score: int = 1) -> Task:
        new_task = Task(
            case_id=case_id,
            task_type=task_type,
            title=title,
            configuration=configuration,
            max_score=max_score
        )
        return self.task_repo.add(new_task)

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.task_repo.get(task_id)

    def update_task_configuration(self, task_id: int, configuration: Dict[str, Any]) -> Optional[Task]:
        task = self.task_repo.get(task_id)
        if task:
            return self.task_repo.update(task, configuration=configuration)
        return None
