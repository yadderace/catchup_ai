"""Exploratory script for candidate-pruned move generation.

Not a formal test (this phase has none by design) -- shows the uncapped
legal_moves() count for a normal turn and a catch-up-bonus turn on the
real side-length-7 board (same numbers Phase 1 already measured), then
the capped count at a couple of candidate_cap values, and prints the
actual candidate cells chosen in one case so they can be eyeballed for
clustering near existing stones.

Note: ranked_candidate_cells() is a Phase 2 code challenge -- the capped
sections below will raise until that function is implemented.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "engine"))

import catchup_engine as ce

SIDE_LENGTH = 7
CANDIDATE_CAPS = (6, 10)


def timed_len(callable_) -> tuple[int, float]:
    start = time.perf_counter()
    result = callable_()
    elapsed = time.perf_counter() - start
    return len(result), elapsed


def main() -> None:
    # --- Uncapped baseline (same numbers Phase 1 measured: 127 / 8,001 / 317,874) ---
    opening_state = ce.GameState(side_length=SIDE_LENGTH)
    count, elapsed = timed_len(opening_state.legal_moves)
    print(f"opening, uncapped: {count} legal moves ({elapsed:.3f}s)")

    normal_state = opening_state.apply_move(opening_state.legal_moves()[0])
    count, elapsed = timed_len(normal_state.legal_moves)
    print(f"normal turn, uncapped: {count} legal moves ({elapsed:.3f}s)")

    board = normal_state.board
    b1 = next(s for s in range(board.num_cells) if board.color_at(s) == "empty")
    b2 = next(n for n in board.neighbors(b1) if board.color_at(n) == "empty")
    bonus_state = normal_state.apply_move([b1, b2])
    assert bonus_state.max_allowed == 3, "expected this move to trigger the catch-up bonus"
    count, elapsed = timed_len(bonus_state.legal_moves)
    print(f"catch-up bonus turn, uncapped: {count} legal moves ({elapsed:.3f}s)")

    # --- Capped counts (candidate-pruned) ---
    print()
    for cap in CANDIDATE_CAPS:
        count, elapsed = timed_len(lambda cap=cap: normal_state.legal_moves(cap))
        print(f"normal turn, candidate_cap={cap}: {count} legal moves ({elapsed:.3f}s)")
        count, elapsed = timed_len(lambda cap=cap: bonus_state.legal_moves(cap))
        print(f"catch-up bonus turn, candidate_cap={cap}: {count} legal moves ({elapsed:.3f}s)")

    # --- Eyeball the actual candidate cells chosen, in one case ---
    cap = 10
    candidates = ce.ranked_candidate_cells(bonus_state.board, cap)
    print(f"\ncandidate cells (cap={cap}) on the bonus-turn board ({len(candidates)} returned):")
    for slot in candidates:
        print(" ", slot, bonus_state.board.coords(slot))

    print("\nall checks passed")


if __name__ == "__main__":
    main()
