find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(catchup_engine
    bindings/pybind_module.cpp
)
