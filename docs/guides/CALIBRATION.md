# DOFBOT Calibration Guide

Calibration is the most hardware-specific part of this project. Never assume that the joint values committed in `config/positions.yaml` are safe for another arm or another physical layout.

## Stored poses

The project currently uses four main poses:

- `home_position`
- `safe_position`
- `observation_position`
- `pick_position`

Each destination bin also has its own joint preset under `bins`.

## Safety first

Before moving the arm:

1. clear the workspace;
2. keep the emergency power switch accessible;
3. verify the arm starts from a known pose;
4. use slow movements while calibrating;
5. test one pose at a time before testing a complete sequence.

## Direct pose validation

The lightweight direct-control script reads `config/positions.yaml` and sends one pose at a time through `Arm_Lib`.

```bash
python3 ros/dofbot_waste_sorting/scripts/sorting_sequence_demo.py home_position
python3 ros/dofbot_waste_sorting/scripts/sorting_sequence_demo.py safe_position
python3 ros/dofbot_waste_sorting/scripts/sorting_sequence_demo.py observation_position
python3 ros/dofbot_waste_sorting/scripts/sorting_sequence_demo.py pick_position
```

A bin name can also be passed:

```bash
python3 ros/dofbot_waste_sorting/scripts/sorting_sequence_demo.py recyclables
```

## Console calibration

```bash
python3 tools/calibrate_positions.py
```

Use this workflow when working directly on the Jetson.

## Browser calibration

Start the WebSocket backend:

```bash
python3 tools/calibration_server.py
```

Then open:

```text
web/calibration_interface.html
```

The browser interface can connect to the Jetson over the local network and move individual joints while showing the current values.

## Configuration file

The canonical pose file is:

```text
config/positions.yaml
```

After calibration, review the diff before committing new values. Calibration is part of the physical setup, not a universal software constant.
