# ui/task_constructor/scenario_builder/edge_item.py
"""
Ребро графа сценария — кривая Безье с наконечником-стрелкой и текстовой подписью.
"""
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsTextItem, QMenu, QInputDialog
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import (
    QPen, QColor, QPainterPath, QBrush, QFont,
    QPolygonF, QPainter
)

from ui.styles.theme import COLORS

import math


class EdgeItem(QGraphicsPathItem):
    """
    Ребро между двумя NodeItem. Рисуется как кривая Безье от output порта
    одного узла к input порту другого.
    """

    def __init__(self, source_node, target_node, label: str = ""):
        super().__init__()
        self.source_node = source_node
        self.target_node = target_node
        self.label = label

        self.setZValue(0)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Стиль линии
        self._pen_normal = QPen(QColor(COLORS["stroke_divider"]), 2)
        self._pen_normal.setCapStyle(Qt.PenCapStyle.RoundCap)
        self._pen_hover = QPen(QColor(COLORS["accent"]), 2.5)
        self._pen_hover.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.setPen(self._pen_normal)

        # Подпись на ребре
        self._label_item = QGraphicsTextItem(self)
        self._label_item.setDefaultTextColor(QColor(COLORS["text_secondary"]))
        self._label_item.setFont(QFont("Segoe UI", 9))
        self._label_item.setPlainText(self.label)

        # Стрелка (треугольник)
        self._arrow_size = 10

        # Регистрируем ребро в узлах
        source_node.edges.append(self)
        target_node.edges.append(self)

        self.update_path()

    def update_path(self):
        """Пересчитывает кривую Безье между портами узлов."""
        p1 = self.source_node.output_port.center_scene_pos()
        p2 = self.target_node.input_port.center_scene_pos()

        dx = abs(p2.x() - p1.x()) * 0.5
        dx = max(dx, 50)

        path = QPainterPath(p1)
        path.cubicTo(
            p1.x() + dx, p1.y(),
            p2.x() - dx, p2.y(),
            p2.x(), p2.y()
        )
        self.setPath(path)

        # Позиция подписи — на середине кривой
        mid = path.pointAtPercent(0.5)
        self._label_item.setPos(mid.x() - 20, mid.y() - 20)

    def paint(self, painter: QPainter, option, widget=None):
        """Рисуем кривую + стрелку на конце."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Линия
        painter.setPen(self.pen())
        painter.drawPath(self.path())

        # Стрелка на конце
        path = self.path()
        if path.length() > 0:
            end = path.pointAtPercent(1.0)
            pre = path.pointAtPercent(max(0, 1.0 - 20 / path.length()))

            angle = math.atan2(end.y() - pre.y(), end.x() - pre.x())
            s = self._arrow_size

            p1 = QPointF(
                end.x() - s * math.cos(angle - math.pi / 6),
                end.y() - s * math.sin(angle - math.pi / 6)
            )
            p2 = QPointF(
                end.x() - s * math.cos(angle + math.pi / 6),
                end.y() - s * math.sin(angle + math.pi / 6)
            )

            arrow = QPolygonF([end, p1, p2])
            painter.setBrush(QBrush(self.pen().color()))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(arrow)

    def hoverEnterEvent(self, event):
        self.setPen(self._pen_hover)
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPen(self._pen_normal)
        self.update()
        super().hoverLeaveEvent(event)

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

        edit_action = menu.addAction("✏️ Изменить подпись")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Удалить связь")

        action = menu.exec(event.screenPos())
        if action == edit_action:
            self._edit_label()
        elif action == delete_action:
            self._delete_edge()

    def mouseDoubleClickEvent(self, event):
        self._edit_label()
        super().mouseDoubleClickEvent(event)

    def _edit_label(self):
        text, ok = QInputDialog.getText(
            None, "Подпись связи",
            "Текст перехода:",
            text=self.label
        )
        if ok:
            self.label = text.strip()
            self._label_item.setPlainText(self.label)

    def _delete_edge(self):
        scene = self.scene()
        if scene and hasattr(scene, 'remove_edge'):
            scene.remove_edge(self)

    def to_dict(self) -> dict:
        return {
            "source": self.source_node.node_id,
            "target": self.target_node.node_id,
            "label": self.label,
        }
