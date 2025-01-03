#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>
#include <Manifold.hpp>

namespace py = pybind11;

// Binding code to expose Manifold.ProcessManifold
PYBIND11_MODULE(manifold, m)
{
    py::class_<Manifold>(m, "Manifold")
        .def(py::init<>())
        .def("ProcessManifold", &Manifold::ProcessManifold, "A function to take an array of verts and faces and produce a manifold mesh");
}