# Changelog

## 2026-09 — Repository refactor

- Renamed the project to `dofbot-waste-sorting`.
- Reframed the repository as a personal robotics project built on the Yahboom DOFBOT platform.
- Reorganized the source tree into `ros/`, `ml/`, `tools/` and `data/`.
- Renamed the ROS package to `dofbot_waste_sorting`.
- Consolidated the duplicated vision node into one implementation.
- Reworked the sorting controller around explicit calibrated joint presets.
- Aligned the camera topic and classification service across the ROS pipeline.
- Removed obsolete internal maintenance and event-specific material.
- Rewrote the public documentation around the actual codebase.

## Earlier development

The repository started as an experimental DOFBOT vision-and-manipulation workspace. It includes camera acquisition, ROS coordination, object classification, arm calibration, I²C triggering and machine-learning utilities.
