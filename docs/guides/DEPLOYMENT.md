# Deployment Guide

This guide reflects the repository as it exists today. The project was developed for a DOFbot/Jetson ROS 1 environment; exact ROS and JetPack versions depend on the image installed on the robot.

## Prerequisites

- Yahboom DOFbot with Jetson Nano
- ROS 1 / Catkin environment compatible with the robot image
- Python 3
- OpenCV and `cv_bridge`
- Yahboom `Arm_Lib`
- the external DOFbot kinematics package used by `tri.launch`
- trained model weights supplied separately

The repository itself does not include the large model weights or complete training dataset.

## Clone

```bash
git clone https://github.com/virgile-tchidehou/projet_robotique2k25UCAO.git
cd projet_robotique2k25UCAO
```

## Python dependencies

Use the packages already provided by JetPack/your robot image when possible, especially CUDA-enabled PyTorch and OpenCV.

```bash
pip3 install -r requirements.txt
```

Do not blindly replace the Jetson-specific PyTorch build with a generic desktop wheel.

## Catkin workspace

From the repository root:

```bash
mkdir -p ~/catkin_ws/src
ln -s "$(pwd)/ros_package" ~/catkin_ws/src/dofbot_tri

cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

## Launch the robot workflow

```bash
roslaunch dofbot_tri tri.launch
```

The launch file starts the project vision and controller nodes and expects the DOFbot kinematics service from the original robot environment.

## Camera check

The camera node uses OpenCV device index `0`.

```bash
python3 - <<'PY'
import cv2
cap = cv2.VideoCapture(0)
print("camera available:", cap.isOpened())
cap.release()
PY
```

## DOFbot library check

```bash
python3 - <<'PY'
from Arm_Lib import Arm_Device
arm = Arm_Device()
print("Arm_Lib available")
PY
```

Only run movement tests with the workspace clear and the arm in a safe mechanical configuration.

## Calibration

Console calibration:

```bash
python3 scripts/calibrate_positions.py
```

Web calibration server:

```bash
python3 scripts/calibration_server.py
```

Then open `web/calibration_interface.html`. If the browser is on another device, configure the Jetson IP in the interface/configuration.

## Model weights

The vision node expects a trained model under the project model path. Model files such as `*.pt` are deliberately excluded from Git because they are large generated artifacts.

## Validation

Useful checks include:

```bash
python3 tests/test_camera.py
python3 tests/test_vision_node.py
python3 tests/test_dofbot_movements.py
python3 tests/test_integration.py
```

Some tests require hardware, ROS services or model weights and are not expected to pass in a generic desktop environment.

## Troubleshooting

For network/calibration issues, see:

- [Network configuration](NETWORK_CONFIG.md)
- [Calibration guide](CALIBRATION.md)
- [Web interface guide](../../web/README.md)

For architecture details, see [../technical/ARCHITECTURE.md](../technical/ARCHITECTURE.md).
