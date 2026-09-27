#!/usr/bin/env python3
"""YOLOv5-backed ROS classification service for the DOFBOT sorting project."""

import os
from pathlib import Path

import rospy
import torch
from cv_bridge import CvBridge

from dofbot_waste_sorting.srv import Classify, ClassifyResponse


CLASS_NAMES = ["dangereux", "menagers", "recyclables"]


class VisionNode:
    def __init__(self):
        rospy.init_node("waste_vision")

        self.bridge = CvBridge()
        self.conf_threshold = float(rospy.get_param("~conf_threshold", 0.60))
        self.iou_threshold = float(rospy.get_param("~iou_threshold", 0.45))
        self.image_size = int(rospy.get_param("~img_size", 640))

        default_weights = Path.home() / "dofbot_models" / "best.pt"
        configured_weights = rospy.get_param(
            "~weights_path",
            os.environ.get("DOFBOT_MODEL_PATH", str(default_weights)),
        )
        self.weights_path = Path(configured_weights).expanduser()

        self.model = None
        self._load_model()

        self.service = rospy.Service(
            "vision/classify",
            Classify,
            self.handle_classification,
        )
        rospy.loginfo("Vision service ready on /vision/classify")

    def _load_model(self):
        if not self.weights_path.exists():
            rospy.logwarn(
                "Model weights not found at %s. Classification requests will return no detection.",
                self.weights_path,
            )
            return

        try:
            local_yolov5 = os.environ.get("YOLOV5_REPO")
            if local_yolov5 and Path(local_yolov5).expanduser().exists():
                self.model = torch.hub.load(
                    str(Path(local_yolov5).expanduser()),
                    "custom",
                    path=str(self.weights_path),
                    source="local",
                )
            else:
                self.model = torch.hub.load(
                    "ultralytics/yolov5",
                    "custom",
                    path=str(self.weights_path),
                    force_reload=False,
                )

            self.model.conf = self.conf_threshold
            self.model.iou = self.iou_threshold
            rospy.loginfo(
                "YOLOv5 model loaded from %s on %s",
                self.weights_path,
                next(self.model.parameters()).device,
            )
        except Exception as exc:
            self.model = None
            rospy.logerr("Unable to load YOLOv5 model: %s", exc)

    def handle_classification(self, request):
        if self.model is None:
            return ClassifyResponse(class_id=-1, confidence=0.0)

        try:
            image = self.bridge.imgmsg_to_cv2(request.image, desired_encoding="bgr8")
            class_id, confidence = self.classify(image)
            return ClassifyResponse(class_id=class_id, confidence=confidence)
        except Exception as exc:
            rospy.logerr("Classification failed: %s", exc)
            return ClassifyResponse(class_id=-1, confidence=0.0)

    def classify(self, image):
        results = self.model(image, size=self.image_size)
        detections = results.pandas().xyxy[0]

        if detections.empty:
            return -1, 0.0

        best = detections.loc[detections["confidence"].idxmax()]
        class_id = int(best["class"])
        confidence = float(best["confidence"])

        if class_id < 0 or class_id >= len(CLASS_NAMES):
            rospy.logwarn("Model returned unsupported class id %d", class_id)
            return -1, 0.0

        rospy.loginfo(
            "Detected %s with %.1f%% confidence",
            CLASS_NAMES[class_id],
            confidence * 100.0,
        )
        return class_id, confidence


if __name__ == "__main__":
    try:
        VisionNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
