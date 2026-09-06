find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(catchup_engine
    bindings/pybind_module.cpp
    src/board.cpp
    src/game_state.cpp
)

target_include_directories(catchup_engine PRIVATE include)
