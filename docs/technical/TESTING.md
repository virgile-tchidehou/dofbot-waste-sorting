# Testing

The project contains a mix of software-only checks and hardware-dependent tests.

## Software-only checks

These should work without the physical arm when the required Python packages are installed:

- configuration parsing;
- image preprocessing;
- class-to-bin mapping;
- repository consistency checks.

Run:

```bash
python3 check_consistency.py
python3 tests/test_integration.py
```

Some test modules also use OpenCV and NumPy.

## Vision tests

The trained weights are not stored in the repository. Tests that require `best.pt` must either:

- receive a local weights path;
- or skip gracefully when the file is absent.

The small image set is stored under:

```text
data/samples/
```

## Hardware tests

The following require a real DOFBOT or part of the physical setup:

- USB camera acquisition;
- `Arm_Lib` servo commands;
- I²C trigger communication;
- full pick-and-place sequences.

Validate one component at a time before launching the complete pipeline.

## Recommended order

1. run `check_consistency.py`;
2. validate configuration;
3. test camera acquisition;
4. validate model loading;
5. calibrate each arm pose;
6. test the direct sorting sequence;
7. enable the I²C trigger;
8. run the complete ROS launch file.

## Safety

Tests that command the arm are not ordinary unit tests. Keep the workspace clear and start with slow, isolated pose validation.
