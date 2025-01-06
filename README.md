# ManifoldPlus Python

Python implementation of the ManifoldPlus C++ library for making watertight manifold surfaces from triangle meshes. 

The library can be installed by cloning the repo and running `pip install .` 

An example minimal python environment can be created with the library installed by running `make env && conda activate && make install-packages`. 

With this example enviroment the tests as provided with the original ManifoldPlus can be run using the python bindings via `make run-test`.

Source: 
https://github.com/hjwdzh/ManifoldPlus
```
@article{huang2020manifoldplus,
  title={ManifoldPlus: A Robust and Scalable Watertight Manifold Surface Generation Method for Triangle Soups},
  author={Huang, Jingwei and Zhou, Yichao and Guibas, Leonidas},
  journal={arXiv preprint arXiv:2005.11621},
  year={2020}
}
```