# services/case_service.py
from typing import List, Optional
from sqlalchemy.orm import Session

from models.content import Case, CaseGroup
from repositories.content_repo import CaseRepository, CaseGroupRepository


class CaseService:
    def __init__(self, session: Session):
        self.session = session
        self.case_repo = CaseRepository(session)
        self.group_repo = CaseGroupRepository(session)

    def create_case(self, group_id: int, title: str, author_id: int, difficulty: int = 1) -> Case:
        new_case = Case(
            group_id=group_id,
            title=title,
            author_id=author_id,
            difficulty=difficulty,
            is_published=False
        )
        return self.case_repo.add(new_case)

    def get_case(self, case_id: int) -> Optional[Case]:
        return self.case_repo.get(case_id)

    def publish_case(self, case_id: int) -> Optional[Case]:
        case = self.case_repo.get(case_id)
        if case:
            case.is_published = True
            self.session.commit()
            self.session.refresh(case)
        return case

    def create_group(self, module_id: int, name: str, order_index: int = 0) -> CaseGroup:
        new_group = CaseGroup(
            module_id=module_id,
            name=name,
            order_index=order_index
        )
        return self.group_repo.add(new_group)
