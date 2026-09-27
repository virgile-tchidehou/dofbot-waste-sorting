# Vision Pipeline

## Goal

The vision layer turns a ROS camera frame into one of the three waste classes used by the sorting controller.

## Input

`camera_node.py` publishes a `sensor_msgs/Image` on:

```text
/dofbot_camera/image_raw
```

The controller captures one frame when an object is ready for classification and sends that frame to `/vision/classify`.

## Model

The implementation targets a custom YOLOv5 model.

The trained weights are intentionally not committed. Supply them with either:

```text
models/best.pt
```

or:

```bash
export DOFBOT_MODEL_PATH=/absolute/path/to/best.pt
```

For a Jetson that already has a local YOLOv5 checkout:

```bash
export YOLOV5_REPO=/absolute/path/to/yolov5
```

This avoids downloading the framework again at runtime.

## Classes

```text
0 dangereux
1 menagers
2 recyclables
```

The mapping must stay aligned with `config/positions.yaml` and the dataset configuration.

## Inference flow

```text
ROS Image
   │
   ▼
CvBridge -> OpenCV BGR frame
   │
   ▼
YOLOv5 inference
   │
   ▼
highest-confidence detection
   │
   ▼
class_id + confidence
```

No fake classification is used when the model is missing. The service returns `-1, 0.0`, allowing the controller to reject the object safely.

## Thresholds

The node exposes ROS parameters for:

- confidence threshold;
- IoU threshold;
- input image size.

A second minimum-confidence check exists in `config/positions.yaml` at controller level. This keeps model inference settings separate from the manipulation acceptance rule.

## Evaluation

Use the small sample set with:

```bash
python3 tools/evaluate_samples.py
```

Model training and larger-scale evaluation belong in `ml/`.
