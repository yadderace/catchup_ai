"""Exploratory script for Task 5 (legal move generation).

Not a formal test (this phase has none by design) -- checks that
legal_moves() returns only 1-cell moves on the opening move, and that
afterwards it returns every combination of empty cells sized between
min_allowed and max_allowed (verified against math.comb, not just eyeballed).
"""

import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "engine"))

import catchup_engine as ce


def check_sizes_and_count(state, label):
    start = time.perf_counter()
    moves = state.legal_moves()
    elapsed = time.perf_counter() - start

    sizes = {len(m) for m in moves}
    empty_count = sum(
        1 for i in range(state.board.num_cells) if state.board.color_at(i) == "empty"
    )
    expected_total = sum(
        math.comb(empty_count, k)
        for k in range(state.min_allowed, state.max_allowed + 1)
        if k <= empty_count
    )
    print(
        f"{label}: min_allowed={state.min_allowed} max_allowed={state.max_allowed} "
        f"move sizes present={sorted(sizes)} total_moves={len(moves)} expected={expected_total} "
        f"elapsed={elapsed:.3f}s"
    )
    assert sizes <= set(range(state.min_allowed, state.max_allowed + 1))
    assert len(moves) == expected_total
    return moves


def main() -> None:
    side_length = 7  # 127 cells -- the real board size, to see actual performance

    # --- Opening move: only 1-cell moves, one per empty cell ---
    state = ce.GameState(side_length=side_length)
    moves = check_sizes_and_count(state, f"opening (side_length={side_length})")
    assert all(len(m) == 1 for m in moves)
    assert len(moves) == state.board.num_cells  # C(127, 1) = 127

    # --- After the opening: normal allowance (sizes 1-2) ---
    state = state.apply_move(moves[0])
    check_sizes_and_count(state, "after opening (normal allowance)")

    # --- Force a catch-up bonus, then check sizes 1-3 all appear ---
    state2 = ce.GameState(side_length=side_length)
    lut = {state2.board.coords(s): s for s in range(state2.board.num_cells)}

    state2 = state2.apply_move([lut[(0, 0)]])  # White opens at the center

    b1 = lut[(1, 0)]
    b2 = next(n for n in state2.board.neighbors(b1) if state2.board.color_at(n) == "empty")
    state2 = state2.apply_move([b1, b2])  # Black: 2 adjacent stones -> new record
    assert state2.max_allowed == 3, "expected the catch-up bonus for White"

    moves2 = check_sizes_and_count(state2, "after black's 2-stone record (white has the bonus)")
    assert sorted({len(m) for m in moves2}) == [1, 2, 3]

    print("\nall checks passed")


if __name__ == "__main__":
    main()
