import numpy as np 
import numpy.typing as npt
import pyvista as pv

from ._manifold_internal import _manifold

__all__ = ['process_manifold']

def _transform_faces(faces: npt.NDArray[np.int32]) -> npt.NDArray[np.int32]: 
    """ Function to transform 1-dimensional face array to 2-dimensional face matrix. 

    Args:
        faces (npt.NDArray[np.int32]): 1-dimensional numpy array of faces in canonical pyvista format.

    Returns:
        npt.NDArray[np.int32]: 2-dimensional numpy array of faces shaped [N x 3] for number of faces N.
    """
    _shape: tuple = faces.shape
    match len(_shape):
        case 1:
            return faces.reshape(-1, 4)[:, 1]
        case _:
            raise ValueError(f"Faces must be a 1-dimensional array not {len(_shape)}-dimensional.")
    
def process_manifold(mesh: pv.PolyData, depth: int = 8) -> pv.PolyData:
    """ Function for making pv.PolyData mesh watertight and manifold.

    Args:
        mesh (pv.PolyData): Input mesh. 
        depth (int, optional): Depth of the octree used to reconstruct the mesh. Defaults to 8.

    Returns:
        pv.PolyData: Output watertight and manifold mesh.
    """
    # type checks
    if not isinstance(mesh, pv.PolyData):
        raise AssertionError(f"Input mesh needs to be type pyvista.PolyData not {type(mesh)}")
    if not isinstance(depth, int):
        raise AssertionError(f"Depth parameters needs to be type int not {type(depth)}")

    # check for triangle
    if not mesh.is_all_triangles:
        raise AssertionError("Input mesh did not pass triangle faces check.")

    # check for manifoldness
    if mesh.is_manifold:
        print("Input mesh is already manifold.")
        return mesh

    # transform faces and fetch verts
    i_verts, i_faces = mesh.points, _transform_faces(mesh.faces)

    # run ManifoldPlus
    o_verts, o_faces = _manifold(i_verts, i_faces, depth=depth)

    return pv.PolyData(o_verts, o_faces)