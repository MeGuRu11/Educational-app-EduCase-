# models/media.py
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Media(Base):
    """
    Таблица для загрузки любых файлов.
    file_path - относительный путь в assets/media/
    """
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(512), unique=True)
    content_type: Mapped[str] = mapped_column(String(100)) # image/png, application/pdf
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    
    # Кем загружен
    uploaded_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    
    # К какому кейсу привязан (не обязательно, но удобно для удаления)
    case_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    
    # К какому заданию
    task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))

    uploader = relationship("User")
    case = relationship("Case")
    task = relationship("Task")
