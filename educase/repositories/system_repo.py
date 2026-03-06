# repositories/system_repo.py
from sqlalchemy.orm import Session
from models.system import SystemSetting, SystemLog
from repositories.base_repo import BaseRepository


class SystemSettingRepository(BaseRepository[SystemSetting]):
    def __init__(self, session: Session):
        super().__init__(SystemSetting, session)


class SystemLogRepository(BaseRepository[SystemLog]):
    def __init__(self, session: Session):
        super().__init__(SystemLog, session)
