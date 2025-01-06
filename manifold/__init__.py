from typing import Any

import numpy as np 

from ._manifold_internal import Manifold

__all__ = ['process_manifold']

def _transform_faces(faces: np.ndarray[Any, np.dtype[np.int32]]): 
    """ Used to convert triangular faces from 1d array to 2d """
    return faces.reshape(-1, 4)[:, 1:]

def process_manifold(verts: np.ndarray[Any, np.dtype[np.float64]], faces: np.ndarray[Any, np.dtype[np.int32]], depth: int = 8) -> tuple[np.ndarray[Any, np.dtype[np.float64]], np.ndarray[Any, np.dtype[np.int32]]]:
    """ A function to take a numpy array of verts and faces and produce a manifold mesh """
    _Manfiold = Manifold()
    formatted_faces = _transform_faces(faces)
    return _Manfiold.ProcessManifold(verts, formatted_faces, depth)