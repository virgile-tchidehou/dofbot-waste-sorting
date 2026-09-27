#!/usr/bin/env python3
"""Main perception-to-manipulation controller for DOFBOT waste sorting."""

from pathlib import Path
import time

import rospy
import yaml
from sensor_msgs.msg import Image

from Arm_Lib import Arm_Device
from dofbot_waste_sorting.srv import Classify, ClassifyRequest

try:
    import smbus
except ImportError:
    smbus = None


class DofbotSortingController:
    def __init__(self):
        rospy.init_node("waste_sorting_controller")

        self.camera_topic = rospy.get_param("~camera_topic", "/dofbot_camera/image_raw")
        self.use_i2c = bool(rospy.get_param("~use_i2c", True))
        self.i2c_address = int(rospy.get_param("~i2c_address", 0x08))
        self.i2c_register = int(rospy.get_param("~i2c_register", 0))
        self.move_duration_ms = int(rospy.get_param("~move_duration_ms", 1200))

        default_config = self._source_root() / "config" / "positions.yaml"
        config_path = Path(
            rospy.get_param("~positions_config", str(default_config))
        ).expanduser()
        self.config = self._load_config(config_path)

        self.arm = Arm_Device()
        time.sleep(1.0)
        self.arm.Arm_serial_set_torque(1)

        self.bus = None
        if self.use_i2c:
            if smbus is None:
                rospy.logwarn("smbus is unavailable; I2C triggering is disabled")
                self.use_i2c = False
            else:
                try:
                    self.bus = smbus.SMBus(1)
                    rospy.loginfo("I2C trigger enabled at address 0x%02X", self.i2c_address)
                except Exception as exc:
                    rospy.logwarn("I2C unavailable: %s", exc)
                    self.use_i2c = False

        rospy.loginfo("Waiting for /vision/classify")
        rospy.wait_for_service("vision/classify")
        self.classify_service = rospy.ServiceProxy("vision/classify", Classify)

        self.move_to("home_position")
        rospy.loginfo("DOFBOT sorting controller ready")

    @staticmethod
    def _source_root():
        current = Path(__file__).resolve()
        try:
            return current.parents[3]
        except IndexError:
            return Path.cwd()

    @staticmethod
    def _load_config(path):
        if not path.exists():
            raise FileNotFoundError(f"Position configuration not found: {path}")
        with path.open("r", encoding="utf-8") as stream:
            return yaml.safe_load(stream)

    def _angles_from_pose(self, pose):
        return [
            int(pose["joint1"]),
            int(pose["joint2"]),
            int(pose["joint3"]),
            int(pose["joint4"]),
            int(pose["joint5"]),
            int(pose.get("gripper", self.config["movement"]["gripper_open"])),
        ]

    def _within_limits(self, angles):
        names = ["joint1", "joint2", "joint3", "joint4", "joint5", "gripper"]
        for name, value in zip(names, angles):
            lower, upper = self.config["limits"][name]
            if not lower <= value <= upper:
                rospy.logerr("%s=%s is outside [%s, %s]", name, value, lower, upper)
                return False
        return True

    def move_angles(self, angles, duration_ms=None):
        duration_ms = int(duration_ms or self.move_duration_ms)
        if not self._within_limits(angles):
            return False

        self.arm.Arm_serial_servo_write6_array(angles, duration_ms)
        time.sleep(duration_ms / 1000.0 + self.config["movement"]["delays"]["after_move"])
        return True

    def move_to(self, pose_name, gripper=None):
        pose = dict(self.config[pose_name])
        if gripper is not None:
            pose["gripper"] = gripper
        return self.move_angles(self._angles_from_pose(pose))

    def move_to_bin(self, bin_name, gripper=None):
        pose = dict(self.config["bins"][bin_name])
        if gripper is not None:
            pose["gripper"] = gripper
        return self.move_angles(self._angles_from_pose(pose))

    def set_gripper(self, angle):
        lower, upper = self.config["limits"]["gripper"]
        if not lower <= angle <= upper:
            raise ValueError(f"Gripper angle {angle} outside [{lower}, {upper}]")
        self.arm.Arm_serial_servo_write(6, int(angle), 700)
        time.sleep(self.config["movement"]["delays"]["after_gripper"])

    def object_detected(self):
        if not self.use_i2c or self.bus is None:
            return False
        try:
            return self.bus.read_byte_data(self.i2c_address, self.i2c_register) == 1
        except Exception as exc:
            rospy.logwarn_throttle(2.0, "I2C read failed: %s", exc)
            return False

    def reset_detection(self):
        if not self.use_i2c or self.bus is None:
            return
        try:
            self.bus.write_byte_data(self.i2c_address, self.i2c_register, 0)
        except Exception as exc:
            rospy.logwarn("Unable to reset I2C detection flag: %s", exc)

    def capture_image(self):
        try:
            return rospy.wait_for_message(self.camera_topic, Image, timeout=5.0)
        except rospy.ROSException:
            rospy.logwarn("No image received from %s", self.camera_topic)
            return None

    def classify(self, image):
        request = ClassifyRequest(image=image)
        response = self.classify_service(request)
        return int(response.class_id), float(response.confidence)

    def execute_sort(self, bin_name):
        movement = self.config["movement"]
        open_gripper = int(movement["gripper_open"])
        closed_gripper = int(movement["gripper_close"])

        sequence_ok = (
            self.move_to("safe_position", gripper=open_gripper)
            and self.move_to("pick_position", gripper=open_gripper)
        )
        if not sequence_ok:
            return False

        self.set_gripper(closed_gripper)
        time.sleep(movement["delays"]["after_grasp"])

        if not self.move_to("safe_position", gripper=closed_gripper):
            return False
        if not self.move_to_bin(bin_name, gripper=closed_gripper):
            return False

        self.set_gripper(open_gripper)
        time.sleep(movement["delays"]["after_release"])

        return (
            self.move_to("safe_position", gripper=open_gripper)
            and self.move_to("home_position", gripper=open_gripper)
        )

    def process_object(self):
        self.reset_detection()

        if not self.move_to("observation_position"):
            return

        image = self.capture_image()
        if image is None:
            self.move_to("home_position")
            return

        class_id, confidence = self.classify(image)
        threshold = float(self.config["classification"]["min_confidence"])

        if class_id < 0 or confidence < threshold:
            rospy.logwarn(
                "Object rejected: class=%d confidence=%.2f threshold=%.2f",
                class_id,
                confidence,
                threshold,
            )
            self.move_to("home_position")
            return

        mapping = self.config["class_to_bin"]
        bin_name = mapping.get(class_id, mapping.get(str(class_id)))
        if bin_name not in self.config["bins"]:
            rospy.logerr("No bin configured for class id %d", class_id)
            self.move_to("home_position")
            return

        rospy.loginfo("Sorting class %d into '%s'", class_id, bin_name)
        if not self.execute_sort(bin_name):
            rospy.logerr("Sorting sequence failed")
            self.move_to("home_position")

    def run(self):
        rate = rospy.Rate(2)
        if not self.use_i2c:
            rospy.logwarn(
                "Automatic trigger is disabled. Enable ~use_i2c after connecting the detector."
            )

        while not rospy.is_shutdown():
            if self.object_detected():
                self.process_object()
            rate.sleep()


if __name__ == "__main__":
    try:
        DofbotSortingController().run()
    except rospy.ROSInterruptException:
        pass
    except Exception as exc:
        rospy.logfatal("Sorting controller stopped: %s", exc)
