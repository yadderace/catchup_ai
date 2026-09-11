#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <stdexcept>
#include <string>

#include "catchup/board.hpp"
#include "catchup/game_state.hpp"
#include "catchup/search.hpp"

namespace py = pybind11;

namespace {

std::string ping() { return "pong"; }

std::string cell_to_string(catchup::Cell cell) {
    switch (cell) {
        case catchup::Cell::Empty:
            return "empty";
        case catchup::Cell::White:
            return "white";
        case catchup::Cell::Black:
            return "black";
    }
    throw std::runtime_error("unreachable");
}

catchup::Cell string_to_stone_color(const std::string& color) {
    if (color == "white") return catchup::Cell::White;
    if (color == "black") return catchup::Cell::Black;
    throw std::invalid_argument("color must be 'white' or 'black'");
}

}  // namespace

PYBIND11_MODULE(catchup_engine, m) {
    m.doc() = "Catchup engine (C++ backend)";
    m.def("ping", &ping, "Health-check function; returns 'pong'.");

    py::class_<catchup::Board>(m, "Board")
        .def(py::init<int>(), py::arg("side_length"))
        .def_property_readonly("side_length", &catchup::Board::side_length)
        .def_property_readonly("num_cells", &catchup::Board::num_cells)
        .def("coords", &catchup::Board::coords, py::arg("slot"))
        .def("neighbors", &catchup::Board::neighbors, py::arg("slot"))
        .def("color_at", [](const catchup::Board& board, int slot) {
            return cell_to_string(board.color_at(slot));
        }, py::arg("slot"))
        .def("cells", [](const catchup::Board& board) {
            std::vector<std::string> colors;
            colors.reserve(board.num_cells());
            for (int slot = 0; slot < board.num_cells(); ++slot) {
                colors.push_back(cell_to_string(board.color_at(slot)));
            }
            return colors;
        })
        .def("place_stone", [](catchup::Board& board, int slot, const std::string& color) {
            board.place_stone(slot, string_to_stone_color(color));
        }, py::arg("slot"), py::arg("color"))
        .def("largest_group", [](const catchup::Board& board, const std::string& color) {
            return board.largest_group_size(string_to_stone_color(color));
        }, py::arg("color"))
        .def("sorted_group_sizes", [](const catchup::Board& board, const std::string& color) {
            return board.sorted_group_sizes(string_to_stone_color(color));
        }, py::arg("color"));

    py::class_<catchup::GameState>(m, "GameState")
        .def(py::init<int>(), py::arg("side_length"))
        .def_property_readonly("board", &catchup::GameState::board)
        .def_property_readonly("to_move", [](const catchup::GameState& state) {
            return cell_to_string(state.to_move());
        })
        .def_property_readonly("min_allowed", &catchup::GameState::min_allowed)
        .def_property_readonly("max_allowed", &catchup::GameState::max_allowed)
        .def_property_readonly("is_terminal", &catchup::GameState::is_terminal)
        .def_property_readonly("winner", [](const catchup::GameState& state) {
            return cell_to_string(state.winner());
        })
        .def("apply_move", &catchup::GameState::apply_move, py::arg("move"))
        .def("legal_moves", static_cast<std::vector<std::vector<int>> (catchup::GameState::*)() const>(
            &catchup::GameState::legal_moves))
        .def("legal_moves", static_cast<std::vector<std::vector<int>> (catchup::GameState::*)(int) const>(
            &catchup::GameState::legal_moves), py::arg("candidate_cap"));

    m.def("ranked_candidate_cells", &catchup::ranked_candidate_cells, py::arg("board"), py::arg("candidate_cap"));
}
