from pathlib import Path

import pyvista as pv

from manifold import process_manifold

DEPTH = 8

if __name__=="__main__":
    print(f"Running python tests with depth: {DEPTH}")

    # find data dir
    workspace = Path(__file__).parents[1]
    data = workspace / "data"
    results_dir = workspace / "results"
    
    # create directory to save results
    if not results_dir.is_dir():
        results_dir.mkdir(parents=True, exist_ok=True)
    
    # example 1 
    bathtub = pv.read(data / "bathtub.obj")
    print(f"Loaded {data / 'bathtub.obj'}. Manifoldness: {bathtub.is_manifold}")
    manifold_bathtub = process_manifold(bathtub, depth=DEPTH)
    print(f"Manifoldness: {manifold_bathtub.is_manifold}.")
    save_path = results_dir / "bathtub.stl"
    print(f"Saving results to {save_path}")
    manifold_bathtub.save(save_path)
    print(f"Resulting mesh has {manifold_bathtub.points.shape[0]} verts and \
            {manifold_bathtub.faces.reshape(-1,4).shape[0]}")
    
    # example 2
    bed = pv.read(data / "bed.obj")
    print(f"Loaded {data / 'bed.obj'}. Manifoldness: {bed.is_manifold}")
    manifold_bed = process_manifold(bed, depth=DEPTH)
    print(f"Manifoldness: {manifold_bed.is_manifold}.")
    save_path = results_dir / "bed.stl"
    print(f"Saving results to {save_path}")
    manifold_bed.save(save_path)
    print(f"Resulting mesh has {manifold_bed.points.shape[0]} verts and \
            {manifold_bed.faces.reshape(-1,4).shape[0]}")