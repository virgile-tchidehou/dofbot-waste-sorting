# Machine-Learning Workspace

This directory contains the training and evaluation side of the DOFBOT waste-sorting project.

The runtime ROS package does not depend on the training workspace being present on the Jetson. Training can be done on another machine and the resulting weights copied to the robot.

## Classes

```text
0: dangereux
1: menagers
2: recyclables
```

## Structure

```text
ml/
├── config/
│   ├── hyp.yaml
│   └── training_config.yaml
├── data/
│   ├── .gitkeep
│   └── dataset.yaml
├── docs/
│   └── README.md
├── scripts/
│   ├── augment_dataset.py
│   ├── evaluate_dataset.py
│   ├── train_baseline.py
│   ├── train_model.py
│   └── vision_node_example.py
└── requirements.txt
```

## What is not versioned

The repository intentionally excludes:

- complete training and validation image sets;
- generated augmentation outputs;
- trained `.pt` weights;
- exported ONNX/TensorRT models;
- training runs.

This keeps Git focused on source code and reproducibility metadata.

## Dataset configuration

Review:

```text
ml/data/dataset.yaml
```

before starting a training run. Dataset paths are environment-specific.

## Training

Use the scripts as reproducible starting points rather than fixed benchmark recipes.

```bash
python3 ml/scripts/train_baseline.py
python3 ml/scripts/train_model.py --help
```

## Evaluation

```bash
python3 ml/scripts/evaluate_dataset.py --help
python3 tools/evaluate_samples.py --help
```

The small repository sample set under `data/samples/` is for smoke testing and demonstrations; it is not a substitute for a statistically meaningful validation dataset.
