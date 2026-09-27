# System Architecture

## Purpose

This project explores an end-to-end robotics problem on the Yahboom DOFBOT platform: perceive an object, classify it, select a destination and execute a repeatable manipulation sequence.

## Layers

### 1. Perception

`camera_node.py` reads a USB camera and publishes:

```text
/dofbot_camera/image_raw
```

The message type is `sensor_msgs/Image`.

### 2. Classification

`vision_node.py` exposes:

```text
/vision/classify
```

using the project service `Classify.srv`.

Input:

```text
sensor_msgs/Image image
```

Output:

```text
int32 class_id
float32 confidence
```

The node loads a YOLOv5 custom model from a path supplied through a ROS parameter or `DOFBOT_MODEL_PATH`.

### 3. Decision and manipulation

`sorting_controller_node.py`:

1. waits for an external object-detection trigger;
2. moves the arm to the observation pose;
3. requests a camera frame;
4. calls the vision service;
5. maps the returned class to a configured bin;
6. performs the pick-and-place sequence through `Arm_Lib`.

### 4. Trigger input

The optional external detector is read over I²C:

```text
bus:      1
address:  0x08
register: 0
```

These values can be overridden through ROS parameters.

### 5. Calibration

Joint presets live in `ros/dofbot_waste_sorting/config/positions.yaml`.

Calibration is deliberately kept outside the controller code so the software can be adapted to a different physical layout without rewriting the state flow.

## Data flow

```text
I²C detector
     │
     ▼
sorting controller
     │
     ├── move to observation
     │
     ▼
camera node ──► ROS Image
     │
     ▼
vision service ──► class id + confidence
     │
     ▼
class-to-bin mapping
     │
     ▼
Arm_Lib pick-and-place sequence
```

## Design boundaries

The repository does not include:

- the trained model weights;
- the complete training dataset;
- the Yahboom low-level SDK;
- the Jetson system image.

Those pieces belong to the runtime environment rather than the source repository.
