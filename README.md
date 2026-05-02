# Ignatius — 3D Gaussian Splatting Pipeline

A research-grade pipeline for reconstructing a 3D scene from multi-view images using [3D Gaussian Splatting](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/). Built and validated on the **Ignatius statue dataset** from the Tanks and Temples benchmark.

---

## Overview

This project takes a set of calibrated multi-view images (with pre-computed COLMAP reconstruction) and produces a 3D Gaussian Splat model, with careful image quality control, localization filtering, and angular train/test splitting at every stage.

```
Raw images (263)
    │
    ▼  Stage 0B — blur & exposure filter
Cleaned images
    │
    ▼  Stage 1A/1B — COLMAP parse & localization filter
Well-localized images (≥500 valid 3D observations)
    │
    ▼  Stage 2 — angular coverage split
Train set + Test set
    │
    ▼  Stages 3–5 — 3DGS training & evaluation
point_cloud.ply + PSNR metrics
```

---

## Pipeline Stages

### Stage 0A — Environment setup
Validates GPU availability (`nvidia-smi`), checks that dataset paths exist, and creates the working directory structure:

```
workspace/
├── scene_clean/
│   ├── images/
│   └── sparse/0/
├── scene_undistorted/
└── output_3dgs/
```

### Stage 0B — Image quality filtering

Rejects blurry or poorly-exposed frames before COLMAP to prevent noisy feature matching and corrupt gradients during training.

| Metric | Threshold | Method |
|---|---|---|
| Sharpness | Laplacian variance > 80 | `cv2.Laplacian` |
| Underexposure | Mean luminance > 20 | `gray.mean()` |
| Overexposure | Mean luminance < 240 | `gray.mean()` |

If the rejection rate exceeds 20%, the blur threshold is automatically relaxed to 50.

**Output:** `blur_distribution.png`

### Stage 1A — Parse COLMAP binaries

Reads `images.bin` and `points3D.bin` directly from the dataset sparse reconstruction (no COLMAP re-run required). Extracts:
- Per-image quaternion pose + translation
- Per-image valid 3D observation count
- Per-point reprojection errors

**Output:** `colmap_analysis.png` (reprojection error histogram + per-image observation count)

