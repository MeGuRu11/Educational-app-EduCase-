# services/module_service.py
from typing import List, Optional
from sqlalchemy.orm import Session

from models.content import Discipline, Topic, Module
from repositories.content_repo import DisciplineRepository, TopicRepository, ModuleRepository


class ModuleService:
    def __init__(self, session: Session):
        self.session = session
        self.discipline_repo = DisciplineRepository(session)
        self.topic_repo = TopicRepository(session)
        self.module_repo = ModuleRepository(session)

    def create_discipline(self, name: str, description: str = "") -> Discipline:
        new_discipline = Discipline(name=name, description=description)
        return self.discipline_repo.add(new_discipline)

    def create_topic(self, discipline_id: int, name: str, description: str = "", order_index: int = 0) -> Topic:
        new_topic = Topic(discipline_id=discipline_id, name=name, description=description, order_index=order_index)
        return self.topic_repo.add(new_topic)

    def create_module(self, topic_id: int, name: str, description: str = "", order_index: int = 0) -> Module:
        new_module = Module(topic_id=topic_id, name=name, description=description, order_index=order_index)
        return self.module_repo.add(new_module)
