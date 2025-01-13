# manifold

Python (PyVista/Numpy) interface for the ManifoldPlus C++ library for making watertight manifold surfaces from triangular meshes.

The library can be installed by cloning the repo and running `pip install .` 

An example minimal python environment can be created with the library installed by running `make env && conda activate && make install-packages`. 

With this example enviroment, the tests as provided with the original ManifoldPlus can be run using the python bindings via `make run-test`.

The library is designed to take `pv.PolyData` as input and return `pv.PolyData` as output:
```
  import pyvista as pv
  from manifold import process_manifold

  non_manifold_mesh: pv.PolyData = pv.read("path/to/mesh.stl")

  # non_manifold_mesh.is_manifold -> False

  manifold_mesh: pv.PolyData = process_manifold(non_manifold_mesh)

  # manifold_mesh.is_manifold -> True (on average)
```

Original C++ Source: 
https://github.com/hjwdzh/ManifoldPlus
```
@article{huang2020manifoldplus,
  title={ManifoldPlus: A Robust and Scalable Watertight Manifold Surface Generation Method for Triangle Soups},
  author={Huang, Jingwei and Zhou, Yichao and Guibas, Leonidas},
  journal={arXiv preprint arXiv:2005.11621},
  year={2020}
}
```