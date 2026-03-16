# repositories/content_repo.py
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.content import Discipline, Topic, Module, CaseGroup, Case
from repositories.base_repo import BaseRepository


class DisciplineRepository(BaseRepository[Discipline]):
    def __init__(self, session: Session):
        super().__init__(Discipline, session)

    def get_by_name(self, name: str) -> Optional[Discipline]:
        stmt = select(Discipline).where(Discipline.name == name)
        return self.session.scalars(stmt).first()


class TopicRepository(BaseRepository[Topic]):
    def __init__(self, session: Session):
        super().__init__(Topic, session)


class ModuleRepository(BaseRepository[Module]):
    def __init__(self, session: Session):
        super().__init__(Module, session)


class CaseGroupRepository(BaseRepository[CaseGroup]):
    def __init__(self, session: Session):
        super().__init__(CaseGroup, session)


class CaseRepository(BaseRepository[Case]):
    def __init__(self, session: Session):
        super().__init__(Case, session)
        
    def get_all_published(self) -> List[Case]:
        stmt = select(Case).where(Case.is_published == True).order_by(Case.id.desc())
        return list(self.session.scalars(stmt).all())

    def count_published(self) -> int:
        from sqlalchemy import func
        stmt = select(func.count(Case.id)).where(Case.is_published == True)
        return self.session.execute(stmt).scalar() or 0

