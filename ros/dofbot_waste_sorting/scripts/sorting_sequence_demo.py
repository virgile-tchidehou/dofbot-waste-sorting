#!/usr/bin/env python3
"""Small direct-control demo for validating calibrated DOFBOT positions."""

from pathlib import Path
import sys
import time

import rospkg
import yaml
from Arm_Lib import Arm_Device


PACKAGE_ROOT = Path(
    rospkg.RosPack().get_path("dofbot_waste_sorting")
)
CONFIG = PACKAGE_ROOT / "config" / "positions.yaml"


def pose_angles(pose, default_gripper):
    return [
        int(pose["joint1"]),
        int(pose["joint2"]),
        int(pose["joint3"]),
        int(pose["joint4"]),
        int(pose["joint5"]),
        int(pose.get("gripper", default_gripper)),
    ]


def main():
    with CONFIG.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    arm = Arm_Device()
    time.sleep(1.0)

    open_gripper = int(config["movement"]["gripper_open"])
    names = [
        "home_position",
        "safe_position",
        "observation_position",
        "pick_position",
    ]

    if len(sys.argv) > 1:
        names = sys.argv[1:]

    for name in names:
        if name in config:
            pose = config[name]
        elif name in config["bins"]:
            pose = config["bins"][name]
        else:
            raise KeyError(f"Unknown pose: {name}")

        angles = pose_angles(pose, open_gripper)
        print(f"{name}: {angles}")
        arm.Arm_serial_servo_write6_array(angles, 1200)
        time.sleep(1.7)


if __name__ == "__main__":
    main()
