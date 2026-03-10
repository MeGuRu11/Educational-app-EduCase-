# repositories/attempt_repo.py
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.attempt import Attempt, TaskAnswer
from repositories.base_repo import BaseRepository


class AttemptRepository(BaseRepository[Attempt]):
    def __init__(self, session: Session):
        super().__init__(Attempt, session)

    def find_active(self, user_id: int, case_id: int) -> Optional[Attempt]:
        """Находит незавершённую попытку пользователя для кейса."""
        return (
            self.session.query(Attempt)
            .filter_by(user_id=user_id, case_id=case_id)
            .filter(Attempt.status.in_(["in_progress", "paused"]))
            .first()
        )
    def get_recent(self, user_id: int, limit: int = 5) -> list[Attempt]:
        """Возвращает последние попытки пользователя."""
        stmt = (
            select(Attempt)
            .where(Attempt.user_id == user_id)
            .order_by(Attempt.started_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def get_all_for_user(self, user_id: int) -> list[Attempt]:
        """Все попытки пользователя для аналитики/истории."""
        stmt = (
            select(Attempt)
            .where(Attempt.user_id == user_id)
            .order_by(Attempt.started_at.desc())
        )
        return list(self.session.scalars(stmt).all())

class TaskAnswerRepository(BaseRepository[TaskAnswer]):
    def __init__(self, session: Session):
        super().__init__(TaskAnswer, session)
