# pomona_nexus

ROS 2 Humble workspace for **Pomona** — an AgileX Scout V2 mobile base with a
UFactory xArm6 arm and DH Robotics AG95 gripper, intended for greenhouse fruit
picking (strawberry / grape / apple / mushroom).

Targets **Ubuntu 22.04 + ROS 2 Humble + Gazebo Classic 11**. The same workspace
runs on the dev machine (simulation) and on the real robot (hardware drivers).

**Author** Pravin Oli &nbsp;·&nbsp; `pravin.oli.08@gmail.com` &nbsp;·&nbsp; `olipravin18@gmail.com`
**License** Apache-2.0 — see [`LICENSE`](LICENSE)
**Attribution** — see [`NOTICE.md`](NOTICE.md) for credits to AgileX, UFactory, DH Robotics, Intel RealSense, RoboSense, Xsens, and the ROS 2 / Gazebo / MoveIt / Nav2 communities.

## Layout

```
pomona_nexus/
├── src/                      ← ROS 2 packages (colcon root)
│   ├── pomona_description/      URDF / xacro / meshes        (shared sim+real)
│   ├── pomona_gazebo/           Gazebo Classic 11 launches    (sim only)
│   ├── pomona_bringup/          CAN/USB/Ethernet drivers      (real only)
│   ├── pomona_msgs/             custom messages
│   ├── pomona_moveit_config/    MoveIt2 for xArm6 + AG95
│   ├── pomona_slam/             SLAM Toolbox
│   └── pomona_navigation/       Nav2
├── goldmines/                ← reference material (see goldmines/README.md)
│   ├── scout_backup_20260522/      udev rules, configs, ip/can dumps from the robot
│   └── scout_workspaces_20260522.tar.gz   the full original ROS1 workspace (gitignored)
├── docs/                     ← hardware notes, IP/CAN maps, runbooks
└── README.md
```

## Build

```bash
cd /home/pravin/pomona_nexus
colcon build --symlink-install
source install/setup.bash
```

## Run

Simulation:
```bash
ros2 launch pomona_gazebo empty_world_pomona_uvc_xacro.launch.py
# Scout + mounting box + xArm6 + AG95 spawn; the base drives from the
# rqt_robot_steering slider, and the arm/gripper are controlled via
# gazebo_ros2_control (arm rises to a home fold and holds).
```
See [`docs/sim_runbook.md`](docs/sim_runbook.md) for the launch timeline,
per-subsystem verification, and fixes for known failures.

Real robot:
```bash
ros2 launch pomona_bringup pomona_bringup.launch.py
```

## Hardware

| Component        | Make / Model                  | Interface             |
|------------------|-------------------------------|-----------------------|
| Mobile base      | AgileX Scout V2 (4-wheel skid)| CAN bus `can0` @ 500k |
| Manipulator arm  | UFactory xArm6 (6-DOF)        | Ethernet `192.168.1.219` |
| End-effector     | DH Robotics AG95 gripper      | FTDI USB `/dev/DH_hand` 115200 8N1 |
| RGB-D camera     | Intel RealSense D435 (on EE)  | USB 3                 |
| 3D LiDAR         | Robosense (rslidar)           | Ethernet              |
| IMU              | Xsens MTi (DB4698SY)          | USB `/dev/xsens_imu`  |
