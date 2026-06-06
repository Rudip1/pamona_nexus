# pomona_gazebo

Gazebo Classic 11 simulation package for Pomona. **Sim only** — real-robot
launches live in `pomona_bringup`. URDF and meshes come from
`pomona_description`.

## Worlds

| World            | Status        | Launch                                              |
|------------------|---------------|-----------------------------------------------------|
| `empty_world`    | ★ working     | `empty_world_xacro.launch.py` / `empty_world_sdf.launch.py` |
| `strawberry`     | placeholder   | `strawberry_xacro.launch.py` / `strawberry_sdf.launch.py` |
| `grapevine`      | placeholder   | `grapevine_xacro.launch.py` / `grapevine_sdf.launch.py`   |
| `apple_orchard`  | placeholder   | `apple_orchard_xacro.launch.py` / `apple_orchard_sdf.launch.py` |
| `mushroom_greenhouse` | placeholder | `mushroom_greenhouse_xacro.launch.py` / `mushroom_greenhouse_sdf.launch.py` |

The four greenhouse worlds boot a baseline (ground + sun) so the launch
graph can be exercised early. Drop your environment SDFs into
`models/<env>/` and update `worlds/<env>.world` to instantiate them.

## Pipelines

Two parallel ways to spawn Pomona — pick one per session:

### Xacro pipeline (recommended)
- `robot_state_publisher` processes `pomona.xacro` (use_sim:=true).
- `/robot_description` carries the full URDF *with* Gazebo plugins.
- `spawn_entity.py -topic robot_description` spawns into Gazebo.
- Edit xacro → relaunch → changes picked up immediately.

### SDF pipeline
- `spawn_entity.py -file models/pomona/model.sdf` spawns a pre-baked SDF.
- Regenerate with:
  ```bash
  bash $(ros2 pkg prefix pomona_description)/share/pomona_description/scripts/xacro_to_urdf.sh
  gz sdf -p urdf/urdf/pomona_sim.urdf > models/pomona/model.sdf
  ```
- `models/pomona/model.sdf` is a placeholder until you run the above.

## Day-1 verification

```bash
cd /home/pravin/pomona_nexus
colcon build --symlink-install
source install/setup.bash

ros2 launch pomona_gazebo empty_world_xacro.launch.py
# → gzserver+gzclient open, Pomona spawns at origin, rqt_robot_steering pops up.
# Slide forward/turn — base should drive on the empty plane.
```

## Topics in sim

| Topic | Type | Publisher |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | `rqt_robot_steering` → diff_drive plugin |
| `/odom` | `nav_msgs/Odometry` | diff_drive plugin |
| `/scan` | `sensor_msgs/LaserScan` | rslidar ray_sensor plugin |
| `/imu/data` | `sensor_msgs/Imu` | imu plugin |
| `/camera/color/image_raw` | `sensor_msgs/Image` | D435 RGB camera plugin |
| `/camera/depth/image_rect_raw` | `sensor_msgs/Image` | D435 depth camera plugin |
| `/camera/depth/points` | `sensor_msgs/PointCloud2` | D435 depth camera plugin |
| `/joint_states` | `sensor_msgs/JointState` | `joint_state_broadcaster` (ros2_control) |
| `/tf`, `/tf_static` | TF | robot_state_publisher + diff_drive plugin |

## Arm + gripper control (gazebo_ros2_control)

The xacro pipeline includes `ros2_control.xacro` (sim only) and the
`libgazebo_ros2_control.so` plugin, which runs a `controller_manager` inside
Gazebo. `empty_world_xacro.launch.py` spawns three controllers and then sends a
one-shot trajectory to raise the arm to its home fold.

| Controller | Type | Interface |
|---|---|---|
| `joint_state_broadcaster` | `joint_state_broadcaster/JointStateBroadcaster` | publishes `/joint_states` |
| `xarm6_traj_controller` | `joint_trajectory_controller/JointTrajectoryController` | `/xarm6_traj_controller/follow_joint_trajectory` (action) |
| `ag95_gripper_controller` | `position_controllers/GripperActionController` | `/ag95_gripper_controller/gripper_cmd` (action); AG95 fingers follow `finger_joint` via URDF `<mimic>` |

Controller params: `config/gazebo_ros2_control_sim.yaml`. Quick checks and the
full failure catalogue (diff-drive `num_wheel_pairs`, the rcl comment-parse
issue, arm droop) are in **`docs/sim_runbook.md`**.

> Note: `pomona_state_publisher.launch.py` strips XML comments from the URDF
> before publishing — required so `gazebo_ros2_control` can parse it. Do not
> revert that to a plain `Command([xacro …])` value.
