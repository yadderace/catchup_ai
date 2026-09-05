#pragma once

#include <memory>
#include <utility>
#include <vector>

namespace catchup {

enum class Cell { Empty, White, Black };

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

private:
  void check_slot(int slot) const;

  std::shared_ptr<const HexHexShape> shape_;
  std::vector<Cell> cells_;
};

} // namespace catchup
