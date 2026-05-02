from config import *
from data_preprocessing import filter_images
from utils import setup_directories
# from colmap_utils import run_colmap
# from train import train_3dgs

def main():
    print("=" * 50)
    print("STARTING PIPELINE")
    print("=" * 50)

    setup_directories()

    # Step 1: Filter images
    filter_images()

    # Step 2: COLMAP (enable later)
    # run_colmap()

    # Step 3: Train model (enable later)
    # train_3dgs()

    print("\n✅ Pipeline completed")

if __name__ == "__main__":
    main()
