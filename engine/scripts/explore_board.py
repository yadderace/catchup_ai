"""Exploratory script for the catchup_engine bindings (Task 1 + Task 2).

Not a formal test (this phase has none by design) -- just a quick, runnable
check that ping() and the Board bindings behave as expected.
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "engine"))

import catchup_engine as ce


def main() -> None:
    print("ping():", ce.ping())

    n = 7
    board = ce.Board(side_length=n)
    expected_cells = 3 * n * n - 3 * n + 1
    print(f"\nside_length={n} -> num_cells={board.num_cells} (expected {expected_cells})")

    counts = Counter(len(board.neighbors(slot)) for slot in range(board.num_cells))
    print("neighbor-count distribution {neighbor_count: how_many_cells}:", dict(sorted(counts.items())))

    corners = [slot for slot in range(board.num_cells) if len(board.neighbors(slot)) == 3]
    print(f"\ncorners ({len(corners)} expected 6):")
    for slot in corners:
        print(" slot", slot, "coords", board.coords(slot), "neighbors", sorted(board.neighbors(slot)))

    center = board.num_cells // 2
    print("\na sample interior cell:")
    print(" slot", center, "coords", board.coords(center), "neighbors", sorted(board.neighbors(center)),
          "color", board.color_at(center))


if __name__ == "__main__":
    main()
