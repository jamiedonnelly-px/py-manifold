cmake_minimum_required(VERSION 3.15)
project(manifold)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON) 

list(APPEND CMAKE_PREFIX_PATH "${CMAKE_SOURCE_DIR}/3rd_party")
add_subdirectory(3rd_party/pybind11)
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/3rd_party/eigen
    ${CMAKE_CURRENT_SOURCE_DIR}/3rd_party/libigl/include
)

# library sources
set(CORE_SOURCES
    src/Intersection.cpp
    src/Manifold.cpp
    src/MeshProjector.cpp
    src/Octree.cpp
)

# internal headers
set(CORE_HEADERS
    src/GridIndex.hpp
    src/Intersection.hpp
    src/MeshProjector.hpp
    src/Octree.hpp
    src/types.hpp
    src/Manifold.hpp
)

add_library(manifold_core STATIC ${CORE_SOURCES} ${CORE_HEADERS})
set_property(TARGET manifold_core PROPERTY POSITION_INDEPENDENT_CODE ON)

pybind11_add_module(manifold src/main.cpp)
target_link_libraries(manifold PRIVATE manifold_core pybind11::module)

set(PYTHON_MODULE_OUTPUT_DIRECTORY manifold)
set_target_properties(manifold PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${PYTHON_MODULE_OUTPUT_DIRECTORY}
)




