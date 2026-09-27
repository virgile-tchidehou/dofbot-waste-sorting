#!/usr/bin/env python3
"""Smoke-test a custom YOLOv5 model on one image."""

import argparse
import os
from pathlib import Path

import torch


def main():
    root = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(description="Smoke-test the DOFBOT waste-sorting model")
    parser.add_argument("--weights", type=Path, default=Path(os.environ.get("DOFBOT_MODEL_PATH", root / "models" / "best.pt")))
    parser.add_argument("--image", type=Path, default=None)
    parser.add_argument("--yolov5-repo", default=os.environ.get("YOLOV5_REPO"))
    parser.add_argument("--confidence", type=float, default=0.25)
    args = parser.parse_args()

    weights = args.weights.expanduser().resolve()
    if not weights.exists():
        raise SystemExit(f"Model weights not found: {weights}")

    image = args.image
    if image is None:
        samples = sorted((root / "data" / "samples").glob("*"))
        samples = [p for p in samples if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}]
        if not samples:
            raise SystemExit("No sample image found in data/samples/")
        image = samples[0]

    image = image.expanduser().resolve()
    if not image.exists():
        raise SystemExit(f"Image not found: {image}")

    if args.yolov5_repo:
        model = torch.hub.load(
            str(Path(args.yolov5_repo).expanduser()),
            "custom",
            path=str(weights),
            source="local",
        )
    else:
        model = torch.hub.load(
            "ultralytics/yolov5",
            "custom",
            path=str(weights),
            force_reload=False,
        )

    model.conf = args.confidence
    results = model(str(image))
    print(results.pandas().xyxy[0].to_string(index=False))


if __name__ == "__main__":
    main()
