from pathlib import Path

import pyvista as pv

from manifold import process_manifold

DEPTH = 8

# find data dir
WORKSPACE = Path(__file__).parents[1]
DATA = WORKSPACE / "data"


def test_manifold():
    # run on bathtub
    bathtub = pv.read(DATA / "bathtub.obj")
    manifold_bathtub = process_manifold(bathtub, depth=DEPTH)

    # run on bed
    bed = pv.read(DATA / "bed.obj")
    manifold_bed = process_manifold(bed, depth=DEPTH)

    # assertion checks
    assert manifold_bathtub.is_manifold
    assert manifold_bed.is_manifold
