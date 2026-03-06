# models/content.py
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Discipline(Base):
    __tablename__ = "disciplines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    topics: Mapped[List["Topic"]] = relationship("Topic", back_populates="discipline", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    discipline_id: Mapped[int] = mapped_column(ForeignKey("disciplines.id"))
    name: Mapped[str] = mapped_column(String(150), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    discipline: Mapped["Discipline"] = relationship("Discipline", back_populates="topics")
    modules: Mapped[List["Module"]] = relationship("Module", back_populates="topic", cascade="all, delete-orphan")


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    topic: Mapped["Topic"] = relationship("Topic", back_populates="modules")
    case_groups: Mapped[List["CaseGroup"]] = relationship("CaseGroup", back_populates="module", cascade="all, delete-orphan")


class CaseGroup(Base):
    __tablename__ = "case_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"))
    name: Mapped[str] = mapped_column(String(200))
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    module: Mapped["Module"] = relationship("Module", back_populates="case_groups")
    cases: Mapped[List["Case"]] = relationship("Case", back_populates="group", cascade="all, delete-orphan")


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("case_groups.id"))
    title: Mapped[str] = mapped_column(String(255), index=True)
    short_description: Mapped[Optional[str]] = mapped_column(Text)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)  # 1-3
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(Integer) # None if unlimited
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Автор (создатель)
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    group: Mapped["CaseGroup"] = relationship("CaseGroup", back_populates="cases")
    
    # Дальнейшие связи (Tasks, Scenarios) будут добавлены позже
