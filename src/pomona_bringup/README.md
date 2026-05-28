# pomona_bringup

Real-robot hardware bringup for **Pomona**. Wraps the vendor drivers
(scout_ros2, xarm_ros2, dh_gripper_driver, rslidar_sdk, realsense2_camera,
xsens_mti_driver) behind a single top-level launch.

Sim only? See `pomona_gazebo` instead.

## Hardware

| Component | Interface | Linux device | Vendor pkg (ROS 2 Humble) |
|---|---|---|---|
| Scout V2 base | CAN | `can0` @ 500 kbps | `scout_ros2` (AgileX) |
| xArm6 arm | Ethernet | `192.168.1.219` | `xarm_ros2` (UFactory) |
| AG95 gripper | FTDI USB | `/dev/DH_hand` 115200 8N1 | `dh_gripper_driver` (port from ROS1) |
| RealSense D435 | USB 3 | (libusb) | `realsense2_camera` |
| Robosense LiDAR | Ethernet | UDP MSOP/DIFOP | `rslidar_sdk` |
| Xsens MTi IMU | USB | `/dev/xsens_imu` | `xsens_mti_driver` (Movella) |

## One-time setup on the robot

```bash
# 1. Install udev rules (creates /dev/DH_hand, /dev/xsens_imu, RealSense perms)
ros2 run pomona_bringup install_udev.sh
# unplug/replug each device, then verify:
ls -l /dev/DH_hand /dev/xsens_imu

# 2. Bring up CAN bus
ros2 run pomona_bringup setup_can.sh           # default: can0 @ 500k
# or:  ros2 run pomona_bringup setup_can.sh can0 500000
```

## Run

```bash
# Full stack:
ros2 launch pomona_bringup pomona_bringup.launch.py

# Subset (turn things off):
ros2 launch pomona_bringup pomona_bringup.launch.py enable_arm:=false enable_gripper:=false

# With RViz:
ros2 launch pomona_bringup pomona_bringup.launch.py use_rviz:=true
```

Individual subsystems:
```bash
ros2 launch pomona_bringup base.launch.py
ros2 launch pomona_bringup arm.launch.py     robot_ip:=192.168.1.219
ros2 launch pomona_bringup gripper.launch.py port:=/dev/DH_hand
ros2 launch pomona_bringup lidar.launch.py
ros2 launch pomona_bringup camera.launch.py
ros2 launch pomona_bringup imu.launch.py
```

## Status

These launch files are **stubs** — the structure is in place but the actual
vendor driver Nodes are commented out with `TODO` markers. To activate:

1. `scout_ros2` — clone from AgileX, build, uncomment in `base.launch.py`.
2. `xarm_ros2` — clone from UFactory, build, uncomment in `arm.launch.py`.
3. `dh_gripper_driver` — port from `goldmines/.../dh_gripper_driver/` (small).
4. `realsense2_camera` — `sudo apt install ros-humble-realsense2-camera`.
5. `rslidar_sdk` — clone from Robosense, build, uncomment in `lidar.launch.py`.
6. `xsens_mti_driver` — download from movella.com.

Hardware contracts (udev / CAN / IP) are real and lifted from the original
robot — see `goldmines/scout_backup_20260522/` for the source dumps.
