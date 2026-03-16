# repositories/user_repo.py
"""
Репозиторий для работы с пользователями.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models.user import Role, User
from repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).options(joinedload(User.role)).where(User.username == username)
        return self.session.execute(stmt).scalar_one_or_none()

    def count_by_role(self, role_name: str) -> int:
        from sqlalchemy import func
        stmt = select(func.count(User.id)).join(User.role).where(Role.name == role_name)
        return self.session.execute(stmt).scalar() or 0


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: Session):
        super().__init__(Role, session)

    def get_by_name(self, name: str) -> Optional[Role]:
        stmt = select(Role).where(Role.name == name)
        return self.session.execute(stmt).scalar_one_or_none()
