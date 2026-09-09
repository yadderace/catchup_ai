import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from board_widget import BoardWidget
from engine_loader import catchup_engine

SIDE_LENGTH = 7


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Catchup")
        self.resize(900, 650)

        self.state = catchup_engine.GameState(side_length=SIDE_LENGTH)
        # (q, r) <-> backend slot number, fixed for the whole game (only cell
        # contents change between states, never the shape/slot numbering).
        self._slot_to_coords = [self.state.board.coords(slot) for slot in range(self.state.board.num_cells)]
        self._coords_to_slot = {coord: slot for slot, coord in enumerate(self._slot_to_coords)}

        self.board_widget = BoardWidget(SIDE_LENGTH)

        self.turn_label = QLabel()
        self.allowance_label = QLabel()
        self.white_group_label = QLabel()
        self.black_group_label = QLabel()
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #b00020;")
        self.confirm_button = QPushButton("Confirm move")
        self.confirm_button.clicked.connect(self._on_confirm_move)

        side_panel = QVBoxLayout()
        for label in (self.turn_label, self.allowance_label, self.white_group_label, self.black_group_label):
            side_panel.addWidget(label)
        side_panel.addWidget(self.confirm_button)
        side_panel.addWidget(self.status_label)
        side_panel.addStretch()

        side_panel_widget = QWidget()
        side_panel_widget.setLayout(side_panel)
        side_panel_widget.setFixedWidth(220)

        layout = QHBoxLayout()
        layout.addWidget(self.board_widget, stretch=1)
        layout.addWidget(side_panel_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self._refresh_board()
        self._refresh_labels()

    def _on_confirm_move(self) -> None:
        selected = self.board_widget.selected_coords()
        count = len(selected)
        if not (self.state.min_allowed <= count <= self.state.max_allowed):
            self.status_label.setText(
                f"Select between {self.state.min_allowed} and {self.state.max_allowed} "
                f"empty cells (you selected {count})."
            )
            return

        move = [self._coords_to_slot[coord] for coord in selected]
        self.state = self.state.apply_move(move)
        self.status_label.setText("")

        self._refresh_board()
        self._refresh_labels()

        if self.state.is_terminal:
            self._announce_winner()

    def _refresh_board(self) -> None:
        colors = self.state.board.cells()
        colors_by_coord = {self._slot_to_coords[slot]: color for slot, color in enumerate(colors)}
        self.board_widget.set_cell_colors(colors_by_coord)

    def _refresh_labels(self) -> None:
        if self.state.is_terminal:
            self.turn_label.setText("Game over")
            self.allowance_label.setText("-")
        else:
            self.turn_label.setText(f"Turn: {self.state.to_move.capitalize()}")
            if self.state.max_allowed == 1:
                allowance_text = "Stones to place: 1 (opening move)"
            elif self.state.max_allowed == 3:
                allowance_text = "Stones to place: 1-3 (catch-up bonus!)"
            else:
                allowance_text = f"Stones to place: {self.state.min_allowed}-{self.state.max_allowed}"
            self.allowance_label.setText(allowance_text)

        self.white_group_label.setText(f"White largest group: {self.state.board.largest_group('white')}")
        self.black_group_label.setText(f"Black largest group: {self.state.board.largest_group('black')}")

    def _announce_winner(self) -> None:
        winner = self.state.winner
        QMessageBox.information(self, "Game over", f"{winner.capitalize()} wins!")
        self.board_widget.setEnabled(False)
        self.confirm_button.setEnabled(False)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
