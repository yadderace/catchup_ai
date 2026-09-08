from PySide6.QtCore import QPointF
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget

from hex_geometry import axial_to_pixel, hex_cells, hex_corners

BACKGROUND_COLOR = "#f0f0f0"
EMPTY_CELL_COLOR = "#d9c7a3"
CELL_BORDER_COLOR = "#333333"
MARGIN = 20


class BoardWidget(QWidget):
    def __init__(self, side_length: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.side_length = side_length
        self.cells = hex_cells(side_length)
        self.setMinimumSize(400, 400)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(BACKGROUND_COLOR))

        hex_size = self._fit_hex_size()
        center_x = self.width() / 2
        center_y = self.height() / 2

        pen = QPen(CELL_BORDER_COLOR)
        pen.setWidthF(1.5)
        painter.setPen(pen)
        painter.setBrush(QBrush(EMPTY_CELL_COLOR))

        for q, r in self.cells:
            cell_x, cell_y = axial_to_pixel(q, r, hex_size)
            corners = hex_corners(center_x + cell_x, center_y + cell_y, hex_size * 0.98)
            painter.drawPolygon(QPolygonF([QPointF(x, y) for x, y in corners]))

    def _fit_hex_size(self) -> float:
        """Largest hex_size that keeps the whole board within the widget, with a margin."""
        centers = [axial_to_pixel(q, r, 1.0) for q, r in self.cells]
        xs = [x for x, _ in centers]
        ys = [y for _, y in centers]
        # Pad by 1 hex_size unit to account for each cell's own corner reach.
        board_width = (max(xs) - min(xs)) + 2.0
        board_height = (max(ys) - min(ys)) + 2.0

        available_width = self.width() - 2 * MARGIN
        available_height = self.height() - 2 * MARGIN
        return min(available_width / board_width, available_height / board_height)