> **Including COLMAP results in your README**
> See the [COLMAP results section](#including-colmap-results) below for suggestions on what to visualize.

### Stage 1B — Localization quality filter

Removes images with fewer than **500 valid 3D observations**, which indicates high pose uncertainty. Cross-references the quality-passed set from Stage 0B with the COLMAP-registered set.

### Stage 2 — Angular coverage-based train/test split

Camera centers are projected to the XZ plane and divided into `N_TEST = n_total // 8` equal angular sectors (~12.5% test). One frame per sector is selected as a test view, ensuring angular diversity rather than random clustering.

**Output:** `camera_split.png` (polar plot of camera positions), `train_list.txt`, `test_list.txt`

### Stages 3–5 — Scene prep, training, and evaluation

- **Stage 3:** Copies the filtered COLMAP sparse model to the working scene.
- **Stage 4:** Calls `colmap image_undistorter` and then runs `train.py` from the [gaussian-splatting](https://github.com/graphdeco-inria/gaussian-splatting) repo at 30 000 iterations.
- **Stage 5:** Runs `render.py` and `metrics.py` on the test set, then computes per-image PSNR and generates a GT vs. rendered comparison grid.

**Outputs:** `per_image_psnr.png`, `comparison_grid.png`, `point_cloud.ply`

---

## Results

| Metric | Value |
|---|---|
| Registered images | — |
| Median reprojection error | — px |
| Train images | — |
| Test images | — |
| Mean PSNR (test, 30k iter) | — dB |

> Fill in after running the full pipeline. A PSNR of **≥ 24 dB** is considered excellent for a stone statue scene at this resolution.

### PSNR quality guide

| PSNR range | Assessment |
|---|---|
| ≥ 24 dB | Excellent — strong reconstruction |
| 22–24 dB | Good — above 21.9 dB baseline |
| < 22 dB | Below baseline — see diagnostics |

---

## Project structure

```
project/
├── scripts/
│   ├── config.py              # All paths & thresholds
│   ├── data_preprocessing.py  # Stage 0B image quality filter
│   ├── colmap_utils.py        # COLMAP runner (placeholder)
│   ├── train.py               # 3DGS training wrapper
│   ├── pipeline.py            # Main entry point
│   └── utils.py               # Directory setup helpers
├── notebooks/
│   └── ignatius.ipynb         # Full research notebook
├── README.md
└── requirements.txt
```

---

## Setup

```bash
# Clone the repo
git clone https://github.com/<your-username>/ignatius-3dgs
cd ignatius-3dgs

# Install Python dependencies
pip install -r requirements.txt

# Clone gaussian-splatting into workspace/
git clone https://github.com/graphdeco-inria/gaussian-splatting workspace/gaussian-splatting
```

### Requirements

```
numpy
opencv-python
matplotlib
Pillow
```

COLMAP and the gaussian-splatting repo are expected to be available in the environment (pre-installed on Kaggle GPU instances).

---

## Running the pipeline

### From the notebook (recommended)

Open `notebooks/ignatius.ipynb` on Kaggle and run cells sequentially. Each stage prints a summary and saves diagnostic plots to `/kaggle/working/`.

### From scripts

```bash
python scripts/pipeline.py
```

Edit `scripts/config.py` to point `SRC_ROOT` at your dataset location.

---

## Including COLMAP results

The notebook produces `colmap_analysis.png` automatically. To make the most of your COLMAP output in the README and for presentations, here are the recommended additions:

### 1. Reprojection error histogram
Already generated as `colmap_analysis.png`. Add it to your README:

```markdown
![COLMAP analysis](assets/colmap_analysis.png)
```

To generate it standalone (outside Kaggle), run:
```python
python scripts/colmap_utils.py --plot
```

### 2. 3D point cloud visualization
The most impressive COLMAP result is the sparse 3D point cloud. You can export a screenshot with:

```bash
# Option A: COLMAP GUI — open workspace/scene_clean, go to Extras > Render
colmap gui

# Option B: use Open3D in Python
python - <<'EOF'
import open3d as o3d
pcd = o3d.io.read_point_cloud("workspace/scene_clean/sparse/0/points3D.ply")
o3d.visualization.draw_geometries([pcd])
EOF
```

To convert `points3D.bin` → `.ply` first:
```bash
colmap model_converter \
  --input_path workspace/scene_clean/sparse/0 \
  --output_path workspace/scene_clean/sparse/0 \
  --output_type PLY
```

Then save a screenshot and add it to `assets/point_cloud.png`.

### 3. Camera trajectory visualization
The Stage 2 polar plot (`camera_split.png`) already shows the camera orbit. For a 3D version, you can use the parsed poses directly:

```python
# In the notebook, after Stage 1A — add this cell:
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

centers = [camera_center(d['qvec'], d['tvec']) for d in colmap_images.values()]
xs, ys, zs = zip(*centers)

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(xs, ys, zs, s=8, c='steelblue', alpha=0.7)
ax.set_title('Camera positions — 3D view')
plt.savefig('/kaggle/working/cameras_3d.png', dpi=120)
```

### Suggested assets folder

```
assets/
├── blur_distribution.png     # Stage 0B output
├── colmap_analysis.png       # Stage 1A output
├── camera_split.png          # Stage 2 output
├── point_cloud.png           # COLMAP 3D point cloud screenshot
├── cameras_3d.png            # 3D camera trajectory (optional)
├── per_image_psnr.png        # Stage 5C output
└── comparison_grid.png       # Stage 5D GT vs rendered
```

---

## Diagnostics

### Overfitting check (Stage 6B)

| Signal | Threshold | Fix |
|---|---|---|
| PLY file too large | > 600 MB | `--densify_grad_threshold 0.00030` |
| PLY file too small | < 50 MB | `--densify_grad_threshold 0.00015` |
| Train–test PSNR gap | > 3 dB | Increase `--opacity_reset_interval` to 2000 |

### Improving PSNR

If PSNR is 21–23 dB, try:
1. Re-run COLMAP with `--SiftExtraction.max_num_features 16384`
2. Switch to exhaustive matching for 263 images
3. Capture additional views from 30° above/below the equatorial orbit

If PSNR is 23–25 dB, try:
1. `--densify_grad_threshold 0.00015` for finer detail
2. Extend training to 40k iterations

---

## Dataset

The **Ignatius** scene is from the [Tanks and Temples](https://www.tanksandtemples.org/) benchmark. The Kaggle-hosted version used here is at:

```
/kaggle/input/datasets/hadilkarous/hidataset/ignatius
```

---

## References

- Kerbl et al., *3D Gaussian Splatting for Real-Time Radiance Field Rendering*, SIGGRAPH 2023 — [paper](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/)
- Knapitsch et al., *Tanks and Temples: Benchmarking Large-Scale Scene Reconstruction*, SIGGRAPH 2017
- [COLMAP](https://colmap.github.io/) — Structure-from-Motion and Multi-View Stereo

---

## License

MIT
