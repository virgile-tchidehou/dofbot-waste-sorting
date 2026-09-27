#!/usr/bin/env python3
"""Quick environment check for a Jetson Nano DOFBOT setup."""

import importlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent


def check_module(name, required=True):
    try:
        module = importlib.import_module(name)
        version = getattr(module, "__version__", "available")
        print(f"[OK] {name}: {version}")
        return True
    except Exception as exc:
        label = "ERROR" if required else "OPTIONAL"
        print(f"[{label}] {name}: {exc}")
        return not required


def main():
    ok = True

    for module in ("yaml", "numpy", "cv2"):
        ok &= check_module(module, required=True)

    check_module("torch", required=False)
    check_module("rospy", required=False)
    check_module("cv_bridge", required=False)
    check_module("Arm_Lib", required=False)
    check_module("smbus", required=False)

    required_paths = [
        ROOT / "config" / "positions.yaml",
        ROOT / "ros" / "dofbot_waste_sorting" / "package.xml",
        ROOT / "ros" / "dofbot_waste_sorting" / "launch" / "sorting.launch",
    ]

    for path in required_paths:
        exists = path.exists()
        print(f"[{'OK' if exists else 'ERROR'}] {path.relative_to(ROOT)}")
        ok &= exists

    if ok:
        print("Base project setup looks consistent.")
        return 0

    print("Setup check found blocking issues.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
