# ROS Interfaces

This page documents the ROS interfaces that are actually implemented in the repository.

## Package

```text
dofbot_waste_sorting
```

## Camera topic

### `/dofbot_camera/image_raw`

Publisher: `camera_node.py`

Type:

```text
sensor_msgs/Image
```

Default acquisition settings:

- camera index: `0`
- width: `640`
- height: `480`
- target rate: `10 Hz`

These values can be overridden with private ROS parameters on the camera node.

## Classification service

### `/vision/classify`

Server: `vision_node.py`

Service definition:

```text
sensor_msgs/Image image
---
int32 class_id
float32 confidence
```

Class mapping:

```text
0 -> dangereux
1 -> menagers
2 -> recyclables
```

If the model is unavailable or no supported object is detected, the node returns:

```text
class_id = -1
confidence = 0.0
```

## Sorting controller

Node: `sorting_controller_node.py`

Important private parameters:

| Parameter | Default |
|---|---|
| `~camera_topic` | `/dofbot_camera/image_raw` |
| `~use_i2c` | `true` |
| `~i2c_address` | `0x08` |
| `~i2c_register` | `0` |
| `~move_duration_ms` | `1200` |
| `~positions_config` | project `config/positions.yaml` |

The controller uses the classification service and the Yahboom `Arm_Lib` API.

## Vision parameters

`vision_node.py` accepts:

| Parameter | Default |
|---|---|
| `~conf_threshold` | `0.60` |
| `~iou_threshold` | `0.45` |
| `~img_size` | `640` |
| `~weights_path` | `models/best.pt` in source checkout |

Environment variables:

- `DOFBOT_MODEL_PATH` — absolute path to the trained weights;
- `YOLOV5_REPO` — optional local YOLOv5 repository for offline loading.

## Launch

```bash
roslaunch dofbot_waste_sorting sorting.launch
```

Disable the external I²C trigger during ROS-stack validation with:

```bash
roslaunch dofbot_waste_sorting sorting.launch use_i2c:=false
```
