#include "catchup/search.hpp"

#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <vector>

namespace catchup {

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

} // namespace catchup
