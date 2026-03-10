# services/scenario_service.py
"""
Сервис обхода графа сценария ветвления.
Определяет текущий узел, следующий узел на основе ответа,
и является ли узел финальным.
"""
from typing import Optional, List

from sqlalchemy.orm import Session

from models.scenario import ScenarioNode


class ScenarioService:
    def __init__(self, session: Session):
        self.session = session

    def get_start_node(self, case_id: int) -> Optional[ScenarioNode]:
        """Находит стартовый узел сценария."""
        return (
            self.session.query(ScenarioNode)
            .filter_by(case_id=case_id, is_start=True)
            .first()
        )

    def get_node(self, node_id: int) -> Optional[ScenarioNode]:
        """Получает узел по ID."""
        return self.session.get(ScenarioNode, node_id)

    def get_all_nodes(self, case_id: int) -> List[ScenarioNode]:
        """Получает все узлы сценария."""
        return (
            self.session.query(ScenarioNode)
            .filter_by(case_id=case_id)
            .all()
        )

    def get_next_node(self, current_node: ScenarioNode,
                      is_correct: Optional[bool] = None,
                      selected_edge: Optional[str] = None) -> Optional[ScenarioNode]:
        """
        Определяет следующий узел на основе текущего и результата ответа.
        
        Логика переходов (transitions JSON):
        - {"condition": "always", "next_node_id": 5}     → безусловный переход
        - {"condition": "if_correct", "next_node_id": 5}  → при правильном ответе
        - {"condition": "if_incorrect", "next_node_id": 6} → при неправильном
        - {"condition": "edge_id", "edge_label": "...", "next_node_id": 7} → по выбору ребра
        """
        transitions = current_node.transitions or []

        for tr in transitions:
            condition = tr.get("condition", "always")

            # Переход по конкретному ребру (для ветвления)
            if condition == "edge_id" and selected_edge:
                if tr.get("edge_id") == selected_edge:
                    return self._resolve_node(tr.get("next_node_id"))

            # Условный переход по результату задания
            if condition == "if_correct" and is_correct is True:
                return self._resolve_node(tr.get("next_node_id"))

            if condition == "if_incorrect" and is_correct is False:
                return self._resolve_node(tr.get("next_node_id"))

            # Безусловный переход (fallback)
            if condition == "always":
                return self._resolve_node(tr.get("next_node_id"))

        return None  # Тупик — нет подходящего перехода

    def is_terminal(self, node: ScenarioNode) -> bool:
        """Проверяет, является ли узел финальным (end)."""
        return node.node_type == "end"

    def _resolve_node(self, node_id: Optional[int]) -> Optional[ScenarioNode]:
        """Получает узел по ID из transitions."""
        if node_id is None:
            return None
        return self.session.get(ScenarioNode, node_id)
