# NOTICE

Pomona Nexus
Copyright 2026 Pravin Oli

This product includes software developed by Pravin Oli and contributors.
Licensed under the Apache License, Version 2.0. See `LICENSE` for the
full license text.

---

## Author

**Pravin Oli**
Email: `pravin.oli.08@gmail.com`, `olipravin18@gmail.com`

Erasmus Mundus Joint Masters in Intelligent Field Robotics Systems (IFROS)
— https://ifrosmaster.org/
- Universitat de Girona, Spain — https://www.udg.edu/en/
- Eötvös Loránd University, Hungary — https://www.elte.hu/

Industrial partner: **EUROKNOWS CO., LTD.** — https://www.euroknows.com/en/home/

---

## Third-party software acknowledgements

This workspace integrates, depends on, or borrows from the following
upstream projects. Each remains under its own license; consult the
respective project for full terms. The list below is for attribution
only and is not exhaustive.

### Robot platform

| Project | Vendor | Used for | Upstream |
|---|---|---|---|
| `scout_ros` / `scout_ros2` | AgileX Robotics | Scout V2 mobile base CAN driver, URDF reference, meshes | https://github.com/agilexrobotics/scout_ros2 |
| `ugv_sdk` | AgileX Robotics | UGV C++ SDK underlying the CAN driver | https://github.com/agilexrobotics/ugv_sdk |
| `xarm_ros2` | UFactory | xArm6 ROS 2 driver, URDF, MoveIt configs, meshes | https://github.com/xArm-Developer/xarm_ros2 |
| `dh_gripper_ros` | DH Robotics | AG95 gripper driver and URDF | https://github.com/DH-Robotics |

### Sensors

| Project | Vendor | Used for | Upstream |
|---|---|---|---|
| `realsense-ros` | Intel | RealSense D435 RGB-D camera driver | https://github.com/IntelRealSense/realsense-ros |
| `rslidar_sdk` | RoboSense | Robosense LiDAR driver | https://github.com/RoboSense-LiDAR/rslidar_sdk |
| `xsens_mti_driver` / `xsens_ros_mti_driver` | Movella (Xsens) | Xsens MTi IMU driver | https://www.movella.com/ |

### ROS 2 ecosystem

- **ROS 2 Humble Hawksbill** — Open Robotics — https://docs.ros.org/en/humble/
- **Gazebo Classic 11** — Open Robotics — https://classic.gazebosim.org/
- **gazebo_ros_pkgs** / **gazebo_ros2_control** — Open Robotics
- **Nav2** — https://github.com/ros-navigation/navigation2
- **MoveIt 2** — https://github.com/ros-planning/moveit2
- **SLAM Toolbox** — Steve Macenski — https://github.com/SteveMacenski/slam_toolbox
- **xacro**, **robot_state_publisher**, **joint_state_publisher**, **rviz2**,
  **pointcloud_to_laserscan**, **rqt_robot_steering** — ROS 2 community

### Predecessor / reference project

- **cogni-nav-x0** (`vf_robot_*` packages) — Apache-2.0, © Pravin Oli — used
  as a reference for the ROS 2 launch-graph layout and per-world Gazebo
  folder pattern. Not redistributed here.

### Predecessor ROS 1 codebase

The original ROS 1 Melodic workspace pulled from the physical robot is
archived under `goldmines/scout_workspaces_20260522.tar.gz` and includes
substantial third-party code (the `navigation`, `geometry`, `geometry2`,
`SLAM`, `m-explore`, `vision_visp`, `aruco_ros`, `tracking_pid`, and
`easy_handeye` ROS 1 packages, among others). These were used on the
original robot but are **not** carried into Pomona Nexus — their ROS 2
equivalents are installed from the `ros-humble-*` apt repositories.

---

## How attribution works in this workspace

- Files authored from scratch carry an Apache-2.0 header with the author
  line `Pravin Oli <pravin.oli.08@gmail.com, olipravin18@gmail.com>`.
- Files lifted or adapted from an upstream project keep the upstream
  copyright notice and add a line noting the adaptation, e.g.
  `# Adapted from agilexrobotics/scout_ros2 (BSD-3-Clause) by Pravin Oli`.
- Mesh files (`.dae`, `.stl`) lifted from upstream are accompanied by an
  `ATTRIBUTION` note in the same directory.

If you spot an attribution that should be added or corrected, open an
issue or email the author.
