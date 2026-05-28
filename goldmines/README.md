# goldmines/

Reference material from the original ROS 1 Melodic robot. **Read-only**.
Pull from here when you need URDF numbers, meshes, hardware configs, or to
see how something was wired on the real robot.

## What's in here

### `scout_backup_20260522/`  (16 MB, tracked in git)
Snapshot of the robot at the time we pulled it. Useful for:

- **udev rules** — `udev_rules/dh_hand.rules`, `99-realsense-libusb.rules`
- **CAN / network state** — `can_setup.txt`, `ip_addr.txt`, `network_interfaces.txt`
- **Serial-by-id mappings** — `serial_by_id.txt` (Xsens IMU, DH gripper FTDI)
- **APT / pip / ROS package lists** — `apt_manual_packages.txt`, `pip_packages.txt`, `ros_packages_full.txt`
- **Original launch shortcuts** — `launch_nav.sh`, `start.sh`, `start_sensors.sh`
- **bashrc / .gitconfig** — for env-var hints
- **maps/** — saved maps from the robot
- **rviz_config/** — RViz dumps
- **RealSense calibration** — `.realsense-config.json`

### `scout_workspaces_20260522.tar.gz`  (2.4 GB, **gitignored**)
The full original ROS 1 workspace. Contains:

- `agilex_ws/src/car_base/scout_ros/{scout_base, scout_bringup, scout_description, scout_msgs}` — AgileX Scout V2 driver + URDF + meshes
- `agilex_ws/src/car_base/ugv_sdk` — UGV C++ SDK
- `agilex_ws/src/moveit_config/scout_xarm/{scout_xarm_description, scout_xarm_base, scout_xarm_moveit_config}` — combined Scout + xArm6 description
- `agilex_ws/src/moveit_config/scout_xarm/xarm_ros/*` — UFactory xArm full stack (xarm_description, xarm_controller, xarm_bringup, moveit configs, gazebo)
- `agilex_ws/src/moveit_config/dh_robotics_ag95_model` — DH AG95 URDF + meshes
- `agilex_ws/src/scout_xarm_grip_moveit_config` — combined MoveIt config (Scout + xArm6 + AG95)
- `agilex_ws/src/start/agx_xarm_bringup` — top-level real-robot bringup launch
- `agilex_ws/src/sensors/{camera/realsense, lidar/rslidar_sdk, lidar/velodyne, imu_ch110}`
- `agilex_ws/src/dh_gripper_driver`, `dh_gripper_msgs` — DH gripper driver
- `agilex_ws/src/xsens_ros_mti_driver`, `ethzasl_xsens_driver` — Xsens IMU drivers
- `agilex_ws/src/{SLAM, navigation, m-explore, aruco_ros, vision_visp}` — ROS 1 navigation/SLAM/perception
- `agilex_ws/src/{Emin_Zeljko, recycle, dataset_recorder, tracking_pid, easy_handeye}` — custom student code

## How to extract specific things

```bash
cd /home/pravin/pomona_nexus/goldmines

# Peek inside without extracting
tar -tzf scout_workspaces_20260522.tar.gz | grep -i mesh

# Extract one folder
tar -xzf scout_workspaces_20260522.tar.gz \
  -C .extracted \
  agilex_ws/src/car_base/scout_ros/scout_description/meshes

# Extract everything into .extracted/ (gitignored)
mkdir -p .extracted && tar -xzf scout_workspaces_20260522.tar.gz -C .extracted
```

`.extracted/` is git-ignored — feel free to extract and delete freely.

## How we use it

When building Pomona packages we **lift** from here:
- DAE / STL meshes → `src/pomona_description/meshes/`
- URDF dimensions / joint origins → `src/pomona_description/urdf/xacro/*.xacro`
- udev rules → `src/pomona_bringup/udev/`
- Launch logic → translated ROS 1 XML → ROS 2 Python in `src/pomona_bringup/launch/`

We **do not** copy whole packages over. Most ROS 1 deps (navigation, SLAM,
geometry, vision_visp) are replaced by their `ros-humble-*` apt equivalents.
