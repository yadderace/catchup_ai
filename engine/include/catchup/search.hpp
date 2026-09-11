#pragma once

#include <vector>

#include "catchup/board.hpp"

namespace catchup {

// Returns at most `candidate_cap` empty-cell slots from `board`, ranked by
// hex distance to the nearest occupied cell (closest first)
std::vector<int> ranked_candidate_cells(const Board &board, int candidate_cap);

} // namespace catchup
