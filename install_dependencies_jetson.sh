#!/usr/bin/env bash
set -euo pipefail

echo "Installing DOFBOT waste-sorting runtime dependencies..."

sudo apt update
sudo apt install -y   python3-pip   python3-yaml   python3-opencv   python3-smbus   ros-melodic-cv-bridge   ros-melodic-sensor-msgs

python3 -m pip install --user   pandas   Pillow   websockets   tqdm

cat <<'EOF'

Jetson-specific notes:
- Keep the CUDA-enabled PyTorch build supplied for your JetPack image.
- Install Yahboom Arm_Lib using the vendor instructions for your DOFBOT image.
- Build the ROS package with Catkin after cloning the repository.
- Model weights are not downloaded by this script.

EOF
