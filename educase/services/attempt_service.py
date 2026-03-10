# services/attempt_service.py
"""
Сервис управления попытками прохождения кейсов.
Создаёт, возобновляет, приостанавливает и завершает попытки.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from models.attempt import Attempt, TaskAnswer
from models.task import Task
from repositories.attempt_repo import AttemptRepository
from services.grader_service import GraderService


class AttemptService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = AttemptRepository(session)
        self.grader = GraderService()

    def start(self, user_id: int, case_id: int) -> Attempt:
        """Начинает новую попытку прохождения кейса."""
        # Если есть незавершенная попытка — возвращаем её
        existing = self.repo.find_active(user_id, case_id)
        if existing:
            return existing

        attempt = Attempt(
            user_id=user_id,
            case_id=case_id,
            status="in_progress",
            started_at=datetime.now().isoformat(),
            score_earned=0.0,
            score_max=0.0,
            time_spent_seconds=0,
        )
        self.session.add(attempt)
        self.session.commit()
        return attempt

    def save_answer(self, attempt_id: int, task_id: int,
                    answer_data: dict) -> Optional[TaskAnswer]:
        """Сохраняет ответ студента и автоматически проверяет."""
        attempt = self.repo.get(attempt_id)
        if not attempt or attempt.status != "in_progress":
            return None

        task = self.session.get(Task, task_id)
        if not task:
            return None

        # Проверяем ответ
        result = self.grader.grade(
            task_type=task.task_type,
            config=task.configuration or {},
            answer=answer_data,
            max_score=float(task.max_score),
        )

        # Ищем существующий ответ (авто-сохранение перезаписывает)
        existing_answer = (
            self.session.query(TaskAnswer)
            .filter_by(attempt_id=attempt_id, task_id=task_id)
            .first()
        )

        if existing_answer:
            # Обновляем результат, убираем старый балл
            attempt.score_earned -= existing_answer.score_earned
            existing_answer.answer_data = answer_data
            existing_answer.is_correct = result.is_correct
            existing_answer.score_earned = result.score
            existing_answer.feedback = result.feedback
            task_answer = existing_answer
        else:
            task_answer = TaskAnswer(
                attempt_id=attempt_id,
                task_id=task_id,
                answer_data=answer_data,
                is_correct=result.is_correct,
                score_earned=result.score,
                feedback=result.feedback,
            )
            self.session.add(task_answer)

        # Обновляем суммарный балл
        attempt.score_earned += result.score
        self.session.commit()

        return task_answer

    def finish(self, attempt_id: int) -> Optional[Attempt]:
        """Завершает попытку и фиксирует результат."""
        attempt = self.repo.get(attempt_id)
        if not attempt:
            return None

        attempt.status = "completed"
        attempt.finished_at = datetime.now().isoformat()

        # Пересчитываем max_score из заданий кейса
        tasks = self.session.query(Task).filter_by(case_id=attempt.case_id).all()
        attempt.score_max = sum(float(t.max_score) for t in tasks)

        self.session.commit()
        return attempt

    def pause(self, attempt_id: int, elapsed_seconds: int = 0) -> Optional[Attempt]:
        """Ставит попытку на паузу, сохраняя прогресс времени."""
        attempt = self.repo.get(attempt_id)
        if not attempt or attempt.status != "in_progress":
            return None

        attempt.time_spent_seconds += elapsed_seconds
        attempt.status = "paused"
        self.session.commit()
        return attempt

    def resume(self, attempt_id: int) -> Optional[Attempt]:
        """Снимает попытку с паузы."""
        attempt = self.repo.get(attempt_id)
        if not attempt or attempt.status != "paused":
            return None

        attempt.status = "in_progress"
        self.session.commit()
        return attempt

    def abandon(self, attempt_id: int) -> Optional[Attempt]:
        """Отменяет попытку (студент вышел)."""
        attempt = self.repo.get(attempt_id)
        if not attempt:
            return None

        attempt.status = "abandoned"
        attempt.finished_at = datetime.now().isoformat()
        self.session.commit()
        return attempt

    def get_progress(self, attempt_id: int) -> dict:
        """Возвращает прогресс прохождения."""
        attempt = self.repo.get(attempt_id)
        if not attempt:
            return {}

        tasks = self.session.query(Task).filter_by(case_id=attempt.case_id).order_by(Task.order_index).all()
        answers = {a.task_id: a for a in attempt.answers}

        tasks_progress = []
        for t in tasks:
            ans = answers.get(t.id)
            tasks_progress.append({
                "task_id": t.id,
                "task_type": t.task_type,
                "title": t.title,
                "answered": ans is not None,
                "is_correct": ans.is_correct if ans else None,
                "score": ans.score_earned if ans else 0,
            })

        total_tasks = len(tasks)
        answered_tasks = sum(1 for tp in tasks_progress if tp["answered"])

        return {
            "attempt_id": attempt.id,
            "status": attempt.status,
            "total_tasks": total_tasks,
            "answered_tasks": answered_tasks,
            "score_earned": attempt.score_earned,
            "score_max": sum(float(t.max_score) for t in tasks),
            "time_spent_seconds": attempt.time_spent_seconds,
            "tasks": tasks_progress,
        }

    def get_recent_attempts(self, user_id: int, limit: int = 5) -> list[Attempt]:
        return self.repo.get_recent(user_id, limit)

    def get_user_stats(self, user_id: int) -> dict:
        attempts = self.repo.get_all_for_user(user_id)
        completed = [a for a in attempts if a.status == "completed"]
        
        total_time = sum(a.time_spent_seconds for a in attempts)
        total_score = sum(a.score_earned for a in completed)
        max_score_possible = sum(float(a.score_max) for a in completed if a.score_max)
        
        avg_score_percent = 0.0
        if max_score_possible > 0:
            avg_score_percent = (total_score / max_score_possible) * 100

        return {
            "total_attempts": len(attempts),
            "completed_cases": len(completed),
            "total_time_seconds": total_time,
            "avg_score_percent": round(avg_score_percent, 1)
        }
