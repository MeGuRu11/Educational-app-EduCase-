# models/task.py
from typing import List, Optional, Any
from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Task(Base):
    """
    Базовая модель для задания любого типа.
    Хранит общую информацию, а специфичные данные (варианты ответов, поля и т.д.)
    хранятся в JSON-поле configuration.
    """
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    
    # Тип здания (SingleChoice, MultiChoice, TextInput, FormFill...)
    task_type: Mapped[str] = mapped_column(String(50), index=True)
    
    # Основной текст задания (может содержать HTML)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[Optional[str]] = mapped_column(Text)
    
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # Сколько баллов дается за это задание
    max_score: Mapped[int] = mapped_column(Integer, default=1)
    
    # JSON со специфической конфигурацией:
    # Пример для SingleChoice:
    # {
    #   "options": [{"id": 1, "text": "A", "is_correct": true}, ...],
    #   "shuffle": true
    # }
    configuration: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Подсказка
    hint: Mapped[Optional[str]] = mapped_column(Text)
    
    # Обоснование правильного ответа
    explanation: Mapped[Optional[str]] = mapped_column(Text)

    case = relationship("Case", backref="tasks")
    
    # attachments (Media) will be added later
