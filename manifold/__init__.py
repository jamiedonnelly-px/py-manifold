import numpy as np
import numpy.typing as npt
import pyvista as pv

from ._manifold_internal import _manifold

__all__ = ["process_manifold"]


def _faces_to_2d(faces: npt.NDArray[np.int32]) -> npt.NDArray[np.int32]:
    """Function to transform 1-dimensional face array to 2-dimensional face matrix.

    Args:
        faces (npt.NDArray[np.int32]): 1-dimensional numpy array of faces in canonical pyvista format.

    Returns:
        npt.NDArray[np.int32]: 2-dimensional numpy array of faces shaped [N x 3] for number of faces N.
    """
    _shape: tuple = faces.shape
    match len(_shape):
        case 1:
            # reshape to [N x 3] for N faces
            return faces.reshape(-1, 4)[:, 1:]
        case _:
            raise ValueError(
                f"Faces must be a 1-dimensional array not {len(_shape)}-dimensional."
            )


def _faces_to_1d(faces: npt.NDArray[np.int32]) -> npt.NDArray[np.int32]:
    _faces_with_tri = np.concatenate(
        [3 * np.ones(faces.shape[0]).reshape(-1, 1).astype(np.int32), faces], axis=1
    )
    return _faces_with_tri.flatten()


def process_manifold(
    mesh: pv.PolyData, depth: int = 8, verbose: bool = False
) -> pv.PolyData:
    """Function for making pv.PolyData mesh watertight and manifold.

    Args:
        mesh (pv.PolyData): Input mesh.
        depth (int, optional): Depth of the octree used to reconstruct the mesh. Defaults to 8.
        verbose (bool, optional): Whether to print logs about the re-meshing process to stdout. Defaults to false.

    Returns:
        pv.PolyData: Output watertight and manifold mesh.
    """
    # type checks
    if not isinstance(mesh, pv.PolyData):
        raise AssertionError(
            f"Input mesh needs to be type pyvista.PolyData not {type(mesh)}"
        )
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
    i_verts, i_faces = mesh.points, _faces_to_2d(mesh.faces)

    # run ManifoldPlus
    o_verts, o_faces = _manifold(i_verts, i_faces, depth=depth, verbose=verbose)

    return pv.PolyData(o_verts, _faces_to_1d(o_faces))
