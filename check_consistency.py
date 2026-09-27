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


def check_required_paths():
    return [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]


def check_class_mapping():
    positions = yaml.safe_load(
        (ROOT / "config" / "positions.yaml").read_text(encoding="utf-8")
    )
    vision = yaml.safe_load(
        (ROOT / "config" / "yolov5_params.yaml").read_text(encoding="utf-8")
    )

    errors = []
    mapping = positions["class_to_bin"]
    names = vision["classes"]["names"]

    for class_id, class_name in enumerate(names):
        mapped = mapping.get(class_id, mapping.get(str(class_id)))
        if mapped != class_name:
            errors.append(
                f"class {class_id}: vision='{class_name}' but class_to_bin='{mapped}'"
            )

    return errors


def check_ros_package_name():
    errors = []
    package_xml = (
        ROOT / "ros/dofbot_waste_sorting/package.xml"
    ).read_text(encoding="utf-8")
    cmake = (
        ROOT / "ros/dofbot_waste_sorting/CMakeLists.txt"
    ).read_text(encoding="utf-8")
    launch = (
        ROOT / "ros/dofbot_waste_sorting/launch/sorting.launch"
    ).read_text(encoding="utf-8")

    expected = "dofbot_waste_sorting"
    if f"<name>{expected}</name>" not in package_xml:
        errors.append("package.xml package name mismatch")
    if f"project({expected})" not in cmake:
        errors.append("CMake project name mismatch")
    if f'pkg="{expected}"' not in launch:
        errors.append("launch package name mismatch")

    return errors


def main():
    failures = []

    failures.extend(f"missing: {path}" for path in check_required_paths())
    failures.extend(f"mapping: {item}" for item in check_class_mapping())
    failures.extend(f"ros: {item}" for item in check_ros_package_name())

    if failures:
        print("Repository consistency check failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("Repository consistency check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
