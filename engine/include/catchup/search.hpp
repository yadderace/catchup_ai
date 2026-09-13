#pragma once

#include <vector>

#include "catchup/board.hpp"
#include "catchup/game_state.hpp"

namespace catchup {

// Returns at most `candidate_cap` empty-cell slots from `board`, ranked by
// hex distance to the nearest occupied cell (closest first)
std::vector<int> ranked_candidate_cells(const Board &board, int candidate_cap);

// Scores a position from one color's point of view: positive favors
// `perspective`, negative favors the opponent.
double evaluate(const GameState &state, Cell perspective);

} // namespace catchup
