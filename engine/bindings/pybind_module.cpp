#include <pybind11/pybind11.h>

#include <string>

namespace {

std::string ping() { return "pong"; }

}  // namespace

PYBIND11_MODULE(catchup_engine, m) {
    m.doc() = "Catchup engine (C++ backend)";
    m.def("ping", &ping, "Health-check function; returns 'pong'.");
}
