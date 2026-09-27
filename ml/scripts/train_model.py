#!/usr/bin/env python3
"""Config-driven YOLOv5 training wrapper."""

import argparse
import os
from pathlib import Path
import subprocess
import sys

import yaml


def resolve_from_config(config_file: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (config_file.parent / path).resolve()


def main():
    root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(description="Train the DOFBOT waste-sorting YOLOv5 model")
    parser.add_argument("--config", type=Path, default=root / "ml" / "config" / "training_config.yaml")
    parser.add_argument("--yolov5-repo", default=os.environ.get("YOLOV5_REPO"))
    parser.add_argument("--weights", default=None, help="Override starting weights, e.g. yolov5m.pt")
    parser.add_argument("--resume", type=Path, default=None, help="Resume from a YOLOv5 last.pt checkpoint")
    args = parser.parse_args()

    config_file = args.config.expanduser().resolve()
    if not config_file.exists():
        raise SystemExit(f"Training config not found: {config_file}")
    if not args.yolov5_repo:
        raise SystemExit("Set YOLOV5_REPO or pass --yolov5-repo /path/to/yolov5")

    yolov5_repo = Path(args.yolov5_repo).expanduser().resolve()
    train_py = yolov5_repo / "train.py"
    if not train_py.exists():
        raise SystemExit(f"YOLOv5 train.py not found: {train_py}")

    with config_file.open("r", encoding="utf-8") as stream:
        cfg = yaml.safe_load(stream)["training"]

    if args.resume:
        checkpoint = args.resume.expanduser().resolve()
        command = [sys.executable, str(train_py), "--resume", str(checkpoint)]
    else:
        dataset = resolve_from_config(config_file, cfg["data"])
        project = resolve_from_config(config_file, cfg["project"])
        weights = args.weights or f"{cfg['model']}.pt"

        command = [
            sys.executable,
            str(train_py),
            "--data", str(dataset),
            "--weights", str(weights),
            "--epochs", str(cfg["epochs"]),
            "--batch-size", str(cfg["batch_size"]),
            "--img", str(cfg["img_size"]),
            "--patience", str(cfg["patience"]),
            "--project", str(project),
            "--name", str(cfg["name"]),
            "--hyp", str(root / "ml" / "config" / "hyp.yaml"),
        ]

    print("Running:", " ".join(command))
    subprocess.run(command, cwd=yolov5_repo, check=True)


if __name__ == "__main__":
    main()
