"""Exploratory script for GameState's turn state machine, including the
corrected catch-up bonus trigger (Phase 2, task 0).

Not a formal test (this phase has none by design) -- plays a hand-built
sequence of moves on a side-length-5 board and checks max_allowed at each
step against the corrected rule: the bonus fires only on the transition
from "mover strictly behind the opponent's largest group" to "mover level
or ahead of it," never merely for staying ahead or extending an existing
lead.
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

    # Turn 2: Black plays 2 adjacent stones -> Black goes from 0 (behind
    # White's 1) to 2 (ahead of White's 1) -> catches up -> White gets the bonus.
    state = state.apply_move([lut[(2, 2)], lut[(1, 2)]])
    show("after black plays 2 adjacent stones", state)
    print(" black largest group:", state.board.largest_group("black"))
    assert state.board.largest_group("black") == 2
    assert state.to_move == "white"
    assert state.max_allowed == 3

    # Turn 3: White uses the bonus: 3 stones, two adjacent + one separate,
    # all clear of White's existing center stone (the doc's own example
    # picks (-1,0), which is actually adjacent to the center (0,0) stone
    # from turn 1 -- that merges into a group of 3, not 2, so different
    # coordinates are used here instead).
    #
    # White goes from 1 (behind Black's 2) to 2 (LEVEL with Black's 2).
    # Under the corrected rule this IS a catch-up (behind -> level-or-ahead),
    # so Black now gets the bonus -- under the old "new overall record"
    # rule this did NOT trigger (2 wasn't a new record), which was the bug.
    state = state.apply_move([lut[(-3, 1)], lut[(-3, 2)], lut[(3, -2)]])
    show("after white uses the bonus (3 stones)", state)
    print(" white largest group:", state.board.largest_group("white"))
    assert state.board.largest_group("white") == 2
    assert state.to_move == "black"
    assert state.max_allowed == 3, "corrected rule: behind (1) -> level (2) with black's 2 must trigger the bonus"

    # Turn 4: Black was already LEVEL (2 vs White's 2) going into this move,
    # not behind -- so extending its own group (2 -> 3) must NOT re-trigger
    # the bonus, even though 3 > 2 afterwards.
    state = state.apply_move([lut[(0, 2)]])
    show("after black extends its group (level -> ahead)", state)
    print(" black largest group:", state.board.largest_group("black"))
    assert state.board.largest_group("black") == 3
    assert state.to_move == "white"
    assert state.max_allowed == 2, "mover was already level, not behind -- extending the lead must not re-trigger"

    # Turn 5: White plays 2 isolated stones (not extending its own group) --
    # just advances the game so Black gets a normal (non-bonus) turn next,
    # setting up turn 6 below. White stays behind Black (2 < 3) throughout.
    state = state.apply_move([lut[(-2, -2)], lut[(-4, 0)]])
    show("after white plays 2 isolated stones", state)
    assert state.to_move == "black"
    assert state.max_allowed == 2, "white stayed behind (2 < 3) and didn't catch up -- no bonus"

    # Turn 6: Black was already STRICTLY AHEAD (3 vs White's 2) going into
    # this move -- extending its group further (3 -> 4) must NOT trigger
    # the bonus either. This is the case most likely to be implemented
    # wrong (easy to accidentally trigger on "still bigger than before").
    state = state.apply_move([lut[(-1, 2)]])
    show("after black extends further while already ahead", state)
    print(" black largest group:", state.board.largest_group("black"))
    assert state.board.largest_group("black") == 4
    assert state.to_move == "white"
    assert state.max_allowed == 2, "mover was already ahead (3 > 2) -- extending the lead further must not re-trigger"

    print("\nall checks passed")


if __name__ == "__main__":
    main()
