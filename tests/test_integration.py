#!/usr/bin/env python3
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class ProjectIntegrationTests(unittest.TestCase):
    def test_ros_package_structure(self):
        required = [
            "ros/dofbot_waste_sorting/package.xml",
            "ros/dofbot_waste_sorting/CMakeLists.txt",
            "ros/dofbot_waste_sorting/launch/sorting.launch",
            "ros/dofbot_waste_sorting/scripts/camera_node.py",
            "ros/dofbot_waste_sorting/scripts/vision_node.py",
            "ros/dofbot_waste_sorting/scripts/sorting_controller_node.py",
            "ros/dofbot_waste_sorting/srv/Classify.srv",
        ]
        for path in required:
            self.assertTrue((ROOT / path).exists(), path)

    def test_class_mapping_matches_vision_config(self):
        positions = yaml.safe_load(
            (ROOT / "ros/dofbot_waste_sorting/config/positions.yaml").read_text(encoding="utf-8")
        )
        vision = yaml.safe_load(
            (ROOT / "ros/dofbot_waste_sorting/config/vision.yaml").read_text(encoding="utf-8")
        )

        names = vision["classes"]["names"]
        mapping = positions["class_to_bin"]

        for class_id, class_name in enumerate(names):
            mapped = mapping.get(class_id, mapping.get(str(class_id)))
            self.assertEqual(mapped, class_name)

    def test_classification_service_schema(self):
        service = (
            ROOT / "ros/dofbot_waste_sorting/srv/Classify.srv"
        ).read_text(encoding="utf-8")

        self.assertIn("sensor_msgs/Image image", service)
        self.assertIn("int32 class_id", service)
        self.assertIn("float32 confidence", service)

    def test_launch_references_current_package(self):
        launch = (
            ROOT / "ros/dofbot_waste_sorting/launch/sorting.launch"
        ).read_text(encoding="utf-8")

        self.assertIn('pkg="dofbot_waste_sorting"', launch)
        self.assertIn('type="camera_node.py"', launch)
        self.assertIn('type="vision_node.py"', launch)
        self.assertIn('type="sorting_controller_node.py"', launch)


if __name__ == "__main__":
    unittest.main()
