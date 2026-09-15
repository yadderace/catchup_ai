"""Benchmark script for the minimax search (alpha-beta pruned).

Not a formal test (this phase has none by design) -- runs find_best_move
at a few (depth, candidate_cap) combinations on the real side-length-7
board, from a couple of different game states, and prints a table of
nodes visited and elapsed time.
"""

import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "engine"))

import catchup_engine as ce

SIDE_LENGTH = 7
DEPTHS = (1, 2, 3, 4, 5)
CANDIDATE_CAPS = (6, 10)
# (depth=5, cap=10) alone is projected at 20+ minutes (~80M nodes, extrapolated
# from the measured growth rate) -- skipped as impractical for a benchmark
# that's meant to be run and reviewed interactively.
SKIP_COMBINATIONS = {(5, 10)}
RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"
RESULTS_FILE = RESULTS_DIR / "benchmark_minimax.txt"

_output_lines: list[str] = []


def emit(line: str = "") -> None:
    print(line)
    _output_lines.append(line)


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
    emit(f"\n=== {label} (to_move={state.to_move}, max_allowed={state.max_allowed}) ===")
    header = f"{'depth':>5} {'cap':>4} {'nodes':>10} {'time (s)':>10} {'score':>10}  move"
    emit(header)
    emit("-" * len(header))
    for depth in DEPTHS:
        for cap in CANDIDATE_CAPS:
            if (depth, cap) in SKIP_COMBINATIONS:
                emit(f"{depth:>5} {cap:>4}  (skipped -- impractically slow, see SKIP_COMBINATIONS)")
                continue
            start = time.perf_counter()
            result = ce.find_best_move(state, depth, cap)
            elapsed = time.perf_counter() - start
            emit(
                f"{depth:>5} {cap:>4} {result.nodes_visited:>10} {elapsed:>10.3f} "
                f"{result.score:>10.2f}  {result.move}"
            )


def main() -> None:
    emit(f"benchmark run: {datetime.now().isoformat(timespec='seconds')}")
    run("opening", opening_state())
    run("a few moves in", midgame_state())

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_FILE.write_text("\n".join(_output_lines) + "\n")
    print(f"\nresults written to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
