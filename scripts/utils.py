from config import *

def setup_directories():
    for d in [
        SCENE / "images",
        SCENE / "sparse/0",
        UNDIST,
        OUTPUT_DIR
    ]:
        d.mkdir(parents=True, exist_ok=True)

    print("📁 Directories ready")
