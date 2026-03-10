# ui/task_constructor/scenario_builder/node_item.py
"""
Узел графа сценария — скруглённый прямоугольник с заголовком,
портами для соединений, drag-and-drop и контекстным меню.
"""
import uuid
from PySide6.QtWidgets import (
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem,
    QMenu, QGraphicsItem
)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QColor, QPen, QBrush, QFont, QPainter,
    QPainterPath, QLinearGradient
)

from ui.styles.theme import COLORS


# Типы узлов сценария
NODE_TYPES = {
    "start": {"label": "Старт", "color": "#4CAF50"},
    "scene": {"label": "Сцена", "color": COLORS["accent"]},
    "question": {"label": "Вопрос", "color": "#FF9800"},
    "action": {"label": "Действие", "color": "#9C27B0"},
    "end_success": {"label": "Успех", "color": "#4CAF50"},
    "end_fail": {"label": "Провал", "color": "#F44336"},
}

NODE_W = 180
NODE_H = 70
PORT_R = 6  # Радиус порта


class PortItem(QGraphicsEllipseItem):
    """Точка соединения (порт) на границе узла."""

    def __init__(self, parent_node: 'NodeItem', is_output: bool = True):
        super().__init__(-PORT_R, -PORT_R, PORT_R * 2, PORT_R * 2, parent_node)
        self.parent_node = parent_node
        self.is_output = is_output

        self._color = QColor(COLORS["accent"])
        self._set_default_style()
        self.setZValue(2)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setAcceptHoverEvents(True)

    def _set_default_style(self):
        """Стиль по умолчанию — полупрозрачный."""
        c = QColor(self._color)
        c.setAlpha(80)
        self.setBrush(QBrush(c))
        self.setPen(QPen(QColor(self._color), 1))

    def set_highlighted(self, on: bool):
        """Подсветка порта при активном режиме соединения."""
        if on:
            self.setBrush(QBrush(self._color))
            self.setPen(QPen(QColor("white"), 2))
        else:
            self._set_default_style()

    def hoverEnterEvent(self, event):
        self.set_highlighted(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.set_highlighted(False)
        super().hoverLeaveEvent(event)

    def center_scene_pos(self) -> QPointF:
        """Координаты центра порта в координатах сцены."""
        return self.scenePos()


class NodeItem(QGraphicsRectItem):
    """
    Узел графа сценария.
    """

    def __init__(self, node_id: str | None = None, node_type: str = "scene",
                 title: str = "", x: float = 0, y: float = 0):
        super().__init__(0, 0, NODE_W, NODE_H)
        self.node_id = node_id or str(uuid.uuid4())[:8]
        self.node_type = node_type
        self.title = title or NODE_TYPES.get(node_type, {}).get("label", "Узел")
        self.description = ""
        self.task_type = ""  # Тип задания (только для question)

        self.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setZValue(1)

        # Визуал
        type_info = NODE_TYPES.get(node_type, NODE_TYPES["scene"])
        self._color = QColor(type_info["color"])

        self.setPen(QPen(self._color.darker(110), 2))
        self.setBrush(QBrush(QColor(COLORS["bg_elevated"])))

        # Заголовок
        self._title_item = QGraphicsTextItem(self)
        self._title_item.setDefaultTextColor(QColor(COLORS["text_primary"]))
        self._title_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._title_item.setPlainText(self.title)
        self._title_item.setPos(10, 8)
        self._title_item.setTextWidth(NODE_W - 20)

        # Подпись типа
        self._type_label = QGraphicsTextItem(self)
        self._type_label.setDefaultTextColor(self._color)
        self._type_label.setFont(QFont("Segoe UI", 8))
        self._type_label.setPlainText(type_info["label"])
        self._type_label.setPos(10, NODE_H - 22)

        # Порты
        self.input_port = PortItem(self, is_output=False)
        self.input_port.setPos(0, NODE_H / 2)  # Слева по центру

        self.output_port = PortItem(self, is_output=True)
        self.output_port.setPos(NODE_W, NODE_H / 2)  # Справа по центру

        # Список рёбер, подключённых к этому узлу
        self.edges: list = []

    def paint(self, painter: QPainter, option, widget=None):
        """Рисуем скруглённый прямоугольник с цветной полоской сверху."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()

        # Фон
        path = QPainterPath()
        path.addRoundedRect(r, 8, 8)
        painter.fillPath(path, QBrush(QColor(COLORS["bg_elevated"])))

        # Цветная полоска сверху
        bar = QPainterPath()
        bar.addRoundedRect(QRectF(r.x(), r.y(), r.width(), 6), 8, 8)
        painter.fillPath(bar, QBrush(self._color))

        # Обводка
        pen_color = self._color if self.isSelected() else QColor(COLORS["stroke_divider"])
        pen_width = 2 if self.isSelected() else 1
        painter.setPen(QPen(pen_color, pen_width))
        painter.drawRoundedRect(r, 8, 8)

    def hoverEnterEvent(self, event):
        self.input_port.set_highlighted(True)
        self.output_port.set_highlighted(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.input_port.set_highlighted(False)
        self.output_port.set_highlighted(False)
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Обновляем все подключённые рёбра
            for edge in self.edges:
                edge.update_path()
        return super().itemChange(change, value)

    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.setStyleSheet(f"""
            QMenu {{
                background: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['stroke_divider']};
                border-radius: 4px;
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

        edit_action = menu.addAction("✏️ Редактировать")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Удалить")

        action = menu.exec(event.screenPos())
        if action == edit_action:
            self._edit_node()
        elif action == delete_action:
            self._delete_node()

    def mouseDoubleClickEvent(self, event):
        self._edit_node()
        super().mouseDoubleClickEvent(event)

    def _edit_node(self):
        from .node_edit_dialog import NodeEditDialog
        data = {
            "type": self.node_type,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type,
        }
        dlg = NodeEditDialog(data)
        if dlg.exec():
            result = dlg.get_data()
            self.title = result.get("title", self.title)
            self.description = result.get("description", "")
            self.task_type = result.get("task_type", "")
            self._title_item.setPlainText(self.title)
            # Показываем тип задания для question
            type_info = NODE_TYPES.get(self.node_type, NODE_TYPES["scene"])
            label = type_info["label"]
            if self.task_type:
                from .node_edit_dialog import ATTACHABLE_TASKS
                task_name = next((t["name"] for t in ATTACHABLE_TASKS if t["id"] == self.task_type), "")
                if task_name:
                    label += f" • {task_name}"
            self._type_label.setPlainText(label)

    def _delete_node(self):
        scene = self.scene()
        if scene and hasattr(scene, 'remove_node'):
            scene.remove_node(self)

    def to_dict(self) -> dict:
        return {
            "id": self.node_id,
            "type": self.node_type,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type,
            "x": self.pos().x(),
            "y": self.pos().y(),
        }
