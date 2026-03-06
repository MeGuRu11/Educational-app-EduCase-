# repositories/attempt_repo.py
from sqlalchemy.orm import Session
from models.attempt import Attempt, TaskAnswer
from repositories.base_repo import BaseRepository


class AttemptRepository(BaseRepository[Attempt]):
    def __init__(self, session: Session):
        super().__init__(Attempt, session)


class TaskAnswerRepository(BaseRepository[TaskAnswer]):
    def __init__(self, session: Session):
        super().__init__(TaskAnswer, session)
