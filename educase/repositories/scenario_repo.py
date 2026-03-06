# repositories/scenario_repo.py
from sqlalchemy.orm import Session
from models.scenario import ScenarioNode
from repositories.base_repo import BaseRepository


class ScenarioNodeRepository(BaseRepository[ScenarioNode]):
    def __init__(self, session: Session):
        super().__init__(ScenarioNode, session)
