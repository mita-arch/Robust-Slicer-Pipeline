from pathlib import Path

from slicer.mesh_io import load_mesh
from slicer.slicer_engine import slice_mesh
from debug_slicer import debug_single_slice

# ------------------------
# Input / output paths
# -------------------------
stl_path = "C:\\Users\\hp\\Downloads\\Main\\Week 1\\Models\\Carburetor.stl"
output_root = Path("output")
model_name = Path(stl_path).stem

# -------------------------
# Load mesh
# -------------------------
print("\n[1/3] Loading mesh...")
mesh = load_mesh(str(stl_path))

# -------------------------
# Slice mesh
# -------------------------
print("\n[2/3] Slicing mesh into layers...")
slices = slice_mesh(
    mesh=mesh,
    layer_height=0.2,
    first_layer_height=0.3,
)

if not slices:
    raise RuntimeError("No slices generated")

print(f"Generated {len(slices)} slices")

# =================================================
# DEBUG SINGLE SLICE ONLY
# =================================================
print("\n[3/3] Running debug on single slice...")

debug_single_slice(
    slices=slices,
    output_root=output_root,
    model_name=model_name,
    slice_id=None,   # middle slice by default
)

print("\n[DEBUG MODE COMPLETE]")
