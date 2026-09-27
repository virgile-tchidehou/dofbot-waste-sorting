#!/usr/bin/env python3
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class MovementConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = yaml.safe_load(
            (ROOT / "ros/dofbot_waste_sorting/config/positions.yaml").read_text(encoding="utf-8")
        )

    def test_required_poses_exist(self):
        for name in (
            "home_position",
            "safe_position",
            "observation_position",
            "pick_position",
        ):
            self.assertIn(name, self.config)

    def test_required_bins_exist(self):
        for name in ("dangereux", "menagers", "recyclables"):
            self.assertIn(name, self.config["bins"])

    def test_all_pose_values_are_within_limits(self):
        limits = self.config["limits"]
        pose_names = [
            "home_position",
            "safe_position",
            "observation_position",
            "pick_position",
        ]

        poses = [self.config[name] for name in pose_names]
        poses.extend(self.config["bins"].values())

        for pose in poses:
            for key in ("joint1", "joint2", "joint3", "joint4", "joint5", "gripper"):
                value = pose[key]
                lower, upper = limits[key]
                self.assertGreaterEqual(value, lower, f"{key} below limit")
                self.assertLessEqual(value, upper, f"{key} above limit")


if __name__ == "__main__":
    unittest.main()
