# Deployment Guide

This project targets a Yahboom DOFBOT running on a Jetson Nano with a ROS 1 / Catkin environment.

Exact JetPack and ROS versions depend on the system image installed on the robot. Keep the vendor-provided GPU stack intact unless you have a reason to replace it.

## Requirements

- Yahboom DOFBOT
- Jetson Nano
- ROS 1 with Catkin
- Python 3
- OpenCV + `cv_bridge`
- Yahboom `Arm_Lib`
- trained YOLOv5 weights
- optional I²C object detector

## Clone

```bash
git clone https://github.com/virgile-tchidehou/dofbot-waste-sorting.git
cd dofbot-waste-sorting
```

## Python dependencies

```bash
pip3 install -r requirements.txt
```

On Jetson, avoid replacing a working CUDA-enabled PyTorch installation with a generic CPU wheel.

## Catkin workspace

```bash
mkdir -p ~/catkin_ws/src
ln -s "$(pwd)/ros/dofbot_waste_sorting" ~/catkin_ws/src/dofbot_waste_sorting

cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

## Model

Place the model at:

```text
~/dofbot_models/best.pt
```

or define:

```bash
export DOFBOT_MODEL_PATH=/absolute/path/to/best.pt
```

If a local clone of YOLOv5 is already available on the Jetson:

```bash
export YOLOV5_REPO=/absolute/path/to/yolov5
```

## Launch

```bash
roslaunch dofbot_waste_sorting sorting.launch
```

The launch file starts:

- the USB camera publisher;
- the vision classification service;
- the sorting controller.

## I²C trigger

The controller expects bus 1, address `0x08`, register `0` by default.

For ROS-only validation:

```bash
roslaunch dofbot_waste_sorting sorting.launch use_i2c:=false
```

## Before the first physical cycle

Validate each pose independently using the calibration guide. The values in `ros/dofbot_waste_sorting/config/positions.yaml` depend on the physical location of the camera, pick zone and bins.
