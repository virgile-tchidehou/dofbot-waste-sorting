# Quick Start

This guide gets the repository into a ROS Catkin workspace without relying on the old repository layout.

## 1. Clone

```bash
git clone https://github.com/virgile-tchidehou/projet_robotique2k25UCAO.git
cd projet_robotique2k25UCAO
```

## 2. Install Python dependencies

Use the Python/JetPack environment already configured on the Jetson when possible.

```bash
pip3 install -r requirements.txt
```

The DOFbot `Arm_Lib` package and ROS dependencies are hardware/environment specific and may need to be installed separately.

## 3. Add the ROS package to Catkin

From the repository root:

```bash
mkdir -p ~/catkin_ws/src
ln -s "$(pwd)/ros_package" ~/catkin_ws/src/dofbot_tri

cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

## 4. Launch

```bash
roslaunch dofbot_tri tri.launch
```

The launch file also expects the DOFbot kinematics package/service used by the original robot environment.

## 5. Calibration

Console:

```bash
python3 scripts/calibrate_positions.py
```

Browser interface:

```bash
python3 scripts/calibration_server.py
```

Then open `web/calibration_interface.html`.

## 6. Tests

Examples:

```bash
python3 tests/test_camera.py
python3 tests/test_vision_node.py
python3 tests/test_dofbot_movements.py
```

Some tests require the physical robot, camera, ROS services or model weights.

For more detail, see [docs/INDEX.md](docs/INDEX.md).
