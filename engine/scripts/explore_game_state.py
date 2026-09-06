"""Exploratory script for Task 4 (GameState turn state machine).

Not a formal test (this phase has none by design) -- replays the worked
example from the technical design doc, section 1.3, on a side-length-5
board, and checks that max_allowed transitions correctly:
opening (1) -> normal (2) -> catch-up bonus (3) -> normal (2).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "engine"))

import catchup_engine as ce


def qr_to_slot(board):
    return {board.coords(slot): slot for slot in range(board.num_cells)}


def show(label, state):
    print(
        f"{label}: to_move={state.to_move} min_allowed={state.min_allowed} "
        f"max_allowed={state.max_allowed} is_terminal={state.is_terminal}"
    )


def main() -> None:
    state = ce.GameState(side_length=5)
    show("start (opening)", state)
    assert state.to_move == "white"
    assert state.min_allowed == 1
    assert state.max_allowed == 1

    lut = qr_to_slot(state.board)

    # Turn 1: White opens with 1 stone at the center.
    state = state.apply_move([lut[(0, 0)]])
    show("after white opens at the center", state)
    assert state.to_move == "black"
    assert state.max_allowed == 2  # opening never triggers the bonus

    # Turn 2: Black plays 2 adjacent stones -> largest group becomes 2,
    # a new record (previous largest was White's 1) -> White gets the bonus.
    state = state.apply_move([lut[(2, 2)], lut[(1, 2)]])
    show("after black plays 2 adjacent stones", state)
    print(" black largest group:", state.board.largest_group("black"))
    assert state.board.largest_group("black") == 2
    assert state.to_move == "white"
    assert state.max_allowed == 3

    # Turn 3: White uses the bonus: 3 stones, two adjacent + one separate,
    # all clear of White's existing center stone (the doc's own example
    # picks (-1,0), which is actually adjacent to the center (0,0) stone
    # from turn 1 -- that merges into a group of 3, not the 2 its table
    # claims, since it didn't account for the already-accumulated board).
    # Largest White group becomes 2 -- not a new record (2 already existed) -> Black stays normal.
    state = state.apply_move([lut[(-3, 1)], lut[(-3, 2)], lut[(3, -2)]])
    show("after white uses the bonus (3 stones)", state)
    print(" white largest group:", state.board.largest_group("white"))
    assert state.board.largest_group("white") == 2
    assert state.to_move == "black"
    assert state.max_allowed == 2

    print("\nall checks passed")


if __name__ == "__main__":
    main()
