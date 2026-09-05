#include "catchup/board.hpp"

#include <algorithm>
#include <array>
#include <cstdlib>
#include <mutex>
#include <numeric>
#include <stdexcept>
#include <unordered_map>

namespace catchup {

namespace {

// The 6 axial neighbor offsets
constexpr std::array<std::pair<int, int>, 6> kNeighborOffsets = {{
    {1, 0},
    {-1, 0},
    {0, 1},
    {0, -1},
    {1, -1},
    {-1, 1},
}};

} // namespace

// Every slot starts out as its own singleton group.
DisjointSet::DisjointSet(int n) : parent_(n), size_(n, 1) {
  std::iota(parent_.begin(), parent_.end(), 0);
}

// Path-halving find: walk toward the root, flattening pointers as we go.
int DisjointSet::find(int x) const {
  while (parent_[x] != x) {
    parent_[x] = parent_[parent_[x]];
    x = parent_[x];
  }
  return x;
}

// Union by size: attach the smaller group's root under the bigger one's.
void DisjointSet::unite(int a, int b) {
  int root_a = find(a);
  int root_b = find(b);
  if (root_a == root_b) {
    return;
  }
  if (size_[root_a] < size_[root_b]) {
    std::swap(root_a, root_b);
  }
  parent_[root_b] = root_a;
  size_[root_a] += size_[root_b];
}

// Builds the shape for a side-length-n hexagon assigns every valid axial
// (q, r) a compact slot number, then precomputes each slot's neighbor list.
HexHexShape::HexHexShape(int side_length) : side_length_(side_length) {
  if (side_length_ < 1) {
    throw std::invalid_argument("side_length must be >= 1");
  }
  radius_ = side_length_ - 1;
  grid_size_ = 2 * radius_ + 1;
  num_cells_ = 3 * side_length_ * side_length_ - 3 * side_length_ + 1;

  axial_to_index_.assign(static_cast<size_t>(grid_size_) * grid_size_, -1);
  axial_of_.reserve(num_cells_);

  // Pass 1, scan every (q, r) in the bounding square,
  // assign slot numbers in the order they're found.
  for (int q = -radius_; q <= radius_; ++q) {
    for (int r = -radius_; r <= radius_; ++r) {
      int s = -q - r;
      if (std::abs(q) <= radius_ && std::abs(r) <= radius_ &&
          std::abs(s) <= radius_) {
        int slot = static_cast<int>(axial_of_.size());
        axial_to_index_[grid_index(q, r)] = slot;
        axial_of_.emplace_back(q, r);
      }
    }
  }

  // Pass 2: now that every valid cell has a slot, look up each of its 6
  // axial neighbors and keep only the ones that resolved to a real slot.
  neighbors_of_.resize(num_cells_);
  for (int slot = 0; slot < num_cells_; ++slot) {
    const auto [q, r] = axial_of_[slot];
    auto &neighbors = neighbors_of_[slot];
    for (const auto &[dq, dr] : kNeighborOffsets) {
      const int n = index_of(q + dq, r + dr);
      if (n >= 0) {
        neighbors.push_back(n);
      }
    }
  }
}

// Looks up the slot for an axial coordinate, or -1 if it's off the board.
int HexHexShape::index_of(int q, int r) const {
  if (q < -radius_ || q > radius_ || r < -radius_ || r > radius_) {
    return -1;
  }
  return axial_to_index_[grid_index(q, r)];
}

// Returns the shared shape for a side length
std::shared_ptr<const HexHexShape> get_hex_hex_shape(int side_length) {
  static std::mutex mutex;
  static std::unordered_map<int, std::shared_ptr<const HexHexShape>> cache;

  std::lock_guard<std::mutex> lock(mutex);
  auto [it, inserted] = cache.try_emplace(side_length, nullptr);
  if (inserted) {
    it->second = std::make_shared<const HexHexShape>(side_length);
  }
  return it->second;
}

// Starts a new, empty board of the given side length. Each color gets its
// own union-find, sized for the full board (unused slots -- the other
// color's stones and empty cells -- just stay untouched singletons).
Board::Board(int side_length)
    : shape_(get_hex_hex_shape(side_length)),
      cells_(shape_->num_cells(), Cell::Empty),
      white_groups_(shape_->num_cells()),
      black_groups_(shape_->num_cells()) {}

// Guards the public accessors below against an out-of-range slot number.
void Board::check_slot(int slot) const {
  if (slot < 0 || slot >= num_cells()) {
    throw std::out_of_range("cell slot out of range");
  }
}

// (q, r) axial coordinate of a slot, for rendering/labeling.
std::pair<int, int> Board::coords(int slot) const {
  check_slot(slot);
  return shape_->coords_of(slot);
}

// Neighbor slots of a cell (up to 6, fewer at the board's edge/corners).
const std::vector<int> &Board::neighbors(int slot) const {
  check_slot(slot);
  return shape_->neighbors_of(slot);
}

// Current occupant of a cell (empty/white/black).
Cell Board::color_at(int slot) const {
  check_slot(slot);
  return cells_[slot];
}

// Picks the union-find for a color; Empty has no group tracking.
DisjointSet &Board::groups_for(Cell color) {
  return color == Cell::White ? white_groups_ : black_groups_;
}

const DisjointSet &Board::groups_for(Cell color) const {
  return color == Cell::White ? white_groups_ : black_groups_;
}

// Occupies an empty cell and unites it with any same-color neighbors --
// each merge is what keeps that color's largest-group size correct
// without ever rescanning the whole board.
void Board::place_stone(int slot, Cell color) {
  check_slot(slot);
  if (color == Cell::Empty) {
    throw std::invalid_argument("color must be white or black");
  }
  if (cells_[slot] != Cell::Empty) {
    throw std::invalid_argument("cell is already occupied");
  }

  cells_[slot] = color;
  DisjointSet &groups = groups_for(color);
  for (int neighbor : neighbors(slot)) {
    if (cells_[neighbor] == color) {
      groups.unite(slot, neighbor);
    }
  }
}

// Scans every stone of the given color once, keeping only the first size
// seen per distinct root -- that's what turns "one entry per stone" into
// "one entry per group".
std::vector<int> Board::group_sizes(Cell color) const {
  const DisjointSet &groups = groups_for(color);
  std::vector<int> sizes;
  std::unordered_map<int, bool> seen_roots;
  for (int slot = 0; slot < num_cells(); ++slot) {
    if (cells_[slot] == color) {
      int root = groups.find(slot);
      if (seen_roots.emplace(root, true).second) {
        sizes.push_back(groups.size_of(root));
      }
    }
  }
  return sizes;
}

int Board::largest_group_size(Cell color) const {
  std::vector<int> sizes = group_sizes(color);
  if (sizes.empty()) {
    return 0;
  }
  return *std::max_element(sizes.begin(), sizes.end());
}

std::vector<int> Board::sorted_group_sizes(Cell color) const {
  std::vector<int> sizes = group_sizes(color);
  std::sort(sizes.begin(), sizes.end(), std::greater<int>());
  return sizes;
}

} // namespace catchup
