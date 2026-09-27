#!/usr/bin/env python3
"""USB camera publisher for the DOFBOT waste-sorting pipeline."""

import cv2
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image


class CameraNode:
    def __init__(self):
        rospy.init_node("dofbot_camera")

        self.camera_index = int(rospy.get_param("~camera_index", 0))
        self.width = int(rospy.get_param("~width", 640))
        self.height = int(rospy.get_param("~height", 480))
        self.fps = float(rospy.get_param("~fps", 10.0))
        self.topic = rospy.get_param("~topic", "/dofbot_camera/image_raw")

        self.bridge = CvBridge()
        self.publisher = rospy.Publisher(self.topic, Image, queue_size=2)
        self.capture = cv2.VideoCapture(self.camera_index)

        if not self.capture.isOpened():
            raise RuntimeError(f"Unable to open camera index {self.camera_index}")

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.capture.set(cv2.CAP_PROP_FPS, self.fps)

        rospy.on_shutdown(self.close)
        rospy.loginfo(
            "DOFBOT camera ready: index=%d, topic=%s, target=%dx%d@%.1f",
            self.camera_index,
            self.topic,
            self.width,
            self.height,
            self.fps,
        )

    def run(self):
        rate = rospy.Rate(self.fps)
        consecutive_errors = 0

        while not rospy.is_shutdown():
            ok, frame = self.capture.read()
            if not ok:
                consecutive_errors += 1
                rospy.logwarn_throttle(2.0, "Camera frame acquisition failed")
                if consecutive_errors >= 20:
                    raise RuntimeError("Too many consecutive camera read failures")
                rate.sleep()
                continue

            consecutive_errors = 0
            frame = cv2.resize(frame, (self.width, self.height))
            message = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            message.header.stamp = rospy.Time.now()
            message.header.frame_id = "dofbot_camera"
            self.publisher.publish(message)
            rate.sleep()

    def close(self):
        if self.capture is not None:
            self.capture.release()


if __name__ == "__main__":
    try:
        CameraNode().run()
    except rospy.ROSInterruptException:
        pass
    except Exception as exc:
        rospy.logfatal("Camera node stopped: %s", exc)
