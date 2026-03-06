# repositories/media_repo.py
from sqlalchemy.orm import Session
from models.media import Media
from repositories.base_repo import BaseRepository


class MediaRepository(BaseRepository[Media]):
    def __init__(self, session: Session):
        super().__init__(Media, session)
