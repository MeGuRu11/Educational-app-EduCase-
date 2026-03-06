# models/scenario.py
from typing import List, Optional, Any
from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class ScenarioNode(Base):
    """
    Узел ветвления. Либо показывает контент, либо содержит задание,
    результат которого определяет следующий узел.
    """
    __tablename__ = "scenario_nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    
    # 'content', 'task', 'end'
    node_type: Mapped[str] = mapped_column(String(50))
    
    title: Mapped[str] = mapped_column(String(255))
    content_html: Mapped[Optional[str]] = mapped_column(Text)
    
    # Если type == 'task', связываем с конкретным заданием
    task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"))
    
    # Определяет стартовый ли это узел
    is_start: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # JSON логики переходов. Пример:
    # [
    #   {"condition": "if_correct", "next_node_id": 5},
    #   {"condition": "if_incorrect", "next_node_id": 6},
    #   {"condition": "always", "next_node_id": 7}
    # ]
    transitions: Mapped[List[dict[str, Any]]] = mapped_column(JSON, default=list)

    case = relationship("Case", backref="nodes")
    task = relationship("Task")
