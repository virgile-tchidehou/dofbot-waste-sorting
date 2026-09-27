# Web Calibration Interface

The browser interface provides a visual way to adjust DOFBOT joints and save named poses through the calibration WebSocket backend.

## Start the backend

From the repository root:

```bash
python3 tools/calibration_server.py
```

The default server listens on:

```text
ws://0.0.0.0:8765
```

## Open the interface

You can open `calibration_interface.html` directly, or serve the folder locally:

```bash
cd web
python3 -m http.server 8080
```

Then open:

```text
http://localhost:8080
```

## Remote Jetson connection

If the browser runs on another computer:

1. get the Jetson IP with `hostname -I`;
2. open the server configuration dialog in the interface;
3. enter the Jetson IP and port `8765`;
4. connect.

## Supported backend commands

The interface uses:

- `move_joint`
- `save_position`
- `get_positions`
- `get_status`

The selected address is stored in browser local storage rather than committed to the repository.

## Safety

The interface can command real servos. Validate limits and keep the robot workspace clear before connecting to physical hardware.
