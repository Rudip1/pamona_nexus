<div align="center">

# 🧭 pomona_navigation

### Nav2 bringup + autonomous UV-C disinfection for the **Pomona** greenhouse robot

*Compose a full Nav2 stack from orthogonal axes — `controller:= localization:=` — then let the robot disinfect every bed on its own.*

[![ROS 2](https://img.shields.io/badge/ROS%202-Humble-22314E?logo=ros&logoColor=white)](https://docs.ros.org/en/humble/)
[![Nav2](https://img.shields.io/badge/Nav2-1.1.x-5B8DEF)](https://navigation.ros.org/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](../../LICENSE)

</div>

---

## What this package does

A launch-time YAML **composer** merges small, single-purpose fragments into one
Nav2 params file, so swapping a controller never means hand-editing a 400-line
monolith:

```
nav2_base.yaml                      ← controller-agnostic Nav2 skeleton
  ⊕ controllers/<controller>.yaml   ← FollowPath block   (mppi | dwb)
  ⊕ planners/NavFn.yaml             ← GridBased block     (NavFn)
  ⊕ localization/amcl.yaml          ← amcl block          (amcl only)
  ⊕ robots/pomona_uvc.yaml          ← footprint, frames, velocity limits
  ─────────────────────────────────────────────────────────────────────
  /tmp/nav2_<ctrl>_<planner>_<loc>.yaml   → passed to every Nav2 node
```

Merged by [`pomona_navigation/launch_utils/compose_params.py`](pomona_navigation/launch_utils/compose_params.py)
in **strict mode**: a robot-profile key that doesn't exist in the merged params
fails the launch with a *"did you mean…?"* hint instead of silently misconfiguring a node.

> Patterned after `cogni-nav-x0 / vf_robot_bringup`, pared to Pomona's needs:
> **MPPI + DWB** controllers, **NavFn** planner, **AMCL** localization.

---

## Launch files

| Launch | Role |
|---|---|
| **`bringup.launch.py`** | Entry point — composes params, starts Nav2 + (AMCL or SLAM) + RViz |
| **`localization.launch.py`** | `map_server` + `amcl` on the saved `pomona_slam` map (include) |
| **`slam.launch.py`** | Online SLAM for mapping — wraps `pomona_slam/slam.launch.py` (include) |
| **`rviz.launch.py`** | RViz2 with the navigation view (include / standalone) |
| **`navigation.launch.py`** | The Nav2 servers themselves (include) |
| **`autonomous_waypoint.launch.py`** | 🌿 **Autonomous bed-disinfection mission** (AMCL + Nav2 + mission node) |

---

## Quickstart

### 1 · Build a map (SLAM)

```bash
# T1  world + robot + teleop
ros2 launch pomona_gazebo strawberry_farm.launch.py
# T2  Nav2 + online SLAM, drive Nav2 goals or teleop to explore
ros2 launch pomona_navigation bringup.launch.py localization:=slam controller:=mppi
# T3  save the map (→ pomona_slam/maps/strawberry_farm.{pgm,yaml})
ros2 launch pomona_slam save_map.launch.py map_name:=strawberry_farm
```

### 2 · Navigate on the saved map (AMCL)

```bash
ros2 launch pomona_navigation bringup.launch.py localization:=amcl controller:=mppi
# RViz → "2D Pose Estimate" to seed AMCL, then "Nav2 Goal" to drive.
```

### 3 · 🌿 Autonomous disinfection mission (explore + map)

```bash
# T1  the farm — the UV-C lamps glow violet and project a translucent beam
ros2 launch pomona_gazebo strawberry_farm.launch.py
# T2  full autonomy on SLAM — sweeps every bed, BUILDS the map as it goes, returns home
ros2 launch pomona_navigation autonomous_waypoint.launch.py controller:=mppi
# T3  (optional) save the map the mission just built
ros2 launch pomona_slam save_map.launch.py map_name:=strawberry_farm
```

The mission runs on **SLAM** (`slam_toolbox`), so the robot starts at the map
origin and generates the occupancy grid while it disinfects — no prior map or
manual pose needed.

---

## The disinfection mission

The pinwheel farm has **6 beds per quadrant × 4 quadrants = 24 beds**. The UV-C
boom carries two downward panels at **±1.0 m**, so a single pass centred on the
furrow between a bed *pair* disinfects **both beds at once** → **3 passes per
quadrant**, **12 lanes** total.

```
        Q2 │ Q1            lane centres per quadrant: 2.5, 6.5, 10.5 m
      ─────┼─────          (the furrows between bed pairs 1.5/3.5, 5.5/7.5, 9.5/11.5)
        Q3 │ Q4
                           Mission:  spawn(0,0) → Q1 → Q2 → Q3 → Q4 → back to spawn
                           each quadrant swept serpentine, no empty back-tracking
```

Waypoints are **derived from the same constants as the world generator**
([`launch_utils/bed_waypoints.py`](pomona_navigation/launch_utils/bed_waypoints.py)) —
edit the farm, the lanes follow. The mission runs on SLAM (robot starts at the
map origin), waits for Nav2, then sends the 25-pose route as a `FollowWaypoints` goal.

```bash
# preview the waypoints without launching anything
python3 src/pomona_navigation/pomona_navigation/launch_utils/bed_waypoints.py
```

| `autonomous_waypoint.launch.py` arg | Default | Meaning |
|---|---|---|
| `controller` | `mppi` | `mppi` \| `dwb` |
| `start_delay` | `10.0` | Seconds to let SLAM + Nav2 settle before sending waypoints |
| `set_initial_pose` | `false` | SLAM starts at origin, so no seeding needed |
| `rviz` | `true` | Show RViz |

---

## `bringup.launch.py` arguments

```bash
ros2 launch pomona_navigation bringup.launch.py --show-args
```

| Argument | Choices | Default | Notes |
|---|---|---|---|
| `controller` | `mppi`, `dwb` | `mppi` | Local controller (`FollowPath` plugin) |
| `planner` | `NavFn` | `NavFn` | Global planner (`GridBased`) |
| `localization` | `amcl`, `slam`, `none` | `amcl` | `map→odom` source |
| `map` | abs path | `""` | Map `.yaml` (wins over `map_name`) |
| `map_name` | basename | `strawberry_farm` | Under `pomona_slam/maps/` |
| `use_sim_time` | `true`, `false` | `true` | `true` in Gazebo |
| `rviz` | `true`, `false` | `true` | Launch RViz |

---

## Controllers & planner

| `controller:=` | Plugin | Notes |
|---|---|---|
| `mppi` | `nav2_mppi_controller::MPPIController` | Primary — smooth, handles tight furrows; DiffDrive model |
| `dwb` | `dwb_core::DWBLocalPlanner` | Dynamic Window baseline |

| `planner:=` | Plugin |
|---|---|
| `NavFn` | `nav2_navfn_planner/NavfnPlanner` (A* on the 2D grid) |

Velocity limits use different key names per plugin (`mppi vx_max` vs `dwb max_vel_x`),
so they live in `robots/pomona_uvc.yaml` under `controller_overrides.<family>` and
are applied only for the selected controller.

---

## `cmd_vel` chain

```
controller_server → cmd_vel_nav → velocity_smoother → cmd_vel_smoothed
                  → collision_monitor → cmd_vel → Gazebo diff_drive / Scout base
```

`behavior_server` recoveries (spin/backup/wait) write **directly** to `/cmd_vel`,
bypassing the chain — by design.

---

## Greenhouse tuning notes

The strawberry furrows are only **~1.0 m wide**, which drives a few non-default choices
(in `nav2_base.yaml` / `robots/pomona_uvc.yaml`):

| Key | Value | Why |
|---|---|---|
| `inflation_radius` | `0.25` m | A larger radius walls off every 1.0 m furrow |
| `cost_scaling_factor` | `4.0` | Keep a clear low-cost ribbon down the furrow centre |
| `footprint` | Scout base `0.925×0.380` | Boom panels ride at ~1.06 m (above the 1.0 m costmap band) |
| costmap layers | `ObstacleLayer` | 2D LiDAR only — no VoxelLayer |
| `collision_monitor.time_before_collision` | `0.6` s | Bed walls sit close in a furrow |

---

## Layout

```
pomona_navigation/
├── launch/
│   ├── bringup.launch.py             # entry point (compose + nav + loc/slam + rviz)
│   ├── navigation.launch.py          # Nav2 servers (include)
│   ├── localization.launch.py        # map_server + amcl (include)
│   ├── slam.launch.py                # wraps pomona_slam online SLAM (include)
│   ├── rviz.launch.py                # RViz2
│   └── autonomous_waypoint.launch.py # bed-disinfection mission
├── config/
│   ├── nav2/
│   │   ├── nav2_base.yaml            # skeleton
│   │   ├── controllers/{mppi,dwb}.yaml
│   │   ├── planners/NavFn.yaml
│   │   └── localization/amcl.yaml
│   └── robots/pomona_uvc.yaml        # footprint, frames, velocity, per-controller overrides
├── behavior_trees/                   # nav-to-pose / nav-through-poses BT XML
├── nodes/bed_disinfection_mission.py # FollowWaypoints client for the mission
├── pomona_navigation/launch_utils/
│   ├── compose_params.py             # strict deep-merge composer
│   └── bed_waypoints.py              # mission geometry (matches the world generator)
└── rviz/navigation.rviz
```

---

<div align="center">
<sub>

Part of **[Pomona Nexus](../../README.md)** · localizes on maps from
**[pomona_slam](../pomona_slam/README.md)** · Author **Pravin Oli** · **Apache-2.0**

</sub>
</div>
