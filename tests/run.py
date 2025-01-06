from pathlib import Path

import numpy as np 
import pyvista as pv

from manifold import process_manifold

if __name__=="__main__":
    print(f"Running python tests...")

    # find data dir
    workspace = Path(__file__).parents[0]
    data = workspace.parents[0] / "data"
    results_dir = workspace / "results"
    
    # create directory to save results
    if not results_dir.is_dir():
        results_dir.mkdir(parents=True, exist_ok=True)
    
    # example 1 
    bathtub = pv.read(data / "bathtub.obj")
    print(f"Loaded {data / 'bathtub.obj'}. Manifoldness: {bathtub.is_manifold}")
    print(f"Running `ManifoldPlus`...")
    verts, faces = bathtub.points, bathtub.faces
    new_verts, new_faces = process_manifold(verts, faces, depth=8)
    manifold_bathtub = pv.PolyData(verts=new_verts, faces=new_faces)
    print(f"Manifoldness: {manifold_bathtub.is_manifold}")
    manifold_bathtub.save(results_dir / "bathtub.obj")

    # example 2
    bed = pv.read(data / "bed.obj")
    print(f"Loaded {data / 'bed.obj'}. Manifoldness: {bed.is_manifold}")
    print(f"Running `ManifoldPlus`...")
    verts, faces = bed.points, bed.faces
    new_verts, new_faces = process_manifold(verts, faces, depth=8)
    manifold_bed = pv.PolyData(verts=new_verts, faces=new_faces)
    print(f"Manifoldness: {manifold_bed.is_manifold}")
    manifold_bed.save(results_dir / "bed.obj")