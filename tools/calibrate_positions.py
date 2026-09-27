#!/usr/bin/env python3
"""Cross-platform console calibration tool for the DOFBOT arm."""

from pathlib import Path
import shlex
import time

import yaml

try:
    from Arm_Lib import Arm_Device
except ImportError:
    Arm_Device = None


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "ros" / "dofbot_waste_sorting" / "config" / "positions.yaml"
JOINT_KEYS = ["joint1", "joint2", "joint3", "joint4", "joint5", "gripper"]


class CalibrationSession:
    def __init__(self, config_path=DEFAULT_CONFIG):
        self.config_path = Path(config_path).expanduser().resolve()
        self.config = self._load_config()
        self.current_angles = self._pose_to_angles(self.config["home_position"])

        self.arm = None
        if Arm_Device is not None:
            try:
                self.arm = Arm_Device()
                time.sleep(0.5)
                print("Physical DOFBOT detected.")
            except Exception as exc:
                print(f"Arm_Lib available but the arm could not be opened: {exc}")

        if self.arm is None:
            print("Simulation mode: commands update values without moving hardware.")

    def _load_config(self):
        with self.config_path.open("r", encoding="utf-8") as stream:
            return yaml.safe_load(stream)

    def _save_config(self):
        with self.config_path.open("w", encoding="utf-8") as stream:
            yaml.safe_dump(
                self.config,
                stream,
                sort_keys=False,
                allow_unicode=True,
            )

    def _pose_to_angles(self, pose):
        open_gripper = self.config["movement"]["gripper_open"]
        return [
            int(pose["joint1"]),
            int(pose["joint2"]),
            int(pose["joint3"]),
            int(pose["joint4"]),
            int(pose["joint5"]),
            int(pose.get("gripper", open_gripper)),
        ]

    def _check_angle(self, joint_index, angle):
        key = JOINT_KEYS[joint_index]
        lower, upper = self.config["limits"][key]
        if not lower <= angle <= upper:
            raise ValueError(f"{key}: {angle} outside [{lower}, {upper}]")

    def move_current(self, duration_ms=800):
        for index, angle in enumerate(self.current_angles):
            self._check_angle(index, angle)

        if self.arm is not None:
            self.arm.Arm_serial_servo_write6_array(
                [int(value) for value in self.current_angles],
                int(duration_ms),
            )
            time.sleep(duration_ms / 1000.0 + 0.2)

        print("Current:", self.current_angles)

    def set_joint(self, joint_id, angle):
        index = int(joint_id) - 1
        if index not in range(6):
            raise ValueError("joint id must be between 1 and 6")

        angle = int(angle)
        self._check_angle(index, angle)
        self.current_angles[index] = angle

        if self.arm is not None:
            self.arm.Arm_serial_servo_write(index + 1, angle, 500)
            time.sleep(0.6)

        print(f"{JOINT_KEYS[index]} = {angle}")

    def resolve_pose(self, name):
        aliases = {
            "home": "home_position",
            "safe": "safe_position",
            "observation": "observation_position",
            "pick": "pick_position",
        }

        config_name = aliases.get(name, name)
        if config_name in self.config:
            return config_name, self.config[config_name]
        if name in self.config["bins"]:
            return name, self.config["bins"][name]
        raise KeyError(f"Unknown pose: {name}")

    def goto(self, name):
        _, pose = self.resolve_pose(name)
        self.current_angles = self._pose_to_angles(pose)
        self.move_current()

    def save(self, name):
        aliases = {
            "home": "home_position",
            "safe": "safe_position",
            "observation": "observation_position",
            "pick": "pick_position",
        }

        values = dict(zip(JOINT_KEYS, map(int, self.current_angles)))

        if name in self.config["bins"]:
            self.config["bins"][name].update(values)
        else:
            key = aliases.get(name, name)
            if key not in {
                "home_position",
                "safe_position",
                "observation_position",
                "pick_position",
            }:
                raise KeyError(
                    "Save target must be home, safe, observation, pick "
                    "or one of the configured bins."
                )
            self.config[key] = values

        self._save_config()
        print(f"Saved '{name}' to {self.config_path}")

    def show(self):
        print("\nJoint values")
        for index, value in enumerate(self.current_angles, start=1):
            print(f"  {index}: {JOINT_KEYS[index - 1]} = {value}")
        print()

    def run(self):
        print(
            """
DOFBOT calibration console

Commands:
  show
  joint <1-6> <angle>
  move <home|safe|observation|pick|bin-name>
  save <home|safe|observation|pick|bin-name>
  quit

Examples:
  joint 2 95
  move observation
  save observation
"""
        )

        while True:
            try:
                parts = shlex.split(input("calibration> ").strip())
                if not parts:
                    continue

                command = parts[0].lower()

                if command in {"quit", "exit", "q"}:
                    break
                if command == "show":
                    self.show()
                elif command == "joint" and len(parts) == 3:
                    self.set_joint(parts[1], parts[2])
                elif command == "move" and len(parts) == 2:
                    self.goto(parts[1])
                elif command == "save" and len(parts) == 2:
                    self.save(parts[1])
                else:
                    print("Unknown or incomplete command.")
            except (ValueError, KeyError) as exc:
                print(f"Error: {exc}")
            except KeyboardInterrupt:
                print()
                break


if __name__ == "__main__":
    CalibrationSession().run()
