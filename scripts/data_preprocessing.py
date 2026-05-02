import cv2
import shutil
from pathlib import Path
from config import *

def filter_images():
    src_images = sorted(SRC_IMAGES.glob("*"))
    dst_images = SCENE / "images"
    dst_images.mkdir(parents=True, exist_ok=True)

    kept = []

    for img_path in src_images:
        if img_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            continue

        img = cv2.imread(str(img_path))
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        blur = cv2.Laplacian(gray, cv2.CV_64F).var()
        mean_lum = gray.mean()

        if blur > BLUR_THRESH and DARK_THRESH < mean_lum < BRIGHT_THRESH:
            shutil.copy2(img_path, dst_images / img_path.name)
            kept.append(img_path.name)

    print(f"✅ Kept {len(kept)} images")
