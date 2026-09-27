#!/usr/bin/env python3
"""Static repository checks for dofbot-waste-sorting."""

from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parent

REQUIRED_PATHS = [
    "README.md",
    "config/positions.yaml",
    "config/yolov5_params.yaml",
    "ros/dofbot_waste_sorting/CMakeLists.txt",
    "ros/dofbot_waste_sorting/package.xml",
    "ros/dofbot_waste_sorting/launch/sorting.launch",
    "ros/dofbot_waste_sorting/scripts/camera_node.py",
    "ros/dofbot_waste_sorting/scripts/vision_node.py",
    "ros/dofbot_waste_sorting/scripts/sorting_controller_node.py",
    "ros/dofbot_waste_sorting/srv/Classify.srv",
    "tools/calibrate_positions.py",
    "tools/calibration_server.py",
    "web/calibration_interface.html",
    "ml/data/dataset.yaml",
]

LEGACY_TERMS = [
    "TRC2025",
    "TRC 2025",
    "UCAO-TECH",
    "Ucaotech",
    "ucaotech_dofbot_trc2025",
    "trc2025_train_models",
    "projet_robotique2k25UCAO",
]

TEXT_SUFFIXES = {
    ".md", ".py", ".yaml", ".yml", ".xml", ".txt", ".js", ".html",
    ".launch", ".srv", ".json", ".ini", ".sh",
}


def check_required_paths():
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    return missing


def check_class_mapping():
    positions = yaml.safe_load((ROOT / "config" / "positions.yaml").read_text(encoding="utf-8"))
    vision = yaml.safe_load((ROOT / "config" / "yolov5_params.yaml").read_text(encoding="utf-8"))

    mapping = positions["class_to_bin"]
    names = vision["classes"]["names"]

    errors = []
    for class_id, class_name in enumerate(names):
        mapped = mapping.get(class_id, mapping.get(str(class_id)))
        if mapped != class_name:
            errors.append(
                f"class {class_id}: vision='{class_name}' but class_to_bin='{mapped}'"
            )
    return errors


def check_legacy_terms():
    hits = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if ".git" in path.parts:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for term in LEGACY_TERMS:
            if term in text:
                hits.append(f"{path.relative_to(ROOT)} -> {term}")
    return hits


def main():
    failures = []

    missing = check_required_paths()
    if missing:
        failures.extend(f"missing: {path}" for path in missing)

    failures.extend(f"mapping: {item}" for item in check_class_mapping())
    failures.extend(f"legacy: {item}" for item in check_legacy_terms())

    if failures:
        print("Repository consistency check failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("Repository consistency check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
