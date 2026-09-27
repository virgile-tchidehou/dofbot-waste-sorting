<div align="center">

# 🤖 DOFBOT Waste Sorting

**Vision-guided robotic sorting with Jetson Nano, ROS 1 and YOLOv5**

Personal robotics project built on the **Yahboom DOFBOT** platform.

</div>

---

## Context

DOFBOT is a 6-axis educational robotic arm designed around vision, ROS and AI experimentation on embedded platforms such as the NVIDIA Jetson Nano. Yahboom provides the hardware platform, low-level arm library and learning material; this repository contains my own waste-sorting pipeline built on top of that kit.

The objective is simple: take a camera image, classify the object, map the class to a destination bin and execute a calibrated pick-and-place sequence with the arm.

This repository is therefore not a copy of the vendor examples. It is a project layer focused on:

- ROS integration;
- camera acquisition;
- waste classification;
- robotic pick-and-place;
- I²C triggering;
- calibration tooling;
- model training and evaluation utilities.

---

## System Pipeline

```text
Object detector / trigger
          │
          ▼
   DOFBOT camera
          │
          ▼
  /dofbot_camera/image_raw
          │
          ▼
   YOLOv5 vision service
      /vision/classify
          │
          ▼
 class id + confidence
          │
          ▼
 sorting controller
          │
          ├── calibrated joint presets
          ├── Arm_Lib
          └── destination bin
```

The current class mapping is:

| Class ID | Category | Destination |
|---:|---|---|
| 0 | dangereux | dangerous-waste bin |
| 1 | menagers | household-waste bin |
| 2 | recyclables | recyclable-waste bin |

---

## Hardware Context

The project targets a Yahboom DOFBOT robotic arm with:

- 6 servo axes including the gripper;
- NVIDIA Jetson Nano as the main computer;
- USB camera;
- Yahboom `Arm_Lib` for servo control;
- optional external detector connected over I²C.

The project can be explored without the physical arm, but movement and end-to-end validation require the DOFBOT hardware.

---

## Repository Structure

```text
dofbot-waste-sorting/
├── data/
│   └── samples/             # Small evaluation image set
├── docs/
│   ├── guides/              # Calibration, deployment and network setup
│   └── technical/           # Architecture and ROS/vision documentation
├── ml/                      # Model training and evaluation workspace
├── ros/
│   └── dofbot_waste_sorting/
│       ├── config/          # Camera, vision and calibrated arm poses
│       ├── launch/
│       ├── scripts/
│       └── srv/
├── tests/                   # Configuration and integration checks
├── tools/                   # Calibration and model utilities
├── web/                     # Browser-based calibration interface
├── QUICKSTART.md
└── requirements.txt
```

---

## ROS Package

The ROS package is:

```text
dofbot_waste_sorting
```

Main nodes:

| Node | Role |
|---|---|
| `camera_node.py` | publishes USB camera frames |
| `vision_node.py` | exposes the YOLOv5 classification service |
| `sorting_controller_node.py` | coordinates detection, classification and arm motion |
| `sorting_sequence_demo.py` | validates calibrated positions directly with `Arm_Lib` |

Launch the complete pipeline with:

```bash
roslaunch dofbot_waste_sorting sorting.launch
```

---

## Model Files

Large trained weights and full datasets are deliberately not stored in Git.

By default, the vision node looks for:

```text
~/dofbot_models/best.pt
```

You can also point to another weights file with:

```bash
export DOFBOT_MODEL_PATH=/absolute/path/to/best.pt
```

The `ml/` directory keeps the training configuration and reproducibility scripts without turning the repository into model storage.

---

## Calibration

Joint positions are stored in:

```text
ros/dofbot_waste_sorting/config/positions.yaml
```

They are hardware-specific and must be checked before use on another DOFBOT.

Two calibration workflows are included:

```bash
python3 tools/calibrate_positions.py
python3 tools/calibration_server.py
```

The second command exposes the calibration backend used by `web/calibration_interface.html`.

---

## Quick Start

See [QUICKSTART.md](QUICKSTART.md).

Technical documentation starts at [docs/INDEX.md](docs/INDEX.md).

---

## Project Scope

This project is a robotics proof of concept and engineering playground around the DOFBOT platform. It is intended to demonstrate the complete chain from perception to manipulation rather than provide a production waste-management system.

The repository is maintained by **Dodji Virgile TCHIDEHOU**.

---

## Upstream Platform

- Yahboom DOFBOT Jetson Nano repository: https://github.com/YahboomTechnology/dofbot-jetson_nano
- Yahboom Technology: https://github.com/YahboomTechnology
