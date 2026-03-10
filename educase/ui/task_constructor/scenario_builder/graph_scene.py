# ui/task_constructor/scenario_builder/graph_scene.py
"""
QGraphicsScene для визуального конструктора сценариев.
Управляет узлами и рёбрами, поддерживает создание связей через порты.
"""
from PySide6.QtWidgets import QGraphicsScene, QMenu, QGraphicsView
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QColor, QPen

from ui.styles.theme import COLORS
from .node_item import NodeItem, PortItem, NODE_TYPES
from .edge_item import EdgeItem

from PySide6.QtWidgets import QGraphicsTextItem


class GraphScene(QGraphicsScene):
    """
    Сцена графа сценариев. Хранит узлы и рёбра,
    поддерживает drag-создание связей через порты.
    """
    graph_changed = Signal()  # Эмитится при любом изменении графа

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(-2000, -2000, 4000, 4000)

        self.nodes: list[NodeItem] = []
        self.edges: list[EdgeItem] = []

        # Состояние рисования связи
        self._connecting = False
        self._connect_source: NodeItem | None = None
        self._temp_line = None
        self._temp_start = QPointF()

    def add_node(self, node_type: str = "scene", title: str = "",
                 x: float = 0, y: float = 0) -> NodeItem:
        """Добавляет новый узел на сцену."""
        node = NodeItem(node_type=node_type, title=title, x=x, y=y)
        self.addItem(node)
        self.nodes.append(node)
        self.graph_changed.emit()
        return node

    def add_edge(self, source: NodeItem, target: NodeItem,
                 label: str = "") -> EdgeItem | None:
        """Добавляет ребро между двумя узлами (без дубликатов)."""
        # Проверка на дубликат
        for e in self.edges:
            if e.source_node == source and e.target_node == target:
                return None
        # Запрет петель
        if source == target:
            return None

        edge = EdgeItem(source, target, label)
        self.addItem(edge)
        self.edges.append(edge)
        self.graph_changed.emit()
        return edge

    def remove_node(self, node: NodeItem):
        """Удаляет узел и все подключённые рёбра."""
        # Удаляем все рёбра, связанные с узлом
        edges_to_remove = [e for e in self.edges
                           if e.source_node == node or e.target_node == node]
        for e in edges_to_remove:
            self.remove_edge(e)

        if node in self.nodes:
            self.nodes.remove(node)
        self.removeItem(node)
        self.graph_changed.emit()

    def remove_edge(self, edge: EdgeItem):
        """Удаляет ребро."""
        if edge.source_node and edge in edge.source_node.edges:
            edge.source_node.edges.remove(edge)
        if edge.target_node and edge in edge.target_node.edges:
            edge.target_node.edges.remove(edge)
        if edge in self.edges:
            self.edges.remove(edge)
        self.removeItem(edge)
        self.graph_changed.emit()

    def _get_transform(self):
        """Возвращает трансформацию текущего view."""
        from PySide6.QtGui import QTransform
        if self.views():
            return self.views()[0].transform()
        return QTransform()

    def _set_all_input_ports_highlighted(self, on: bool):
        """Подсвечивает/гасит все input-порты на сцене."""
        for node in self.nodes:
            node.input_port.set_highlighted(on)

    def mousePressEvent(self, event):
        """Обработка начала создания связи через порт."""
        item = self.itemAt(event.scenePos(), self._get_transform())

        if isinstance(item, PortItem) and item.is_output:
            # Начинаем рисование связи от output-порта
            self._connecting = True
            self._connect_source = item.parent_node
            self._temp_start = item.center_scene_pos()

            # Подсвечиваем все input-порты, чтобы пользователь видел куда бросать
            self._set_all_input_ports_highlighted(True)

            pen = QPen(QColor(COLORS["accent"]), 2, Qt.PenStyle.DashLine)
            self._temp_line = self.addLine(
                self._temp_start.x(), self._temp_start.y(),
                self._temp_start.x(), self._temp_start.y(),
                pen
            )
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._connecting and self._temp_line:
            self._temp_line.setLine(
                self._temp_start.x(), self._temp_start.y(),
                event.scenePos().x(), event.scenePos().y()
            )
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._connecting:
            self._connecting = False
            if self._temp_line:
                self.removeItem(self._temp_line)
                self._temp_line = None

            # Гасим подсветку input-портов
            self._set_all_input_ports_highlighted(False)

            # Ищем цель под курсором
            target_node = None
            item = self.itemAt(event.scenePos(), self._get_transform())

            if isinstance(item, PortItem) and not item.is_output:
                # Бросили точно на input-порт
                target_node = item.parent_node
            elif isinstance(item, (NodeItem, QGraphicsTextItem)):
                # Бросили на узел или его текст — тоже соединяем
                if isinstance(item, NodeItem):
                    target_node = item
                elif item.parentItem() and isinstance(item.parentItem(), NodeItem):
                    target_node = item.parentItem()

            if target_node and self._connect_source and target_node != self._connect_source:
                self.add_edge(self._connect_source, target_node)

            self._connect_source = None
            return

        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        """Контекстное меню на пустой области → добавить узел."""
        item = self.itemAt(event.scenePos(), self._get_transform())

        if item is None:
            menu = QMenu()
            menu.setStyleSheet(f"""
                QMenu {{
                    background: {COLORS['bg_elevated']};
                    border: 1px solid {COLORS['stroke_divider']};
                    border-radius: 6px;
                    padding: 4px;
                }}
                QMenu::item {{
                    padding: 6px 24px;
                    color: {COLORS['text_primary']};
                }}
                QMenu::item:selected {{
                    background: {COLORS['state_hover']};
                    border-radius: 4px;
                }}
            """)

            add_menu = menu.addMenu("➕ Добавить узел")
            actions = {}
            for type_id, info in NODE_TYPES.items():
                a = add_menu.addAction(f"{info['label']}")
                actions[a] = type_id

            action = menu.exec(event.screenPos())
            if action and action in actions:
                pos = event.scenePos()
                self.add_node(
                    node_type=actions[action],
                    x=pos.x(), y=pos.y()
                )
            return

        super().contextMenuEvent(event)

    def get_data(self) -> dict:
        """Сериализация графа."""
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }

    def load_data(self, data: dict):
        """Загрузка графа из dict."""
        # Очищаем
        for e in list(self.edges):
            self.remove_edge(e)
        for n in list(self.nodes):
            self.remove_node(n)

        # Узлы
        node_map = {}
        for nd in data.get("nodes", []):
            node = NodeItem(
                node_id=nd["id"],
                node_type=nd.get("type", "scene"),
                title=nd.get("title", ""),
                x=nd.get("x", 0),
                y=nd.get("y", 0),
            )
            node.description = nd.get("description", "")
            node.task_type = nd.get("task_type", "")
            self.addItem(node)
            self.nodes.append(node)
            node_map[nd["id"]] = node

        # Рёбра
        for ed in data.get("edges", []):
            src = node_map.get(ed["source"])
            tgt = node_map.get(ed["target"])
            if src and tgt:
                edge = EdgeItem(src, tgt, ed.get("label", ""))
                self.addItem(edge)
                self.edges.append(edge)
