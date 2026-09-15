#pragma once

#include <vector>

#include "catchup/board.hpp"
#include "catchup/game_state.hpp"

namespace catchup {

// The move a top-level search picked, its minimax score (from the
// mover's own point of view), and how many search nodes were visited
// while finding it.
struct SearchResult {
  std::vector<int> move;
  double score;
  long long nodes_visited;
};

// Returns at most `candidate_cap` empty-cell slots from `board`, ranked by
// hex distance to the nearest occupied cell (closest first)
std::vector<int> ranked_candidate_cells(const Board &board, int candidate_cap);

// Scores a position from one color's point of view: positive favors
// `perspective`, negative favors the opponent.
double evaluate(const GameState &state, Cell perspective);

// Looks `depth` plies ahead from `state`, assuming both sides always play
// their best available move (drawn from the candidate-pruned pool), and
// returns state's score from maximizing_player's fixed point of view.
double minimax(const GameState &state, int depth, Cell maximizing_player,
               int candidate_cap, long long &nodes_visited);

// Tries every top-level candidate move for whoever state.to_move() is
// (that becomes maximizing_player for the whole search), scores each
// resulting position with minimax, and returns the best one found.
SearchResult find_best_move(const GameState &state, int depth,
                            int candidate_cap);

} // namespace catchup
