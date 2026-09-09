from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget

from hex_geometry import axial_to_pixel, hex_cells, hex_corners, pixel_to_axial

BACKGROUND_COLOR = "#f0f0f0"
CELL_COLORS = {
    "empty": "#d9c7a3",
    "white": "#fefefe",
    "black": "#202020",
}
CELL_BORDER_COLOR = "#333333"
SELECTED_BORDER_COLOR = "#1e88e5"
MARGIN = 20


class BoardWidget(QWidget):
    def __init__(self, side_length: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.side_length = side_length
        self.cells = hex_cells(side_length)  # every valid (q, r) on this board
        self._cell_set = set(self.cells)
        self.selected: set[tuple[int, int]] = set()  # cells the user has clicked
        self.cell_colors: dict[tuple[int, int], str] = {}  # (q, r) -> "empty"/"white"/"black", set by the caller
        self.setMinimumSize(400, 400)

    def set_cell_colors(self, colors_by_coord: dict[tuple[int, int], str]) -> None:
        """Replaces the board's cell colors (from the backend) and clears any selection."""
        self.cell_colors = colors_by_coord
        self.selected.clear()
        self.update()

    def selected_coords(self) -> set[tuple[int, int]]:
        return set(self.selected)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(BACKGROUND_COLOR))

        # Same hex_size/center every cell is drawn with
        hex_size, center_x, center_y = self._layout()

        normal_pen = QPen(QColor(CELL_BORDER_COLOR))
        normal_pen.setWidthF(1.5)
        selected_pen = QPen(QColor(SELECTED_BORDER_COLOR))
        selected_pen.setWidthF(3.5)

        for cell in self.cells:
            q, r = cell
            color = self.cell_colors.get(cell, "empty")
            painter.setPen(selected_pen if cell in self.selected else normal_pen)
            painter.setBrush(QBrush(QColor(CELL_COLORS[color])))
            cell_x, cell_y = axial_to_pixel(q, r, hex_size)
            corners = hex_corners(center_x + cell_x, center_y + cell_y, hex_size * 0.98)
            painter.drawPolygon(QPolygonF([QPointF(x, y) for x, y in corners]))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Map the click's pixel position back to a board cell, then toggle
        # its selection -- only empty cells can be selected.
        hex_size, center_x, center_y = self._layout()
        pos = event.position()
        cell = pixel_to_axial(pos.x() - center_x, pos.y() - center_y, hex_size)

        if cell in self._cell_set and self.cell_colors.get(cell, "empty") == "empty":
            if cell in self.selected:
                self.selected.remove(cell)
            else:
                self.selected.add(cell)
            self.update()  # schedules a repaint so the new selection shows up

    def _layout(self) -> tuple[float, float, float]:
        """(hex_size, center_x, center_y) shared by painting and hit-testing."""
        return self._fit_hex_size(), self.width() / 2, self.height() / 2

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
