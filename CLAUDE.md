# CLAUDE.md — Pomona Nexus

Loaded automatically when Claude Code starts in this workspace. Read this
first; it captures the layout decisions and "why we did it this way" so a
fresh session doesn't need to re-derive them.

## What this workspace is

ROS 2 Humble workspace for **Pomona** — an AgileX Scout V2 mobile base
carrying a UFactory xArm6 arm with a DH Robotics AG95 gripper. Target use
case is greenhouse fruit picking (strawberry / grapevine / apple /
mushroom). The same workspace runs on the dev laptop (simulation) and
on the physical robot (hardware drivers).

The robot originally ran ROS 1 Melodic; we ported the geometry, meshes,
and hardware config into a clean ROS 2 Humble structure. The original
ROS 1 source is archived under `goldmines/` (read-only reference, see
`goldmines/README.md`).

## Author + license

- **Pravin Oli** &nbsp; `pravin.oli.08@gmail.com`, `olipravin18@gmail.com`
- License: **Apache-2.0** — see `LICENSE`, attribution in `NOTICE.md`
- Affiliation: IFROS (Erasmus Mundus, UdG + ELTE) &middot; EUROKNOWS CO., LTD.

Every file authored from scratch gets the Apache-2.0 header from
`docs/file_header.txt` (Python / C++ / XML variants). Files lifted from
upstream keep their original copyright and add an "Adapted from" line.

## Top-level layout

```
pomona_nexus/
├── src/                              colcon root
│   ├── pomona_description/           URDF/xacro + meshes (shared sim+real)
│   ├── pomona_gazebo/                Gazebo Classic 11 (sim only)
│   ├── pomona_bringup/               CAN/USB/Ethernet drivers (real only)
│   ├── pomona_msgs/                  custom messages (empty day-1)
│   ├── pomona_moveit_config/         MoveIt 2 (xArm6 + AG95)
│   ├── pomona_slam/                  SLAM Toolbox
│   └── pomona_navigation/            Nav2
├── goldmines/                        reference: ROS 1 source tar + robot dumps
│   ├── scout_backup_20260522/           udev, configs, IP/CAN/serial dumps
│   ├── scout_workspaces_20260522.tar.gz original ROS 1 workspace (gitignored, 2.4 GB)
│   └── .extracted/                      scratch extract dir (gitignored)
├── docs/                             non-ROS docs (file_header.txt, runbooks)
├── LICENSE, NOTICE.md, README.md
└── .gitignore
```

## Naming convention

- Packages: `pomona_<purpose>` — no `_robot_` infix (matches turtlebot4/husky style).
- `pomona_bringup` = **real hardware only** (CAN, USB, Ethernet drivers).
- `pomona_gazebo` = **sim only** (Gazebo Classic 11).
- `pomona_slam` / `pomona_navigation` / `pomona_moveit_config` work
  against either sim or real — toggle with `use_sim_time:=true/false`.
- No `pomona_moveit_bringup` package; launch files live inside
  `pomona_moveit_config/launch/`.

## Hardware (real robot)

| Component | Make / Model | Interface | Linux dev |
|---|---|---|---|
| Mobile base | AgileX Scout V2 | CAN 500 kbps | `can0` |
| Arm | UFactory xArm6 (6-DOF) | Ethernet | `192.168.1.219` |
| Gripper | DH Robotics AG95 | FTDI USB 115200 8N1 | `/dev/DH_hand` |
| RGB-D camera | Intel RealSense D435 | USB 3 | librealsense |
| 3D LiDAR | Robosense (rslidar) | Ethernet | UDP |
| IMU | Xsens MTi (DB4698SY) | USB | `/dev/xsens_imu` |

Geometry:
- Scout V2 base 0.925 × 0.380 × 0.210 m, wheelbase 0.498 m, track 0.583 m
- xArm6 mount on base: `xyz=(0.212, 0, 0.26)` (from real robot calibration)
- RealSense on EE: `xyz=(0,0,0.06) rpy=(0,-1.57,3.14)` from `link_eef`
- rslidar on base: `xyz=(0,0,0.138)`

