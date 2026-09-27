# ML Notes

This folder documents the model-development workflow used by the DOFBOT waste-sorting project.

## Workflow

1. collect and label images for the three project classes;
2. split the dataset into train/validation sets;
3. configure paths in `../data/dataset.yaml`;
4. apply augmentation where useful;
5. train a baseline model;
6. evaluate on held-out data;
7. copy the selected weights to the robot runtime.

## Runtime handoff

The ROS vision node does not read training directories. It only needs a trained weights file supplied through `DOFBOT_MODEL_PATH` or the local `models/best.pt` convention.

## Version-control policy

Datasets, generated runs and model binaries are intentionally excluded from Git. Keep source code, configuration and short technical notes in the repository; store large ML artifacts separately.
