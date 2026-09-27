#!/usr/bin/env python3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VISION_NODE = ROOT / "ros/dofbot_waste_sorting/scripts/vision_node.py"


class VisionNodeStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = VISION_NODE.read_text(encoding="utf-8")

    def test_single_vision_node_implementation(self):
        self.assertEqual(self.source.count("class VisionNode:"), 1)

    def test_current_ros_service_package(self):
        self.assertIn(
            "from dofbot_waste_sorting.srv import Classify, ClassifyResponse",
            self.source,
        )

    def test_no_silent_mock_classifier(self):
        self.assertNotIn("mock_classification", self.source)

    def test_model_path_is_configurable(self):
        self.assertIn("DOFBOT_MODEL_PATH", self.source)
        self.assertIn("~weights_path", self.source)


if __name__ == "__main__":
    unittest.main()
