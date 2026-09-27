<div align="center">

# 🤖 TRC 2025 — DOFbot Waste Sorting

**ROS 1 • Jetson Nano • Computer Vision • YOLO • Web Calibration**

Autonomous waste-sorting project developed by the **UCAO-TECH** team for the TRC 2025 robotics competition.

</div>

---

## Overview

This repository contains the software developed around a Yahboom DOFbot robotic arm for automatic waste sorting.

The system combines:

- camera acquisition on the Jetson Nano;
- computer-vision classification;
- ROS services and nodes for system coordination;
- DOFbot arm control for pick-and-place operations;
- I²C communication with external electronics;
- console and browser-based calibration tools.

The classification workflow uses three project categories:

- **dangereux**
- **ménagers**
- **recyclables**

> This repository is kept as an engineering project archive and demonstration. Robot-specific calibration values, trained model weights and the complete training dataset are intentionally not versioned.

---

## Architecture

```text
Camera
  │
  ▼
final_camera_node.py
  │  /dofbot_camera/image_raw
  ▼
vision_node.py
  │  ROS classification service
  ▼
i2c_controller_node.py
  │
  ├── DOFbot / Arm_Lib
  └── external I²C detection
```

A separate WebSocket calibration server connects the robotic arm to the browser interface in `web/`.

---

## Repository Structure

```text
.
├── config/                  # Camera, positions and vision parameters
├── docs/
│   ├── guides/              # Calibration, deployment, network and competition guides
│   └── technical/           # Architecture, API, testing and vision documentation
├── images/                  # Small validation image set used by local test scripts
├── ros_package/             # ROS package: dofbot_tri
│   ├── launch/
│   ├── scripts/
│   └── srv/
├── scripts/                 # Calibration and model test utilities
├── tests/                   # Camera, vision, movement and integration tests
├── trc2025_train_models/    # Training configuration and reproducibility scripts
├── web/                     # Browser calibration interface
├── QUICKSTART.md
└── requirements.txt
```

---

## Main Components

| Component | Role |
|---|---|
| `final_camera_node.py` | Captures frames and publishes ROS images |
| `vision_node.py` | Loads the vision model and exposes the classification service |
| `i2c_controller_node.py` | Coordinates detection, classification and arm movement |
| `tri.launch` | Starts the main ROS nodes |
| `calibrate_positions.py` | Console-based servo calibration |
| `calibration_server.py` | WebSocket bridge for remote calibration |
| `calibration_interface.html` | Browser interface for joint control and saved positions |

---

## Quick Start

Clone the repository:

```bash
git clone https://github.com/virgile-tchidehou/projet_robotique2k25UCAO.git
cd projet_robotique2k25UCAO
```

Install the Python dependencies required by your Jetson/ROS environment:

```bash
pip3 install -r requirements.txt
```

Create a Catkin workspace and expose the ROS package:

```bash
mkdir -p ~/catkin_ws/src
ln -s "$(pwd)/ros_package" ~/catkin_ws/src/dofbot_tri

cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

Launch the ROS system:

```bash
roslaunch dofbot_tri tri.launch
```

See [QUICKSTART.md](QUICKSTART.md) and [docs/guides/DEPLOYMENT.md](docs/guides/DEPLOYMENT.md) for the environment-specific setup.

---

## Calibration Interface

Start the WebSocket calibration server:

```bash
python3 scripts/calibration_server.py
```

Then open `web/calibration_interface.html` in a browser and configure the Jetson address if the interface runs on another machine.

The server can also operate in simulation mode when `Arm_Lib` is unavailable.

---

## Vision Model and Dataset

The project code expects the trained model to be provided separately. Large ML artifacts are excluded from Git:

- `*.pt`, `*.pth`, `*.onnx`, `*.engine`
- full training/validation datasets;
- generated training outputs.

The repository keeps the training configuration, scripts and a small image set so the workflow remains understandable without turning the Git repository into model storage.

---

## Documentation

- [Documentation index](docs/INDEX.md)
- [Calibration guide](docs/guides/CALIBRATION.md)
- [Deployment guide](docs/guides/DEPLOYMENT.md)
- [Network configuration](docs/guides/NETWORK_CONFIG.md)
- [TRC 2025 competition notes](docs/guides/COMPETITION_TRC2025.md)
- [System architecture](docs/technical/ARCHITECTURE.md)
- [Vision node](docs/technical/VISION_NODE.md)
- [Testing](docs/technical/TESTING.md)
- [Training workspace](trc2025_train_models/README.md)

---

## Project Status

The repository represents the **2025 competition-era implementation**. It is retained as a technical record of the robotics work rather than presented as a currently maintained production system.

For newer experiments and reusable robotics work, see the broader `robotics-lab` repository.

---

## Team

Developed within **UCAO-TECH** for TRC 2025.

Repository maintained by **Dodji Virgile TCHIDEHOU**.
