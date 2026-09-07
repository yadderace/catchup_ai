"""Exploratory script for Task 6: random self-play.

Not a formal test (this phase has none by design) -- plays full games with
random legal moves so the turn-by-turn behavior (allowance changes,
catch-up bonus, end-of-game/winner) can be reviewed by eye across many
games, not just the hand-picked scenarios in the earlier explore_*.py
scripts.

Usage:
    python engine/scripts/manual_playthrough.py [num_games]

num_games defaults to NUM_GAMES below if not given on the command line.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "engine"))

import catchup_engine as ce

SIDE_LENGTH = 7
NUM_GAMES = 3


def play_one_game(side_length: int, game_index: int) -> ce.GameState:
    state = ce.GameState(side_length=side_length)
    print(f"\n=== Game {game_index} (side_length={side_length}, {state.board.num_cells} cells) ===")

    turn = 0
    while not state.is_terminal:
        turn += 1
        mover = state.to_move
        move = random.choice(state.legal_moves())
        coords = [state.board.coords(slot) for slot in move]

        state = state.apply_move(move)
        print(
            f"turn {turn:>3}: {mover:<5} plays {len(move)} stone(s) "
            f"slots={move} coords={coords} -> next max_allowed={state.max_allowed}"
        )

    print(f"-- game {game_index} over after {turn} turns --")
    print(f"   winner: {state.winner}")
    print(f"   white groups (desc): {state.board.sorted_group_sizes('white')}")
    print(f"   black groups (desc): {state.board.sorted_group_sizes('black')}")
    return state


def main() -> None:
    num_games = int(sys.argv[1]) if len(sys.argv) > 1 else NUM_GAMES

    wins = {"white": 0, "black": 0}
    for game_index in range(1, num_games + 1):
        final_state = play_one_game(SIDE_LENGTH, game_index)
        wins[final_state.winner] += 1

    print(f"\n=== {num_games} game(s) played -- white: {wins['white']}, black: {wins['black']} ===")


if __name__ == "__main__":
    main()
