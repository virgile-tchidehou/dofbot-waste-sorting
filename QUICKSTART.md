# Quick Start

## 1. Clone

```bash
git clone https://github.com/virgile-tchidehou/dofbot-waste-sorting.git
cd dofbot-waste-sorting
```

## 2. Install Python dependencies

On Jetson Nano, keep the CUDA-enabled PyTorch/OpenCV versions provided by your JetPack image when possible.

```bash
pip3 install -r requirements.txt
```

The Yahboom `Arm_Lib` package must also be available on the robot.

## 3. Add the ROS package to Catkin

From the repository root:

```bash
mkdir -p ~/catkin_ws/src
ln -s "$(pwd)/ros/dofbot_waste_sorting" ~/catkin_ws/src/dofbot_waste_sorting

cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

## 4. Provide the model

The model is intentionally not versioned.

```bash
mkdir -p models
cp /path/to/best.pt models/best.pt
```

Or:

```bash
export DOFBOT_MODEL_PATH=/absolute/path/to/best.pt
```

## 5. Review calibration before moving the arm

Open:

```text
config/positions.yaml
```

Then validate poses carefully:

```bash
python3 ros/dofbot_waste_sorting/scripts/sorting_sequence_demo.py home_position
```

## 6. Launch

```bash
roslaunch dofbot_waste_sorting sorting.launch
```

To disable the external I²C trigger while validating the ROS stack:

```bash
roslaunch dofbot_waste_sorting sorting.launch use_i2c:=false
```

## 7. Calibration tools

```bash
python3 tools/calibrate_positions.py
python3 tools/calibration_server.py
```

Then open `web/calibration_interface.html`.

See [docs/INDEX.md](docs/INDEX.md) for the rest of the documentation.
