# models/user.py
"""
Модели данных: Role, User, Group.
"""
import json
from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    permissions: Mapped[str] = mapped_column(Text, default="{}", nullable=False)

    users: Mapped[List["User"]] = relationship(back_populates="role")

    @property
    def permissions_dict(self) -> dict:
        try:
            return json.loads(self.permissions)
        except Exception:
            return {}


class Group(Base, TimestampMixin):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    teacher_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    is_active: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    teacher: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="managed_groups",
        foreign_keys=[teacher_id],
    )
    # Мягкая связь: users.group_id не имеет DB constraint
    students: Mapped[List["User"]] = relationship(
        "User",
        primaryjoin="User.group_id == Group.id",
        back_populates="group",
        foreign_keys="User.group_id",
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    group_id: Mapped[Optional[int]] = mapped_column(Integer)

    avatar_path: Mapped[Optional[str]] = mapped_column(String)
    is_active: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_login_at: Mapped[Optional[str]] = mapped_column(String)
    login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[str]] = mapped_column(String)

    # Relationships
    role: Mapped["Role"] = relationship(back_populates="users")
    group: Mapped[Optional["Group"]] = relationship(
        "Group",
        primaryjoin="User.group_id == Group.id",
        back_populates="students",
        foreign_keys=[group_id],
    )
    managed_groups: Mapped[List["Group"]] = relationship(
        "Group",
        back_populates="teacher",
        foreign_keys="Group.teacher_id",
    )
