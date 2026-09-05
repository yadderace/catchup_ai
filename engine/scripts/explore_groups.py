"""Exploratory script for Task 3 (union-find group tracking).

Not a formal test (this phase has none by design) -- places a few stones by
hand and checks that group sizes come out right for adjacent vs. separate
stones, and that colors are tracked independently.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "engine"))

import catchup_engine as ce


def first_empty_non_neighbor(board, avoid_slots, avoid_neighbors_of):
    blocked = set(avoid_slots)
    for slot in avoid_neighbors_of:
        blocked.update(board.neighbors(slot))
    for slot in range(board.num_cells):
        if slot not in blocked and board.color_at(slot) == "empty":
            return slot
    raise RuntimeError("no candidate slot found -- board too small for this check")


def main() -> None:
    board = ce.Board(side_length=4)

    # --- Case 1: two adjacent white stones merge into one group of size 2 ---
    slot_a = 0
    slot_b = board.neighbors(slot_a)[0]
    board.place_stone(slot_a, "white")
    board.place_stone(slot_b, "white")
    print("after 2 adjacent white stones:", board.sorted_group_sizes("white"))
    assert board.largest_group("white") == 2
    assert board.sorted_group_sizes("white") == [2]

    # --- Case 2: a separate white stone (touching neither) stays its own group ---
    slot_c = first_empty_non_neighbor(board, [slot_a, slot_b], [slot_a, slot_b])
    board.place_stone(slot_c, "white")
    print("after 1 separate white stone:", board.sorted_group_sizes("white"))
    assert board.sorted_group_sizes("white") == [2, 1]
    assert board.largest_group("white") == 2

    # --- Case 3: extending the pair merges it up to size 3 ---
    slot_d = next(
        n for n in board.neighbors(slot_b)
        if n != slot_a and board.color_at(n) == "empty"
    )
    board.place_stone(slot_d, "white")
    print("after extending the pair:", board.sorted_group_sizes("white"))
    assert board.sorted_group_sizes("white") == [3, 1]
    assert board.largest_group("white") == 3

    # --- Case 4: black is tracked independently of white ---
    slot_black = first_empty_non_neighbor(board, [], [])
    board.place_stone(slot_black, "black")
    print("black groups:", board.sorted_group_sizes("black"))
    assert board.sorted_group_sizes("black") == [1]
    assert board.largest_group("white") == 3  # unaffected by black's move

    # --- Case 5: placing on an occupied cell is rejected ---
    try:
        board.place_stone(slot_a, "black")
        raise AssertionError("expected placing on an occupied cell to raise")
    except ValueError as exc:
        print("occupied-cell placement correctly rejected:", exc)

    print("\nall checks passed")


if __name__ == "__main__":
    main()
