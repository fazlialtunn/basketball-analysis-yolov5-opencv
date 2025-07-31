# 🏀 Basketball Analysis with YOLO and OpenCV

Analyze basketball footage with automated detection of players, ball, team assignment, and more. This repository integrates object tracking, zero-shot classification, and custom keypoint detection for a fully annotated basketball game experience.

Leveraging the convenience of Roboflow for dataset management and Ultralytics' YOLO models for both training and inference, this project provides a robust framework for basketball video analysis.

Training notebooks are included to help you customize and fine-tune models to suit your specific needs, ensuring a seamless and efficient workflow.

## ✨ Features

- Player and ball detection/tracking using pretrained models.
- Court keypoint detection for visualizing important zones.
- Team assignment with jersey color classification.
- Ball possession detection, pass detection, and interception detection.
- Easy stubbing to skip repeated computation for fast iteration.
- Various “drawers” to overlay detected elements onto frames.

---

📥 How to Clone This Project with Model Files

This project uses Git LFS (Large File Storage) to store large model files.

If you’d like to download the full project including trained models, please follow the steps below:

✅ Step-by-step:

# 1. Clone the repository
git clone https://github.com/fazlialtunn/basketball-analysis-yolov5-opencv.git

# 2. Go into the project directory
cd basketball-analysis-yolov5-opencv

# 3. Install Git LFS (only once)
git lfs install

# 4. Download the large model files
git lfs pull

⚠️ If you skip Step 4, model files under the models/ directory will not be available for use.
