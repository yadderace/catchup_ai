#pragma once

#include <memory>
#include <utility>
#include <vector>

namespace catchup {

enum class Cell { Empty, White, Black };

// Disjoint-set (union-find) over a fixed universe of n slots.
// Every slot starts as its own singleton group.
// unite() merges two groups.
class DisjointSet {
public:
  explicit DisjointSet(int n);

  // Root of x group, with path compression along the way.
  int find(int x) const;

  // Merges the groups containing a and b (no-op if already the same group).
  void unite(int a, int b);

  // Size of the group containing x.
  int size_of(int x) const { return size_[find(x)]; }

private:
  mutable std::vector<int> parent_;
  std::vector<int> size_;
};

// Precomputed shape of a hex-hex board of a given side length
class HexHexShape {
public:
  explicit HexHexShape(int side_length);

  int side_length() const { return side_length_; }
  int radius() const { return radius_; }
  int num_cells() const { return num_cells_; }

  // Slot for axial (q, r), or -1 if that cell is not on the board.
  int index_of(int q, int r) const;

  std::pair<int, int> coords_of(int slot) const { return axial_of_[slot]; }
  const std::vector<int> &neighbors_of(int slot) const {
    return neighbors_of_[slot];
  }

private:
  int grid_index(int q, int r) const {
    return (q + radius_) * grid_size_ + (r + radius_);
  }

  int side_length_;
  int radius_;
  int num_cells_;
  int grid_size_;
  std::vector<int> axial_to_index_;
  std::vector<std::pair<int, int>> axial_of_;
  std::vector<std::vector<int>> neighbors_of_;
};

// Returns the shared HexHexShape for a given side length
std::shared_ptr<const HexHexShape> get_hex_hex_shape(int side_length);

// Per-position board state: which color occupies each cell.
class Board {
public:
  explicit Board(int side_length);

  int side_length() const { return shape_->side_length(); }
  int num_cells() const { return shape_->num_cells(); }

  std::pair<int, int> coords(int slot) const;
  const std::vector<int> &neighbors(int slot) const;
  Cell color_at(int slot) const;

  // Places a stone of the given color on an empty cell, merging it with
  // any same-color neighbors into their group(s). Throws if the slot is
  // out of range, already occupied, or color is Cell::Empty.
  void place_stone(int slot, Cell color);

  // Size of that color's largest group on the board (0 if it has none).
  int largest_group_size(Cell color) const;

  // Sizes of every one of that color's groups, descending
  std::vector<int> sorted_group_sizes(Cell color) const;

  // True if no stone has been placed yet.
  bool is_empty() const;

  // True if every cell is occupied.
  bool is_full() const;

private:
  void check_slot(int slot) const;
  DisjointSet &groups_for(Cell color);
  const DisjointSet &groups_for(Cell color) const;
  std::vector<int> group_sizes(Cell color) const;

  std::shared_ptr<const HexHexShape> shape_;
  std::vector<Cell> cells_;
  DisjointSet white_groups_;
  DisjointSet black_groups_;
};

} // namespace catchup
