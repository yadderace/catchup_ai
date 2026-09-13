"""Exploratory script for the evaluate() code challenge.

Not a formal test (this phase has none by design) -- builds a few
hand-picked GameState positions via apply_move (same style as Phase 1's
scripts) and checks that evaluate() orders them the way a human would
expect: a clearly-ahead position scores in the ahead color's favor, a
tied position scores close to zero, and a terminal position scores far
more extreme than any non-terminal position, in the winner's favor.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "engine"))

import catchup_engine as ce


def qr_to_slot(board):
    return {board.coords(slot): slot for slot in range(board.num_cells)}


def build_lopsided_position():
    """White grows one connected chain of 5; Black gets 4 isolated singletons.
    Non-terminal (side length 5, 61 cells, only 9 occupied)."""
    state = ce.GameState(side_length=5)
    lut = qr_to_slot(state.board)

    state = state.apply_move([lut[(0, 0)]])  # White opens, starting its chain

    white_extensions = [(1, 0), (2, 0), (3, 0), (4, 0)]
    black_singletons = [(-4, 0), (-4, 4), (0, -4), (0, 4)]  # mutually non-adjacent, far from White's chain
    wi = bi = 0
    while wi < len(white_extensions) or bi < len(black_singletons):
        if state.to_move == "white":
            state = state.apply_move([lut[white_extensions[wi]]])
            wi += 1
        else:
            state = state.apply_move([lut[black_singletons[bi]]])
            bi += 1

    assert not state.is_terminal
    assert state.board.largest_group("white") == 5
    assert state.board.largest_group("black") == 1
    return state


def build_even_position():
    """White and Black each grow their own separate chain of 3 -- an exactly
    tied position (both largest groups are 3). Non-terminal."""
    state = ce.GameState(side_length=5)
    lut = qr_to_slot(state.board)

    state = state.apply_move([lut[(0, 0)]])  # White opens
    state = state.apply_move([lut[(0, 4)]])  # Black starts its own chain
    state = state.apply_move([lut[(1, 0)]])  # White extends
    state = state.apply_move([lut[(-1, 4)]])  # Black extends
    state = state.apply_move([lut[(2, 0)]])  # White extends
    state = state.apply_move([lut[(-2, 4)]])  # Black extends

    assert not state.is_terminal
    assert state.board.largest_group("white") == 3
    assert state.board.largest_group("black") == 3
    return state


def build_terminal_position():
    """Fills a tiny (side length 2, 7 cells) board completely, deterministically."""
    state = ce.GameState(side_length=2)
    while not state.is_terminal:
        state = state.apply_move(state.legal_moves()[0])
    return state


def main() -> None:
    # --- Clearly ahead: White (largest group 5) vs Black (largest group 1) ---
    ahead_state = build_lopsided_position()
    score_white_ahead = ce.evaluate(ahead_state, "white")
    score_black_ahead = ce.evaluate(ahead_state, "black")
    print(f"lopsided position: eval(white)={score_white_ahead}  eval(black)={score_black_ahead}")
    assert score_white_ahead > 0, "White is clearly ahead -- should score positive for White"
    assert score_black_ahead < 0, "White is clearly ahead -- should score negative for Black"

    # --- Roughly even: both largest groups tied at 3 ---
    even_state = build_even_position()
    score_white_even = ce.evaluate(even_state, "white")
    score_black_even = ce.evaluate(even_state, "black")
    print(f"even position:     eval(white)={score_white_even}  eval(black)={score_black_even}")
    assert abs(score_white_even) < abs(score_white_ahead), (
        "a tied position should score much closer to zero than a clearly lopsided one"
    )

    # --- Terminal: score must be far more extreme than any non-terminal score ---
    terminal_state = build_terminal_position()
    winner = terminal_state.winner
    loser = "black" if winner == "white" else "white"
    score_winner = ce.evaluate(terminal_state, winner)
    score_loser = ce.evaluate(terminal_state, loser)
    print(f"terminal position: eval({winner})={score_winner}  eval({loser})={score_loser}  (winner: {winner})")
    assert score_winner > 0, "the winner's own perspective must score positive"
    assert score_loser < 0, "the loser's own perspective must score negative"
    assert abs(score_winner) > abs(score_white_ahead), (
        "a certain win must outweigh any non-terminal heuristic score in magnitude"
    )
    assert abs(score_loser) > abs(score_white_ahead), (
        "a certain loss must outweigh any non-terminal heuristic score in magnitude"
    )

    print("\nall checks passed")


if __name__ == "__main__":
    main()
