# repositories/group_repo.py
"""
Репозиторий для работы с группами.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models.user import Group
from repositories.base_repo import BaseRepository


class GroupRepository(BaseRepository[Group]):
    def __init__(self, session: Session):
        super().__init__(Group, session)

    def get_by_name(self, name: str) -> Optional[Group]:
        stmt = select(Group).where(Group.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_with_teacher(self, id: int) -> Optional[Group]:
        stmt = select(Group).options(joinedload(Group.teacher)).where(Group.id == id)
        return self.session.execute(stmt).scalar_one_or_none()
