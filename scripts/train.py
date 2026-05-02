import os
from config import *

def train_3dgs():
    print("🚀 Starting 3D Gaussian Splatting training")

    cmd = f"""
    python train.py \
        -s {UNDIST} \
        -m {OUTPUT_DIR}
    """

    os.system(cmd)
