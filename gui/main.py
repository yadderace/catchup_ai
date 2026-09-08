"""Application entry point."""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from board_widget import BoardWidget
from engine_loader import catchup_engine

SIDE_LENGTH = 7


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Catchup")
        self.resize(800, 600)
        self.setCentralWidget(BoardWidget(SIDE_LENGTH))

        state = catchup_engine.GameState(side_length=SIDE_LENGTH)
        print(
            f"initial state: to_move={state.to_move} "
            f"min_allowed={state.min_allowed} max_allowed={state.max_allowed}"
        )


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
