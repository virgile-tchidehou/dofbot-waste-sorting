#!/usr/bin/env python3
"""Evaluate a YOLOv5 model on the small repository sample set."""

import argparse
import os
from collections import Counter
from pathlib import Path

import torch


CLASS_NAMES = ["dangereux", "menagers", "recyclables"]
PREFIX_TO_ID = {name: index for index, name in enumerate(CLASS_NAMES)}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def expected_class(path: Path):
    name = path.name.lower()
    for prefix, class_id in PREFIX_TO_ID.items():
        if name.startswith(prefix + "_"):
            return class_id
    return None


def main():
    root = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(description="Evaluate model predictions on data/samples")
    parser.add_argument("--weights", type=Path, default=Path(os.environ.get("DOFBOT_MODEL_PATH", root / "models" / "best.pt")))
    parser.add_argument("--yolov5-repo", default=os.environ.get("YOLOV5_REPO"))
    parser.add_argument("--confidence", type=float, default=0.25)
    args = parser.parse_args()

    weights = args.weights.expanduser().resolve()
    if not weights.exists():
        raise SystemExit(f"Model weights not found: {weights}")

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

    samples = sorted(
        p for p in (root / "data" / "samples").iterdir()
        if p.suffix.lower() in IMAGE_SUFFIXES
    )

    total = 0
    correct = 0
    per_class = Counter()
    per_class_correct = Counter()

    for image in samples:
        truth = expected_class(image)
        if truth is None:
            continue

        detections = model(str(image)).pandas().xyxy[0]
        if detections.empty:
            predicted = -1
            confidence = 0.0
        else:
            row = detections.loc[detections["confidence"].idxmax()]
            predicted = int(row["class"])
            confidence = float(row["confidence"])

        total += 1
        per_class[truth] += 1
        if predicted == truth:
            correct += 1
            per_class_correct[truth] += 1

        print(
            f"{image.name}: expected={CLASS_NAMES[truth]} "
            f"predicted={CLASS_NAMES[predicted] if 0 <= predicted < len(CLASS_NAMES) else 'none'} "
            f"confidence={confidence:.3f}"
        )

    print("\nSample-set summary")
    print(f"evaluated: {total}")
    if total:
        print(f"accuracy:  {correct / total:.2%}")

    for class_id, name in enumerate(CLASS_NAMES):
        count = per_class[class_id]
        hits = per_class_correct[class_id]
        if count:
            print(f"{name}: {hits}/{count}")


if __name__ == "__main__":
    main()
