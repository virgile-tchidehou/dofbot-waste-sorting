#!/usr/bin/env python3
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class CameraConfigurationTests(unittest.TestCase):
    def test_camera_node_exists(self):
        self.assertTrue(
            (ROOT / "ros/dofbot_waste_sorting/scripts/camera_node.py").exists()
        )

    def test_camera_config_matches_runtime_topic(self):
        config = yaml.safe_load(
            (ROOT / "config/camera_params.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(
            config["ros"]["image_topic"],
            "/dofbot_camera/image_raw",
        )

    def test_resolution_is_positive(self):
        config = yaml.safe_load(
            (ROOT / "config/camera_params.yaml").read_text(encoding="utf-8")
        )
        self.assertGreater(config["camera"]["width"], 0)
        self.assertGreater(config["camera"]["height"], 0)
        self.assertGreater(config["camera"]["fps"], 0)


if __name__ == "__main__":
    unittest.main()
