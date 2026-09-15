"""Benchmark script for plain classic minimax (Task 3).

Not a formal test (this phase has none by design) -- runs find_best_move
at a few (depth, candidate_cap) combinations on the real side-length-7
board, from a couple of different game states, and prints a table of
nodes visited and elapsed time. This is the actual deliverable: a
written-down "before" baseline (plain minimax) that task 4's alpha-beta
version gets benchmarked against.

Note: minimax() is a Phase 2 code challenge -- this script will raise
until that function is implemented.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "engine"))

import catchup_engine as ce

SIDE_LENGTH = 7
DEPTHS = (1, 2)
CANDIDATE_CAPS = (6, 10)


def opening_state():
    return ce.GameState(side_length=SIDE_LENGTH)


def midgame_state():
    """A few moves in: White opens, Black replies with 2 adjacent stones
    (triggering the catch-up bonus), then one more move each side."""
    state = ce.GameState(side_length=SIDE_LENGTH)
    lut = {state.board.coords(s): s for s in range(state.board.num_cells)}
    state = state.apply_move([lut[(0, 0)]])  # White opens at the center

    b1 = next(s for s in range(state.board.num_cells) if state.board.color_at(s) == "empty")
    b2 = next(n for n in state.board.neighbors(b1) if state.board.color_at(n) == "empty")
    state = state.apply_move([b1, b2])  # Black plays 2 adjacent stones

    state = state.apply_move(state.legal_moves()[0])  # White replies
    state = state.apply_move(state.legal_moves()[0])  # Black replies

    return state


def run(label, state):
    print(f"\n=== {label} (to_move={state.to_move}, max_allowed={state.max_allowed}) ===")
    header = f"{'depth':>5} {'cap':>4} {'nodes':>10} {'time (s)':>10} {'score':>10}  move"
    print(header)
    print("-" * len(header))
    for depth in DEPTHS:
        for cap in CANDIDATE_CAPS:
            start = time.perf_counter()
            result = ce.find_best_move(state, depth, cap)
            elapsed = time.perf_counter() - start
            print(
                f"{depth:>5} {cap:>4} {result.nodes_visited:>10} {elapsed:>10.3f} "
                f"{result.score:>10.2f}  {result.move}"
            )


def main() -> None:
    run("opening", opening_state())
    run("a few moves in", midgame_state())


if __name__ == "__main__":
    main()
