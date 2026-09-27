#!/usr/bin/env python3
"""Launch a straightforward YOLOv5 baseline training run."""

import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(description="Train a YOLOv5 baseline for DOFBOT waste sorting")
    parser.add_argument("--yolov5-repo", default=os.environ.get("YOLOV5_REPO"))
    parser.add_argument("--dataset", type=Path, default=root / "ml" / "data" / "dataset.yaml")
    parser.add_argument("--weights", default="yolov5m.pt")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--name", default="baseline")
    args = parser.parse_args()

    if not args.yolov5_repo:
        raise SystemExit("Set YOLOV5_REPO or pass --yolov5-repo /path/to/yolov5")

    yolov5_repo = Path(args.yolov5_repo).expanduser().resolve()
    train_py = yolov5_repo / "train.py"
    dataset = args.dataset.expanduser().resolve()

    if not train_py.exists():
        raise SystemExit(f"YOLOv5 train.py not found: {train_py}")
    if not dataset.exists():
        raise SystemExit(f"Dataset config not found: {dataset}")

    command = [
        sys.executable,
        str(train_py),
        "--data", str(dataset),
        "--weights", args.weights,
        "--epochs", str(args.epochs),
        "--batch-size", str(args.batch_size),
        "--img", str(args.img_size),
        "--project", str(root / "ml" / "runs"),
        "--name", args.name,
    ]

    print("Running:", " ".join(command))
    subprocess.run(command, cwd=yolov5_repo, check=True)


if __name__ == "__main__":
    main()
