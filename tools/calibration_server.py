#!/usr/bin/env python3
"""WebSocket backend for the DOFBOT browser calibration interface."""

import asyncio
from datetime import datetime
import json
from pathlib import Path
import time

import websockets
import yaml

try:
    from Arm_Lib import Arm_Device
except ImportError:
    Arm_Device = None


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "positions.yaml"
JOINT_KEYS = ["joint1", "joint2", "joint3", "joint4", "joint5", "gripper"]


class CalibrationServer:
    def __init__(self):
        self.config = self._load_config()
        self.current_angles = self._pose_to_angles(self.config["home_position"])
        self.clients = set()

        self.arm = None
        if Arm_Device is not None:
            try:
                self.arm = Arm_Device()
                time.sleep(0.5)
            except Exception as exc:
                print(f"Arm connection unavailable: {exc}")

        self.simulation_mode = self.arm is None

    def _load_config(self):
        with CONFIG_PATH.open("r", encoding="utf-8") as stream:
            return yaml.safe_load(stream)

    def _save_config(self):
        with CONFIG_PATH.open("w", encoding="utf-8") as stream:
            yaml.safe_dump(
                self.config,
                stream,
                sort_keys=False,
                allow_unicode=True,
            )

    def _pose_to_angles(self, pose):
        default_gripper = self.config["movement"]["gripper_open"]
        return [
            int(pose["joint1"]),
            int(pose["joint2"]),
            int(pose["joint3"]),
            int(pose["joint4"]),
            int(pose["joint5"]),
            int(pose.get("gripper", default_gripper)),
        ]

    def _check_angle(self, index, angle):
        key = JOINT_KEYS[index]
        lower, upper = self.config["limits"][key]
        if not lower <= angle <= upper:
            raise ValueError(f"{key}: {angle} outside [{lower}, {upper}]")

    def move_joint(self, joint_id, angle):
        index = int(joint_id) - 1
        if index not in range(6):
            raise ValueError("joint id must be between 1 and 6")

        angle = int(angle)
        self._check_angle(index, angle)
        self.current_angles[index] = angle

        if self.arm is not None:
            self.arm.Arm_serial_servo_write(index + 1, angle, 500)

    def save_position(self, name, angles):
        if len(angles) != 6:
            raise ValueError("a position must contain six joint values")

        values = [int(value) for value in angles]
        for index, value in enumerate(values):
            self._check_angle(index, value)

        pose = dict(zip(JOINT_KEYS, values))
        aliases = {
            "home": "home_position",
            "observation": "observation_position",
            "safe": "safe_position",
            "pick": "pick_position",
        }

        if name in self.config["bins"]:
            self.config["bins"][name].update(pose)
        else:
            key = aliases.get(name)
            if key is None:
                raise ValueError(f"unsupported position name: {name}")
            self.config[key] = pose

        self.current_angles = values
        self._save_config()

    def frontend_positions(self):
        return {
            "home": self.config["home_position"],
            "observation": self.config["observation_position"],
            "bins": self.config["bins"],
        }

    async def send(self, websocket, payload):
        await websocket.send(json.dumps(payload, ensure_ascii=False))

    async def log(self, websocket, message, level="info"):
        await self.send(
            websocket,
            {
                "type": "log",
                "message": message,
                "level": level,
                "timestamp": datetime.now().isoformat(),
            },
        )

    async def handle_message(self, websocket, message):
        data = json.loads(message)
        command = data.get("command")
        params = data.get("data") or {}

        if command == "move_joint":
            self.move_joint(params["joint"], params["angle"])
            await self.log(
                websocket,
                f"Joint {params['joint']} moved to {params['angle']}°",
                "success",
            )
            return

        if command == "save_position":
            self.save_position(params["name"], params["angles"])
            await self.log(
                websocket,
                f"Position '{params['name']}' saved",
                "success",
            )
            await self.send(
                websocket,
                {"type": "positions", "data": self.frontend_positions()},
            )
            return

        if command == "get_positions":
            await self.send(
                websocket,
                {"type": "positions", "data": self.frontend_positions()},
            )
            return

        if command == "get_status":
            await self.send(
                websocket,
                {
                    "type": "status",
                    "simulation_mode": self.simulation_mode,
                    "current_angles": self.current_angles,
                },
            )
            return

        await self.log(websocket, f"Unknown command: {command}", "warning")

    async def handle_client(self, websocket, path=None):
        self.clients.add(websocket)
        try:
            await self.log(
                websocket,
                "Calibration backend connected",
                "success",
            )
            await self.send(
                websocket,
                {
                    "type": "status",
                    "simulation_mode": self.simulation_mode,
                    "current_angles": self.current_angles,
                },
            )
            await self.send(
                websocket,
                {"type": "positions", "data": self.frontend_positions()},
            )

            async for message in websocket:
                try:
                    await self.handle_message(websocket, message)
                except Exception as exc:
                    await self.log(websocket, str(exc), "error")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)

    async def serve(self, host="0.0.0.0", port=8765):
        mode = "simulation" if self.simulation_mode else "hardware"
        print(f"DOFBOT calibration server: ws://{host}:{port} ({mode})")
        async with websockets.serve(self.handle_client, host, port):
            await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(CalibrationServer().serve())
    except KeyboardInterrupt:
        print("\nServer stopped.")
