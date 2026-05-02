from pathlib import Path

# Paths
SRC_ROOT    = Path("/kaggle/input/datasets/hadilkarous/hidataset/ignatius")
SRC_SPARSE  = SRC_ROOT / "sparse" / "0"
SRC_IMAGES  = SRC_ROOT / "input"

WORK        = Path("./workspace")
SCENE       = WORK / "scene_clean"
UNDIST      = WORK / "scene_undistorted"
OUTPUT_DIR  = WORK / "output_3dgs"

# Image filtering
BLUR_THRESH   = 80
DARK_THRESH   = 20
BRIGHT_THRESH = 240