## Software environment

- **Ubuntu 22.04** + **ROS 2 Humble** + **Gazebo Classic 11**
- Vendor drivers expected (not all installed yet — see `pomona_bringup/README.md`):
  - `scout_ros2` (AgileX) — apt or vcs
  - `xarm_ros2` (UFactory) — git
  - `dh_gripper_driver` (port from ROS 1 in goldmines)
  - `ros-humble-realsense2-camera` — apt
  - `rslidar_sdk` (Robosense) — git
  - `xsens_mti_driver` (Movella) — download

## Build + run

```bash
cd /home/pravin/pomona_nexus
colcon build --symlink-install
source install/setup.bash
```

Working out of the box (day-1):
```bash
# Standalone URDF viewer (no Gazebo, no robot)
ros2 launch pomona_description display.launch.py

# Pomona in Gazebo empty_world, driveable with rqt_robot_steering
ros2 launch pomona_gazebo empty_world_xacro.launch.py
# → drag the slider in rqt → Scout drives via /cmd_vel → diff_drive plugin → /odom
```

Sim worlds: `empty_world` is wired end-to-end. The four greenhouse worlds
(`strawberry`, `grapevine`, `apple_orchard`, `mushroom_greenhouse`) are
placeholders — folders + launchers exist, content TBD.

## Two pipelines (sim)

| Pipeline | Spawn from | Source-of-truth flow |
|---|---|---|
| **xacro** (recommended) | `/robot_description` topic | xacro → RSP → spawn_entity |
| **sdf** | `models/pomona/model.sdf` file | xacro → URDF → `gz sdf -p` → SDF |

Both `<env>_xacro.launch.py` and `<env>_sdf.launch.py` exist per world.
The SDF file is a placeholder until you run `xacro_to_urdf.sh` + `gz sdf -p`.

## Known stubs (planned, not implemented)

- `pomona_bringup/launch/{base,arm,gripper,lidar,camera,imu}.launch.py` —
  declare args only; vendor driver Nodes commented out as TODO.
- `pomona_moveit_config/launch/*` — minimal stubs. Recommended next step
  is to run MoveIt Setup Assistant against `pomona.xacro` and let it
  regenerate the package.
- `pomona_gazebo/models/pomona/model.sdf` — placeholder red box; regenerate
  from xacro when SDF pipeline is needed.
- `pomona_msgs` — empty; add messages and uncomment `rosidl_generate_interfaces`.
- 4 greenhouse worlds — empty `.world` files; need environment SDFs.

## Conventions for new code

- Apache-2.0 header from `docs/file_header.txt` on every new file.
- Maintainer block in `package.xml` lists both emails (`pravin.oli.08@gmail.com`
  and `olipravin18@gmail.com`).
- Files lifted from upstream keep their original copyright and add an
  `Adapted from <repo> (<license>)` line.
- Meshes copied from upstream: add a line to the local `ATTRIBUTION` file
  in the same directory.

## Git

```
59a8fcb  Initial workspace skeleton: rename, goldmines, README
17f08de  Add LICENSE (Apache-2.0), NOTICE (credits), file header template
a4f1e03  Scaffold 7 packages
```

Author config is set per-commit (see commit metadata); the global
`~/.gitconfig` is not changed.

## Next milestones

1. **Verify empty_world live** — actually run `empty_world_xacro.launch.py`,
   confirm gzclient opens, Pomona spawns, slider drives the base.
2. **MoveIt Setup Assistant** — regenerate `pomona_moveit_config/` properly.
3. **Wire in vendor drivers** — uncomment `base.launch.py` etc. as each one
   becomes available (`scout_ros2`, `xarm_ros2`, `realsense2_camera`, …).
4. **Build out greenhouse worlds** — strawberry first (highest-value crop).
5. **SLAM + Nav2 in sim** — record a bag, build a map, drive a goal.
