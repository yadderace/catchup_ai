#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <stdexcept>
#include <string>

#include "catchup/board.hpp"

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
        }, py::arg("slot"));
}
