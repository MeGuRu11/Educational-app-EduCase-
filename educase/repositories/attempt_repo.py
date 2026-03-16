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

    def count_today(self) -> int:
        from datetime import datetime
        from sqlalchemy import func
        today_str = datetime.now().strftime("%Y-%m-%d")
        stmt = select(func.count(Attempt.id)).where(Attempt.started_at.like(f"{today_str}%"))
        return self.session.execute(stmt).scalar() or 0

    def get_avg_score(self, user_id: Optional[int] = None) -> float:
        from sqlalchemy import func
        stmt = select(func.avg(Attempt.score_earned))
        if user_id:
            stmt = stmt.where(Attempt.user_id == user_id)
        res = self.session.execute(stmt).scalar()
        return float(res) if res else 0.0

    def get_recent_activity(self, limit: int = 10) -> list[Attempt]:
        from sqlalchemy.orm import joinedload
        stmt = (
            select(Attempt)
            .options(joinedload(Attempt.user), joinedload(Attempt.case))
            .order_by(Attempt.started_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def get_daily_stats(self, days: int = 7) -> dict:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        
        dates = []
        attempts = []
        completed = []
        
        # Mapping English day names to Russian for better UX if needed, or keep short English
        day_names = {"Mon": "Пн", "Tue": "Вт", "Wed": "Ср", "Thu": "Чт", "Fri": "Пт", "Sat": "Сб", "Sun": "Вс"}
        
        for i in range(days):
            d = start_date + timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            eng_day = d.strftime("%a")
            dates.append(day_names.get(eng_day, eng_day))
            
            att_count = self.session.query(func.count(Attempt.id)).filter(Attempt.started_at.like(f"{d_str}%")).scalar() or 0
            attempts.append(att_count)
            
            comp_count = self.session.query(func.count(Attempt.id)).filter(
                Attempt.started_at.like(f"{d_str}%"),
                Attempt.status == "completed"
            ).scalar() or 0
            completed.append(comp_count)
            
        return {"dates": dates, "attempts": attempts, "completed": completed}

class TaskAnswerRepository(BaseRepository[TaskAnswer]):
    def __init__(self, session: Session):
        super().__init__(TaskAnswer, session)
