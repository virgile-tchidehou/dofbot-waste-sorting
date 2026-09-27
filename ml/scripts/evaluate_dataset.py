#!/usr/bin/env python3
"""Evaluate a YOLOv5 model on a labeled validation image directory."""

import argparse
import os
from collections import Counter
from pathlib import Path

import torch
import yaml


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def load_model(weights: Path, yolov5_repo: str | None, confidence: float):
    if yolov5_repo:
        model = torch.hub.load(
            str(Path(yolov5_repo).expanduser()),
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

    model.conf = confidence
    return model


def resolve_validation_dir(dataset_yaml: Path) -> Path:
    with dataset_yaml.open("r", encoding="utf-8") as stream:
        cfg = yaml.safe_load(stream)

    root = Path(cfg["path"]).expanduser()
    if not root.is_absolute():
        root = (dataset_yaml.parent / root).resolve()

    val = Path(cfg["val"])
    return val if val.is_absolute() else root / val


def label_file_for(image_path: Path) -> Path:
    parts = list(image_path.parts)
    if "images" in parts:
        index = len(parts) - 1 - parts[::-1].index("images")
        parts[index] = "labels"
        return Path(*parts).with_suffix(".txt")
    return image_path.with_suffix(".txt")


def ground_truth_classes(label_path: Path) -> set[int]:
    if not label_path.exists():
        return set()

    classes = set()
    for line in label_path.read_text(encoding="utf-8").splitlines():
        fields = line.strip().split()
        if fields:
            classes.add(int(float(fields[0])))
    return classes


def best_prediction(model, image_path: Path):
    results = model(str(image_path))
    detections = results.pandas().xyxy[0]
    if detections.empty:
        return -1, 0.0

    row = detections.loc[detections["confidence"].idxmax()]
    return int(row["class"]), float(row["confidence"])


def main():
    root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(description="Evaluate a custom YOLOv5 waste-sorting model")
    parser.add_argument("--weights", type=Path, default=Path(os.environ.get("DOFBOT_MODEL_PATH", root / "models" / "best.pt")))
    parser.add_argument("--dataset", type=Path, default=root / "ml" / "data" / "dataset.yaml")
    parser.add_argument("--yolov5-repo", default=os.environ.get("YOLOV5_REPO"))
    parser.add_argument("--confidence", type=float, default=0.25)
    parser.add_argument("--limit", type=int, default=0, help="0 means all validation images")
    args = parser.parse_args()

    weights = args.weights.expanduser().resolve()
    dataset = args.dataset.expanduser().resolve()

    if not weights.exists():
        raise SystemExit(f"Model weights not found: {weights}")
    if not dataset.exists():
        raise SystemExit(f"Dataset config not found: {dataset}")

    val_dir = resolve_validation_dir(dataset)
    if not val_dir.exists():
        raise SystemExit(
            f"Validation image directory not found: {val_dir}\n"
            "Update the 'path' field in ml/data/dataset.yaml."
        )

    images = sorted(p for p in val_dir.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES)
    if args.limit > 0:
        images = images[: args.limit]

    model = load_model(weights, args.yolov5_repo, args.confidence)

    evaluated = 0
    correct = 0
    skipped = 0
    per_class = Counter()
    per_class_correct = Counter()

    for image_path in images:
        truth = ground_truth_classes(label_file_for(image_path))
        if not truth:
            skipped += 1
            continue

        predicted, confidence = best_prediction(model, image_path)
        evaluated += 1

        for class_id in truth:
            per_class[class_id] += 1

        if predicted in truth:
            correct += 1
            per_class_correct[predicted] += 1

        print(
            f"{image_path.name}: predicted={predicted} "
            f"confidence={confidence:.3f} truth={sorted(truth)}"
        )

    print("\nEvaluation summary")
    print(f"images discovered: {len(images)}")
    print(f"images evaluated:  {evaluated}")
    print(f"images skipped:    {skipped}")

    if evaluated:
        print(f"top-class accuracy: {correct / evaluated:.2%}")

    for class_id in sorted(per_class):
        total = per_class[class_id]
        hits = per_class_correct[class_id]
        print(f"class {class_id}: {hits}/{total}")


if __name__ == "__main__":
    main()
