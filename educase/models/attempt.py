# models/attempt.py
from typing import Any, Optional
from sqlalchemy import String, Integer, ForeignKey, JSON, Float, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Attempt(Base):
    """
    Попытка прохождения конкретного Кейса пользователем.
    """
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    
    # Статус прохождения: "in_progress", "completed", "failed"
    status: Mapped[str] = mapped_column(String(50), default="in_progress")
    
    score_earned: Mapped[float] = mapped_column(Float, default=0.0)
    score_max: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Время прохождения в секундах
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)
    
    started_at: Mapped[Optional[str]] = mapped_column(String(50))
    finished_at: Mapped[Optional[str]] = mapped_column(String(50))

    user = relationship("User")
    case = relationship("Case", backref="attempts")
    answers = relationship("TaskAnswer", back_populates="attempt", cascade="all, delete-orphan")


class TaskAnswer(Base):
    """
    Ответ пользователя на конкретное задание внутри попытки.
    """
    __tablename__ = "task_answers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("attempts.id", ondelete="CASCADE"))
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    
    # JSON с ответом, структура зависит от типа задания
    # e.g { "selected_option_id": 12 }
    # или { "text": "Мацерация" }
    answer_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    score_earned: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Для заданий, требующих ручной проверки (form_fill_document, например)
    needs_manual_review: Mapped[bool] = mapped_column(Boolean, default=False)
    feedback: Mapped[Optional[str]] = mapped_column(Text) # Обратная связь от преподавателя

    attempt: Mapped["Attempt"] = relationship("Attempt", back_populates="answers")
    task = relationship("Task")
