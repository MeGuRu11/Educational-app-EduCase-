# repositories/base_repo.py
"""
Generic репозиторий для базовых CRUD-операций с моделями SQLAlchemy.
"""
from typing import Generic, TypeVar, Any, cast

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get(self, id: int) -> ModelType | None:
        stmt = select(self.model).where(getattr(self.model, "id") == id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def count(self) -> int:
        from sqlalchemy import func
        stmt = select(func.count()).select_from(self.model)
        return self.session.execute(stmt).scalar() or 0

    def add(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def create(self, **kwargs) -> ModelType:
        obj = self.model(**kwargs)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: ModelType, **kwargs) -> ModelType:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        model_any = cast(Any, self.model)
        stmt = delete(self.model).where(model_any.id == id)
        result = cast(Any, self.session.execute(stmt))
        self.session.commit()
        return result.rowcount > 0 # type: ignore
