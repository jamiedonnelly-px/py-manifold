#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>
#include <Manifold.hpp>

namespace py = pybind11;

// Binding code to expose Manifold.ProcessManifold
PYBIND11_MODULE(_manifold_internal, m) {
    m.def("_manifold", [](const MatrixD& verts, const MatrixI& faces, int depth = 8, int verbose = 0) {
        return Manifold().ProcessManifold(verts, faces, depth, verbose);
    },
    py::arg("vertices"),
    py::arg("faces"),
    py::arg("depth") = 8,
    py::arg("verbose") = 0
    );
}