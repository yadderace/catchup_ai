#include "catchup/game_state.hpp"

#include <algorithm>
#include <stdexcept>
#include <utility>

namespace catchup {

namespace {

// Appends every size-k combination of items[start:] to `out`.
void collect_combinations(const std::vector<int> &items, int k, size_t start,
                          std::vector<int> &current,
                          std::vector<std::vector<int>> &out) {
  if (static_cast<int>(current.size()) == k) {
    out.push_back(current);
    return;
  }
  for (size_t i = start; i < items.size(); ++i) {
    current.push_back(items[i]);
    collect_combinations(items, k, i + 1, current, out);
    current.pop_back();
  }
}

} // namespace

// A fresh game: empty board, White to move, opening move (exactly 1 stone).
GameState::GameState(int side_length)
    : board_(side_length), to_move_(Cell::White), max_allowed_(1) {}

GameState::GameState(Board board, Cell to_move, int max_allowed)
    : board_(std::move(board)), to_move_(to_move), max_allowed_(max_allowed) {}

// Compare largest groups, then second-largest, and so on, treating a color
// with fewer groups as having 0 for the missing ones.
Cell GameState::winner() const {
  if (!is_terminal()) {
    throw std::logic_error("winner() is only valid once is_terminal is true");
  }
  const std::vector<int> white_sizes = board_.sorted_group_sizes(Cell::White);
  const std::vector<int> black_sizes = board_.sorted_group_sizes(Cell::Black);
  const size_t rounds = std::max(white_sizes.size(), black_sizes.size());
  for (size_t i = 0; i < rounds; ++i) {
    const int white_size = i < white_sizes.size() ? white_sizes[i] : 0;
    const int black_size = i < black_sizes.size() ? black_sizes[i] : 0;
    if (white_size != black_size) {
      return white_size > black_size ? Cell::White : Cell::Black;
    }
  }

  // This line should never be reached.
  throw std::logic_error(
      "no winner could be determined (unexpected true draw)");
}

GameState GameState::apply_move(const std::vector<int> &move) const {
  if (is_terminal()) {
    throw std::logic_error("cannot apply a move: the game is already over");
  }
  const int count = static_cast<int>(move.size());
  if (count < min_allowed() || count > max_allowed_) {
    throw std::invalid_argument(
        "move size is outside [min_allowed, max_allowed]");
  }

  // The opening move never triggers the catch-up bonus
  const bool was_opening = board_.is_empty();
  const int previous_largest =
      was_opening ? 0
                  : std::max(board_.largest_group_size(Cell::White),
                             board_.largest_group_size(Cell::Black));

  Board new_board = board_;
  for (int slot : move) {
    new_board.place_stone(slot, to_move_);
  }

  const Cell next_to_move =
      (to_move_ == Cell::White) ? Cell::Black : Cell::White;

  int next_max_allowed;
  if (was_opening) {
    next_max_allowed = 2;
  } else {
    const int new_largest = std::max(new_board.largest_group_size(Cell::White),
                                     new_board.largest_group_size(Cell::Black));
    next_max_allowed = (new_largest > previous_largest) ? 3 : 2;
  }

  return GameState(std::move(new_board), next_to_move, next_max_allowed);
}

std::vector<std::vector<int>> GameState::legal_moves() const {
  std::vector<int> empty_cells;
  for (int slot = 0; slot < board_.num_cells(); ++slot) {
    if (board_.color_at(slot) == Cell::Empty) {
      empty_cells.push_back(slot);
    }
  }

  std::vector<std::vector<int>> moves;
  std::vector<int> current;
  for (int k = min_allowed(); k <= max_allowed_; ++k) {
    if (k > static_cast<int>(empty_cells.size())) {
      break; // not enough empty cells left to reach this size
    }
    collect_combinations(empty_cells, k, 0, current, moves);
  }
  return moves;
}

} // namespace catchup
