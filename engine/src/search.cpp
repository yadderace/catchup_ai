#include "catchup/search.hpp"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <numeric>
#include <stdexcept>
#include <vector>

namespace catchup {

constexpr double kInfinity = 1e9;

std::vector<int> ranked_candidate_cells(const Board &board, int candidate_cap) {

  if (candidate_cap <= 0) {
    throw std::invalid_argument("candidate_cap must be > 0");
  }

  // Identify empty slots
  std::vector<int> empty_cells;
  for (int i = 0; i < board.num_cells(); i++) {
    if (board.color_at(i) == Cell::Empty) {
      empty_cells.push_back(i);
    }
  }

  // If the board is empty, return the first `candidate_cap` empty cells
  if (board.is_empty()) {
    if (static_cast<int>(empty_cells.size()) > candidate_cap) {
      empty_cells.resize(candidate_cap);
    }
    return empty_cells;
  }

  // Identify occupied slots
  std::vector<int> occupied_cells;
  for (int i = 0; i < board.num_cells(); i++) {
    if (board.color_at(i) != Cell::Empty) {
      occupied_cells.push_back(i);
    }
  }

  // Get score for each empty cell by applying hex distance to nearest stone
  // distance = (|dq| + |dr| + |dq + dr|) / 2.
  std::vector<std::pair<int, int>> candidates_with_scores;
  for (int empty_cell : empty_cells) {
    const std::pair<int, int> empty_coords = board.coords(empty_cell);
    int min_dist = 1000;
    for (int occupied_cell : occupied_cells) {
      std::pair<int, int> occupied_coords = board.coords(occupied_cell);
      int dq = empty_coords.first - occupied_coords.first;
      int dr = empty_coords.second - occupied_coords.second;
      int dist = (std::abs(dq) + std::abs(dr) + std::abs(dq + dr)) / 2;
      min_dist = std::min(min_dist, dist);
    }
    candidates_with_scores.push_back({empty_cell, min_dist});
  }

  // Get the top `candidate_cap` candidates
  const int cap =
      std::min(static_cast<int>(candidates_with_scores.size()), candidate_cap);
  std::partial_sort(
      candidates_with_scores.begin(), candidates_with_scores.begin() + cap,
      candidates_with_scores.end(),
      [](const auto &a, const auto &b) { return a.second < b.second; });

  // Extract the top candidate cells
  std::vector<int> candidates;
  for (int i = 0; i < cap; i++) {
    candidates.push_back(candidates_with_scores[i].first);
  }

  return candidates;
}

double evaluate(const GameState &state, Cell perspective) {

  // If the game is over, return the winner
  if (state.is_terminal()) {
    Cell winner_player = state.winner();
    if (winner_player == perspective) {
      return 1000.0;
    } else {
      return -1000.0;
    }
  }

  // Heuristic evaluation for non-terminal states
  Cell opponent = (perspective == Cell::White) ? Cell::Black : Cell::White;
  const Board &board = state.board();
  std::vector<int> perspective_groups = board.sorted_group_sizes(perspective);
  std::vector<int> opponent_groups = board.sorted_group_sizes(opponent);

  Cell player_more_groups =
      (perspective_groups.size() >= opponent_groups.size()) ? perspective
                                                            : opponent;
  int diff_groups = std::abs(static_cast<int>(perspective_groups.size()) -
                             static_cast<int>(opponent_groups.size()));

  // Summing the sizes of the stones of each player
  int perspective_stones =
      std::accumulate(perspective_groups.begin(), perspective_groups.end(), 0);
  int opponent_stones =
      std::accumulate(opponent_groups.begin(), opponent_groups.end(), 0);

  // Iterate through the groups to check the current player win condition
  std::vector<int> largest_groups_list = (player_more_groups == perspective)
                                             ? perspective_groups
                                             : opponent_groups;
  std::vector<int> smallest_groups_list = (player_more_groups == perspective)
                                              ? opponent_groups
                                              : perspective_groups;
  Cell winner_color = Cell::Empty;

  for (size_t i = 0; i < largest_groups_list.size(); i++) {
    int group_size = largest_groups_list[i];

    int smallest_group_size =
        (i < smallest_groups_list.size()) ? smallest_groups_list[i] : 0;
    if (smallest_group_size == 0) {
      winner_color = player_more_groups;
      break;
    }

    if (group_size > smallest_group_size) {
      winner_color = player_more_groups;
      break;
    }
    if (group_size < smallest_group_size) {
      winner_color =
          (player_more_groups == Cell::White) ? Cell::Black : Cell::White;
      break;
    }
  }

  // Calculate the score
  int coef_diff_groups = 2 * ((player_more_groups == perspective) ? 1 : -1);
  int coef_winner = 10 * ((winner_color == Cell::Empty)
                              ? 0
                              : ((winner_color == perspective) ? 1 : -1));
  double score = coef_diff_groups * diff_groups + coef_winner +
                 perspective_stones - opponent_stones;

  return score;
}

double minimax(const GameState &state, int depth, Cell maximizing_player,
               int candidate_cap, long long &nodes_visited) {

  nodes_visited++;

  // Checking if game state is terminal or depth is 0
  if (state.is_terminal() || depth == 0) {
    return evaluate(state, maximizing_player);
  }

  double best_score;

  // Maximizing player
  if (state.to_move() == maximizing_player) {
    best_score = -kInfinity;
    const std::vector<std::vector<int>> moves =
        state.legal_moves(candidate_cap);
    for (const auto &move : moves) {
      const GameState child = state.apply_move(move);
      const double score = minimax(child, depth - 1, maximizing_player,
                                   candidate_cap, nodes_visited);
      best_score = std::max(best_score, score);
    }
  }
  // Minimizing player
  else {
    best_score = kInfinity;
    const std::vector<std::vector<int>> moves =
        state.legal_moves(candidate_cap);
    for (const auto &move : moves) {
      const GameState child = state.apply_move(move);
      const double score = minimax(child, depth - 1, maximizing_player,
                                   candidate_cap, nodes_visited);
      best_score = std::min(best_score, score);
    }
  }

  return best_score;
}

SearchResult find_best_move(const GameState &state, int depth,
                            int candidate_cap) {
  if (state.is_terminal()) {
    throw std::logic_error("cannot find a move: the game is already over");
  }
  // Getting the player whose turn it is
  const Cell maximizing_player = state.to_move();
  // Getting all legal moves
  const std::vector<std::vector<int>> moves = state.legal_moves(candidate_cap);
  if (moves.empty()) {
    throw std::logic_error("no legal moves available");
  }

  long long nodes_visited = 0;
  std::vector<int> best_move;
  double best_score = 0.0;
  bool have_best = false;

  // Iterating through all legal moves and applying the minimax algorithm
  for (const std::vector<int> &move : moves) {
    const GameState child = state.apply_move(move);
    const double score = minimax(child, depth - 1, maximizing_player,
                                 candidate_cap, nodes_visited);
    if (!have_best || score > best_score) {
      best_score = score;
      best_move = move;
      have_best = true;
    }
  }

  return SearchResult{best_move, best_score, nodes_visited};
}

} // namespace catchup
