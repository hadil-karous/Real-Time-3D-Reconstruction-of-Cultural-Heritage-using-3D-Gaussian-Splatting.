import os
from config import *

def run_colmap():
    print("🚧 Running COLMAP (placeholder)")

    # Example command (adapt later)
    cmd = f"""
    colmap automatic_reconstructor \
        --workspace_path {SCENE} \
        --image_path {SCENE / "images"}
    """

    os.system(cmd)
