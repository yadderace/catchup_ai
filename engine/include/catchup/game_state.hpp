#pragma once

#include <vector>

#include "catchup/board.hpp"

namespace catchup {

// Turn-based state machine on top of a Board: whose turn it is, how many
// stones they may place, and full-board/winner detection.
class GameState {
public:
  explicit GameState(int side_length);

  // Returns a copy of the current board.
  Board board() const { return board_; }
  Cell to_move() const { return to_move_; }
  int min_allowed() const { return 1; }
  int max_allowed() const { return max_allowed_; }
  bool is_terminal() const { return board_.is_full(); }

  // Winner once is_terminal is true; throws std::logic_error otherwise.
  Cell winner() const;

  // Applies a move (a set of empty cells for the player to move)
  // and returns the resulting new state.
  // Throws if the move's size falls outside [min_allowed, max_allowed],
  // any cell is invalid or already occupied, or the game is already over.
  GameState apply_move(const std::vector<int> &move) const;

  // Every legal move for the current player, all combinations of empty
  // cells with size in [min_allowed, max_allowed].
  std::vector<std::vector<int>> legal_moves() const;

private:
  GameState(Board board, Cell to_move, int max_allowed);

  Board board_;
  Cell to_move_;
  int max_allowed_;
};

} // namespace catchup
