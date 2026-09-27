# Network Configuration

The core ROS pipeline can run entirely on the Jetson Nano. Network access is mainly useful for SSH and the browser-based calibration interface.

## Find the Jetson IP

```bash
hostname -I
```

## Test from another computer

```bash
ping <JETSON_IP>
ssh <user>@<JETSON_IP>
```

## Web calibration

The calibration backend listens on port `8765` by default:

```bash
python3 tools/calibration_server.py
```

Open `web/calibration_interface.html` on another computer and configure the Jetson IP in the interface.

If a firewall is enabled, allow the WebSocket port only on the trusted local network:

```bash
sudo ufw allow 8765/tcp
```

## Recommended practice

Do not hard-code a private LAN address into the repository. The web interface stores the selected server address locally in the browser.
